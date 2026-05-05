#!/usr/bin/env python3
"""
Unitree SDK shim for BotBrain simulation.

Bridges a generic ROS 2 simulator (Gazebo Harmonic, Isaac Sim, MuJoCo)
to the Unitree-SDK-2 DDS topic shape that the real `*_pkg` nodes
(go2_pkg, b2_pkg, g1_pkg, ...) expect:

  Sim publishes              ──►  Shim re-publishes as
  /joint_states                   /lf/lowstate.motor_state[]
  /imu/data                       /lf/lowstate.imu_state, /lf/sportmodestate.imu_state
  /odom                           /lf/sportmodestate.position[], .velocity[]
                                  /lf/lowstate.power_v / .bms_state.soc (faked)

  Real *_pkg publishes       ──►  Shim consumes & forwards to sim
  /api/sport/request              /sim/cmd_vel       (when api_id == 1008)
                                  internal mode FSM   (StandUp/StandDown/Damp/...)
                                  /api/sport/response (always success)
  /api/robot_state/request        /api/robot_state/response  (always success)
  /api/vui/request                /api/vui/response          (echo brightness)
  /api/obstacles_avoid/request    (no-op ack)

The shim is intentionally permissive: every sport/robot_state request is
acknowledged with status code 0 so the existing lifecycle write nodes
finish their `on_activate` initialisation sequence in simulation. The
`mode` field of SportModeState is updated to mirror the FSM transitions
the real robot would go through.
"""
import math
from collections import deque

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy

from sensor_msgs.msg import JointState, Imu
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist

from unitree_go.msg import LowState, SportModeState
from unitree_api.msg import Request, Response


# Canonical Unitree motor index ordering (Go2 / B2 / Go2-W).
# Matches what go2_pkg/b2_pkg's *_read.py already assume.
MOTOR_NAME_BY_INDEX = [
    'FR_hip_joint',   'FR_thigh_joint', 'FR_calf_joint',     # 0,1,2
    'FL_hip_joint',   'FL_thigh_joint', 'FL_calf_joint',     # 3,4,5
    'RR_hip_joint',   'RR_thigh_joint', 'RR_calf_joint',     # 6,7,8
    'RL_hip_joint',   'RL_thigh_joint', 'RL_calf_joint',     # 9,10,11
]
NUM_MOTORS = 20  # LowState reserves 20 motor slots even on 12-DoF quadrupeds.

# Sport-mode FSM — mirrors the integers go2_write.get_current_mode reads back.
MODE_BALANCE_STAND = 1
MODE_POSE          = 2
MODE_STAND_DOWN    = 5
MODE_STAND_UP      = 6
MODE_DAMP          = 7
MODE_SIT           = 10

# api_id → next mode mapping for sport requests we care about.
API_TO_MODE = {
    1001: MODE_DAMP,           # Damp
    1002: MODE_BALANCE_STAND,  # BalanceStand
    1004: MODE_STAND_UP,       # StandUp
    1005: MODE_STAND_DOWN,     # StandDown
    1009: MODE_SIT,            # Sit
}


class UnitreeSdkShim(Node):
    def __init__(self):
        super().__init__('unitree_sdk_shim')

        self.declare_parameter('joint_prefix', '')
        self.declare_parameter('publish_rate_hz', 50.0)
        self.declare_parameter('battery_voltage', 28.0)
        self.declare_parameter('battery_soc', 95)
        self.declare_parameter('cmd_vel_topic', '/sim/cmd_vel')
        self.declare_parameter('joint_states_topic', '/joint_states')
        self.declare_parameter('imu_topic', '/imu/data')
        self.declare_parameter('odom_topic', '/odom')

        self.joint_prefix = self.get_parameter('joint_prefix').value
        rate_hz = float(self.get_parameter('publish_rate_hz').value)
        self.battery_voltage = float(self.get_parameter('battery_voltage').value)
        self.battery_soc = int(self.get_parameter('battery_soc').value)
        cmd_vel_topic = self.get_parameter('cmd_vel_topic').value
        joint_states_topic = self.get_parameter('joint_states_topic').value
        imu_topic = self.get_parameter('imu_topic').value
        odom_topic = self.get_parameter('odom_topic').value

        # Mutable state captured from the simulator.
        self._joint_q = np.zeros(NUM_MOTORS, dtype=np.float32)
        self._joint_dq = np.zeros(NUM_MOTORS, dtype=np.float32)
        self._imu_quat = np.array([0.0, 0.0, 0.0, 1.0], dtype=np.float32)
        self._imu_gyro = np.zeros(3, dtype=np.float32)
        self._imu_accel = np.array([0.0, 0.0, 9.81], dtype=np.float32)
        self._position = np.zeros(3, dtype=np.float32)
        self._velocity = np.zeros(3, dtype=np.float32)
        self._yaw_speed = 0.0
        self._body_height = 0.0
        self._mode = MODE_STAND_DOWN  # Robots boot lying down.
        self._gait_type = 0

        # Lookup of joint name → motor slot.
        self._name_to_idx = {}
        for idx, base in enumerate(MOTOR_NAME_BY_INDEX):
            self._name_to_idx[f'{self.joint_prefix}{base}'] = idx
            self._name_to_idx[base] = idx  # accept both prefixed and unprefixed

        sensor_qos = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
        )

        # Inputs from the simulator.
        self.create_subscription(JointState, joint_states_topic,
                                 self._on_joint_states, sensor_qos)
        self.create_subscription(Imu, imu_topic,
                                 self._on_imu, sensor_qos)
        self.create_subscription(Odometry, odom_topic,
                                 self._on_odom, 10)

        # Inputs from the BotBrain stack (real *_write.py nodes).
        self.create_subscription(Request, '/api/sport/request',
                                 self._on_sport_request, 10)
        self.create_subscription(Request, '/api/robot_state/request',
                                 self._on_robot_state_request, 10)
        self.create_subscription(Request, '/api/vui/request',
                                 self._on_vui_request, 10)
        self.create_subscription(Request, '/api/obstacles_avoid/request',
                                 self._on_obs_request, 10)

        # Outputs to the BotBrain stack.
        self._sport_state_pub = self.create_publisher(SportModeState, '/lf/sportmodestate', 10)
        self._low_state_pub   = self.create_publisher(LowState,       '/lf/lowstate',       10)
        self._sport_resp_pub  = self.create_publisher(Response, '/api/sport/response', 10)
        self._rstate_resp_pub = self.create_publisher(Response, '/api/robot_state/response', 10)
        self._vui_resp_pub    = self.create_publisher(Response, '/api/vui/response', 10)
        self._obs_resp_pub    = self.create_publisher(Response, '/api/obstacles_avoid/response', 10)

        # Output to the simulator (locomotion command).
        self._cmd_vel_pub = self.create_publisher(Twist, cmd_vel_topic, 10)

        # Recent api ids for debugging.
        self._recent_api_ids = deque(maxlen=10)

        period = 1.0 / max(rate_hz, 1.0)
        self.create_timer(period, self._publish_sport_state)
        self.create_timer(period * 0.5, self._publish_low_state)  # 2x sport rate

        self.get_logger().info(
            f"UnitreeSdkShim ready. joint_prefix='{self.joint_prefix}', "
            f"sport_rate={rate_hz} Hz, cmd_vel→{cmd_vel_topic}"
        )

    # ------------------------------------------------------------------
    # Sim → Unitree adapters
    # ------------------------------------------------------------------
    def _on_joint_states(self, msg: JointState):
        for name, q, dq in self._iter_joint_positions(msg):
            idx = self._name_to_idx.get(name)
            if idx is not None and idx < NUM_MOTORS:
                self._joint_q[idx] = q
                self._joint_dq[idx] = dq

    @staticmethod
    def _iter_joint_positions(msg: JointState):
        n = len(msg.name)
        for i in range(n):
            q = msg.position[i] if i < len(msg.position) else 0.0
            dq = msg.velocity[i] if i < len(msg.velocity) else 0.0
            yield msg.name[i], float(q), float(dq)

    def _on_imu(self, msg: Imu):
        self._imu_quat = np.array([
            msg.orientation.x, msg.orientation.y,
            msg.orientation.z, msg.orientation.w,
        ], dtype=np.float32)
        self._imu_gyro = np.array([
            msg.angular_velocity.x,
            msg.angular_velocity.y,
            msg.angular_velocity.z,
        ], dtype=np.float32)
        self._imu_accel = np.array([
            msg.linear_acceleration.x,
            msg.linear_acceleration.y,
            msg.linear_acceleration.z,
        ], dtype=np.float32)

    def _on_odom(self, msg: Odometry):
        p = msg.pose.pose.position
        v = msg.twist.twist.linear
        self._position = np.array([p.x, p.y, p.z], dtype=np.float32)
        self._velocity = np.array([v.x, v.y, v.z], dtype=np.float32)
        self._yaw_speed = float(msg.twist.twist.angular.z)
        self._body_height = float(p.z)

    # ------------------------------------------------------------------
    # BotBrain stack → sim adapters
    # ------------------------------------------------------------------
    def _on_sport_request(self, msg: Request):
        api_id = msg.header.identity.api_id
        self._recent_api_ids.append(api_id)

        if api_id == 1008:
            # Move (cmd_vel). Parameter is JSON {"x":..,"y":..,"z":..}.
            self._forward_cmd_vel(msg.parameter)
        elif api_id in API_TO_MODE:
            self._mode = API_TO_MODE[api_id]
            self.get_logger().info(f"Sport mode → {self._mode} (api_id={api_id})")
        elif api_id == 1011:
            try:
                import json
                self._gait_type = int(json.loads(msg.parameter or '{}').get('data', 0))
            except Exception:
                pass

        # Always ack so lifecycle on_activate succeeds.
        self._ack(self._sport_resp_pub, msg)

    def _on_robot_state_request(self, msg: Request):
        # E.g. enable sport_mode service / disable MCF.
        self._ack(self._rstate_resp_pub, msg)

    def _on_vui_request(self, msg: Request):
        # Light brightness ack. We don't track here; *_write owns that state.
        self._ack(self._vui_resp_pub, msg, data=msg.parameter)

    def _on_obs_request(self, msg: Request):
        self._ack(self._obs_resp_pub, msg)

    @staticmethod
    def _ack(publisher, request: Request, data: str = ''):
        resp = Response()
        resp.header.identity.id = request.header.identity.id
        resp.header.identity.api_id = request.header.identity.api_id
        resp.header.status.code = 0
        resp.data = data
        publisher.publish(resp)

    def _forward_cmd_vel(self, parameter: str):
        try:
            import json
            data = json.loads(parameter or '{}')
        except ValueError:
            return
        twist = Twist()
        twist.linear.x = float(data.get('x', 0.0))
        twist.linear.y = float(data.get('y', 0.0))
        twist.angular.z = float(data.get('z', 0.0))
        self._cmd_vel_pub.publish(twist)

    # ------------------------------------------------------------------
    # Periodic outputs: SportModeState + LowState
    # ------------------------------------------------------------------
    def _publish_sport_state(self):
        msg = SportModeState()
        msg.mode = int(self._mode)
        msg.gait_type = int(self._gait_type)
        msg.body_height = float(self._body_height)
        for i in range(3):
            msg.position[i] = float(self._position[i])
            msg.velocity[i] = float(self._velocity[i])
        msg.yaw_speed = float(self._yaw_speed)
        self._fill_imu(msg.imu_state)
        self._sport_state_pub.publish(msg)

    def _publish_low_state(self):
        msg = LowState()
        self._fill_imu(msg.imu_state)
        for i in range(NUM_MOTORS):
            msg.motor_state[i].q = float(self._joint_q[i])
            msg.motor_state[i].dq = float(self._joint_dq[i])
        msg.power_v = float(self.battery_voltage)
        msg.power_a = 0.0
        msg.bms_state.soc = self.battery_soc
        msg.bms_state.current = 0
        self._low_state_pub.publish(msg)

    def _fill_imu(self, imu_state):
        imu_state.quaternion[0] = float(self._imu_quat[0])
        imu_state.quaternion[1] = float(self._imu_quat[1])
        imu_state.quaternion[2] = float(self._imu_quat[2])
        imu_state.quaternion[3] = float(self._imu_quat[3])
        imu_state.gyroscope[0] = float(self._imu_gyro[0])
        imu_state.gyroscope[1] = float(self._imu_gyro[1])
        imu_state.gyroscope[2] = float(self._imu_gyro[2])
        imu_state.accelerometer[0] = float(self._imu_accel[0])
        imu_state.accelerometer[1] = float(self._imu_accel[1])
        imu_state.accelerometer[2] = float(self._imu_accel[2])
        imu_state.rpy[0] = self._yaw_speed * 0.0  # left at 0; downstream nodes recompute
        imu_state.temperature = 35


def main(args=None):
    rclpy.init(args=args)
    node = UnitreeSdkShim()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
