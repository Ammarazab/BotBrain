#!/usr/bin/env python3
"""
Kinematic locomotion fallback for Gazebo Harmonic.

Quadruped controllers in Gazebo are notoriously twitchy and Unitree
doesn't ship a Gazebo plugin for the Go2/B2 sport-mode controller.
For BotBrain's stack — twist_mux, Nav2, RTABMap, the dashboard — what
matters is that *some* base frame moves in response to a cmd_vel and
publishes odom + joint_states + imu.

This node implements that: it integrates cmd_vel to a pose, teleports
the simulated robot via gz set-pose, and republishes:

  - /joint_states  (rest pose, 12 zeros — meshes stay still)
  - /imu/data      (flat orientation, gyro = angular cmd, accel = gravity)
  - /odom          (integrated x/y/yaw)

For locomotion-fidelity work use Isaac Sim instead (see isaac_sim_runner.py),
which loads Unitree's official RL policy and gives you real foot contacts.
"""
import math
import subprocess

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TransformStamped, Quaternion
from sensor_msgs.msg import JointState, Imu
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster

from bot_sim_pkg.unitree_shim_helpers import (
    MOTOR_NAME_BY_INDEX,
    yaw_to_quaternion,
)


class KinematicLocomotion(Node):
    def __init__(self):
        super().__init__('kinematic_locomotion')

        self.declare_parameter('cmd_vel_topic', '/sim/cmd_vel')
        self.declare_parameter('world_name', 'botbrain_world')
        self.declare_parameter('model_name', 'botbrain_robot')
        self.declare_parameter('joint_prefix', '')
        self.declare_parameter('publish_rate_hz', 50.0)
        self.declare_parameter('teleport', True)  # call `gz` to move the model
        self.declare_parameter('initial_z', 0.40)

        self.world_name = self.get_parameter('world_name').value
        self.model_name = self.get_parameter('model_name').value
        self.joint_prefix = self.get_parameter('joint_prefix').value
        self.teleport = bool(self.get_parameter('teleport').value)
        rate_hz = float(self.get_parameter('publish_rate_hz').value)

        self._x = 0.0
        self._y = 0.0
        self._z = float(self.get_parameter('initial_z').value)
        self._yaw = 0.0
        self._vx = 0.0
        self._vy = 0.0
        self._wz = 0.0

        self.create_subscription(
            Twist, self.get_parameter('cmd_vel_topic').value,
            self._on_cmd_vel, 10,
        )
        self._joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        self._imu_pub   = self.create_publisher(Imu, '/imu/data', 10)
        self._odom_pub  = self.create_publisher(Odometry, '/odom', 10)
        self._tf = TransformBroadcaster(self)

        period = 1.0 / max(rate_hz, 1.0)
        self._dt = period
        self.create_timer(period, self._tick)

        self.get_logger().info(
            f"KinematicLocomotion teleport={self.teleport} world={self.world_name} "
            f"model={self.model_name} rate={rate_hz}Hz"
        )

    def _on_cmd_vel(self, msg: Twist):
        self._vx = float(msg.linear.x)
        self._vy = float(msg.linear.y)
        self._wz = float(msg.angular.z)

    def _tick(self):
        # Integrate body-frame velocity into world pose.
        cy, sy = math.cos(self._yaw), math.sin(self._yaw)
        self._x += (self._vx * cy - self._vy * sy) * self._dt
        self._y += (self._vx * sy + self._vy * cy) * self._dt
        self._yaw += self._wz * self._dt
        self._yaw = (self._yaw + math.pi) % (2 * math.pi) - math.pi

        if self.teleport:
            self._teleport_in_gz()

        now = self.get_clock().now().to_msg()
        q = yaw_to_quaternion(self._yaw)

        # /joint_states (zero pose; 12 leg joints)
        js = JointState()
        js.header.stamp = now
        js.name = [f'{self.joint_prefix}{n}' for n in MOTOR_NAME_BY_INDEX[:12]]
        js.position = [0.0] * 12
        self._joint_pub.publish(js)

        # /imu/data
        imu = Imu()
        imu.header.stamp = now
        imu.header.frame_id = f'{self.joint_prefix}imu_link'
        imu.orientation = Quaternion(x=q[0], y=q[1], z=q[2], w=q[3])
        imu.angular_velocity.z = self._wz
        imu.linear_acceleration.z = 9.81
        self._imu_pub.publish(imu)

        # /odom + odom→base_link TF
        odom = Odometry()
        odom.header.stamp = now
        odom.header.frame_id = f'{self.joint_prefix}odom'
        odom.child_frame_id = f'{self.joint_prefix}base_link'
        odom.pose.pose.position.x = self._x
        odom.pose.pose.position.y = self._y
        odom.pose.pose.position.z = self._z
        odom.pose.pose.orientation = Quaternion(x=q[0], y=q[1], z=q[2], w=q[3])
        odom.twist.twist.linear.x = self._vx
        odom.twist.twist.linear.y = self._vy
        odom.twist.twist.angular.z = self._wz
        self._odom_pub.publish(odom)

        tf = TransformStamped()
        tf.header.stamp = now
        tf.header.frame_id = f'{self.joint_prefix}odom'
        tf.child_frame_id = f'{self.joint_prefix}base_link'
        tf.transform.translation.x = self._x
        tf.transform.translation.y = self._y
        tf.transform.translation.z = self._z
        tf.transform.rotation = odom.pose.pose.orientation
        self._tf.sendTransform(tf)

    def _teleport_in_gz(self):
        # Best-effort: ignore failures so the node keeps publishing odom
        # even when running standalone (no Gazebo) for unit testing.
        cmd = [
            'gz', 'service', '-s', f'/world/{self.world_name}/set_pose',
            '--reqtype', 'gz.msgs.Pose',
            '--reptype', 'gz.msgs.Boolean',
            '--timeout', '50',
            '--req',
            f'name: "{self.model_name}", '
            f'position: {{x: {self._x}, y: {self._y}, z: {self._z}}}, '
            f'orientation: {{x: 0, y: 0, z: {math.sin(self._yaw/2)}, '
            f'w: {math.cos(self._yaw/2)}}}',
        ]
        try:
            subprocess.run(cmd, check=False, capture_output=True, timeout=0.1)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass


def main(args=None):
    rclpy.init(args=args)
    node = KinematicLocomotion()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
