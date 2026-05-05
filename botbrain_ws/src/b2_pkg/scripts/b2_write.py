#!/usr/bin/env python3
"""
Hardware write/command node for the Unitree B2 quadruped.

Mirrors go2_pkg/scripts/go2_write.py but adapts the kinematic ranges
that differ on the B2 platform (taller standing height, longer legs,
larger pose envelope).

Reference docs:
  - https://support.unitree.com/home/en/B2_developer
  - https://github.com/unitreerobotics/unitree_ros2
"""
import rclpy
from rclpy.lifecycle import LifecycleNode, TransitionCallbackReturn
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from bot_custom_interfaces.srv import Mode, Pose, BodyHeight, ContinuousGait, Euler, FootRaiseHeight, SwitchGait, SwitchJoystick, SpeedLevel, CurrentMode, LightControl, ObstacleAvoidance
from bot_custom_interfaces.msg import RobotStatus
from unitree_api.msg import Request, Response
from geometry_msgs.msg import Twist
from unitree_go.msg import SportModeState
from std_srvs.srv import SetBool
import numpy as np
import json
import time

# B2-specific kinematic envelopes. The B2 has a much taller standing pose
# than the Go2 and a wider safe pose range.
# Body height delta is measured around the nominal stand height.
B2_BODY_HEIGHT_MIN = -0.20
B2_BODY_HEIGHT_MAX = 0.15
B2_FOOT_RAISE_MIN = 0.0
B2_FOOT_RAISE_MAX = 0.20
B2_EULER_ROLL_LIMIT = 0.75
B2_EULER_PITCH_LIMIT = 0.75
B2_EULER_YAW_LIMIT = 0.6


class RobotWriteNode(LifecycleNode):

    def __init__(self):
        super().__init__('lifecycle_robot_write_node')

        self.emergency_flag = True
        self.light_state = False
        self.obstacle_avoidance_state = False
        self.op_mode = None
        self.gait_type = None
        self.sport_response = None
        self.robot_state_response = None

        self.callback_group = None
        self.publisher_ = None
        self.robot_state_publisher_ = None
        self.vui_publisher_ = None
        self.obstacle_avoidance_publisher_ = None
        self.robot_status_publisher_ = None
        self.robot_status_timer_ = None
        self.cmd_vel_subscription = None
        self.sports_mode_subscription = None
        self.sport_response_subscription = None
        self.robot_state_response_subscription = None
        self.vui_subscription = None
        self.set_mode_srv = None
        self.set_pose_srv = None
        self.set_body_height_srv = None
        self.set_continuous_gait_srv = None
        self.set_euler_srv = None
        self.set_foot_raise_height_srv = None
        self.set_switch_gait_srv = None
        self.set_switch_joystick_srv = None
        self.set_speed_level_service_ = None
        self.get_current_mode_srv = None
        self.set_emergency_stop_srv = None
        self.set_light_srv = None
        self.set_obstacle_avoidance_srv = None

        self.get_logger().info("B2 lifecycle write node created, in 'unconfigured' state.")

    def on_configure(self, state: rclpy.lifecycle.State) -> TransitionCallbackReturn:
        self.get_logger().info("on_configure() is called.")

        self.callback_group = ReentrantCallbackGroup()

        self.publisher_ = self.create_publisher(Request, '/api/sport/request', 1)
        self.robot_state_publisher_ = self.create_publisher(Request, '/api/robot_state/request', 1)
        self.vui_publisher_ = self.create_publisher(Request, '/api/vui/request', 1)
        self.obstacle_avoidance_publisher_ = self.create_publisher(Request, '/api/obstacles_avoid/request', 1)
        self.robot_status_publisher_ = self.create_publisher(RobotStatus, 'robot_status', 1)

        self.robot_status_timer_ = self.create_timer(0.5, self.robot_status_callback, callback_group=self.callback_group)
        self.robot_status_timer_.cancel()

        self.cmd_vel_subscription = self.create_subscription(
            Twist, 'cmd_vel_out', self.cmd_vel_subscription_callback, 1, callback_group=self.callback_group)
        self.sports_mode_subscription = self.create_subscription(
            SportModeState, '/lf/sportmodestate', self.sport_state_subscription_callback, 1, callback_group=self.callback_group)
        self.sport_response_subscription = self.create_subscription(
            Response, '/api/sport/response', self.sport_response_callback, 10, callback_group=self.callback_group)
        self.robot_state_response_subscription = self.create_subscription(
            Response, '/api/robot_state/response', self.robot_state_response_callback, 10, callback_group=self.callback_group)
        self.vui_subscription = self.create_subscription(
            Response, '/api/vui/response', self.vui_callback, 10, callback_group=self.callback_group)

        self.set_mode_srv = self.create_service(Mode, 'mode', self.handle_mode, callback_group=self.callback_group)
        self.set_pose_srv = self.create_service(Pose, 'pose', self.handle_pose, callback_group=self.callback_group)
        self.set_body_height_srv = self.create_service(BodyHeight, 'body_height', self.handle_body_height, callback_group=self.callback_group)
        self.set_continuous_gait_srv = self.create_service(ContinuousGait, 'continuous_gait', self.handle_continuous_gait, callback_group=self.callback_group)
        self.set_euler_srv = self.create_service(Euler, 'euler', self.handle_euler, callback_group=self.callback_group)
        self.set_foot_raise_height_srv = self.create_service(FootRaiseHeight, 'foot_raise_height', self.handle_foot_raise_height, callback_group=self.callback_group)
        self.set_switch_gait_srv = self.create_service(SwitchGait, 'switch_gait', self.handle_switch_gait, callback_group=self.callback_group)
        self.set_switch_joystick_srv = self.create_service(SwitchJoystick, 'switch_joystick', self.handle_switch_joystick, callback_group=self.callback_group)
        self.set_speed_level_service_ = self.create_service(SpeedLevel, 'speed_level', self.handle_speed_level, callback_group=self.callback_group)
        self.get_current_mode_srv = self.create_service(CurrentMode, 'current_mode', self.get_current_mode, callback_group=self.callback_group)
        self.set_emergency_stop_srv = self.create_service(SetBool, 'emergency_stop', self.set_emergency_stop, callback_group=self.callback_group)
        self.set_light_srv = self.create_service(LightControl, 'light_control', self.set_light, callback_group=self.callback_group)
        self.set_obstacle_avoidance_srv = self.create_service(ObstacleAvoidance, 'obstacle_avoidance', self.set_obstacle_avoidance, callback_group=self.callback_group)

        self.get_logger().info("Node configured successfully.")
        return TransitionCallbackReturn.SUCCESS

    def on_activate(self, state: rclpy.lifecycle.State) -> TransitionCallbackReturn:
        self.get_logger().info("on_activate() is called.")

        super().on_activate(state)

        self.robot_status_timer_.reset()

        self.get_logger().info("Sending stand_down command during activation...")

        class MockResponse:
            def __init__(self):
                self.success = False
                self.message = ""

        req = Request()
        req.header.identity.api_id = 1005  # StandDown
        response = MockResponse()

        self.send_sport_request(req, response)

        if not response.success:
            self.get_logger().error("Failed to execute stand_down during activation")
            self.robot_status_timer_.cancel()
            super().on_deactivate(state)
            return TransitionCallbackReturn.FAILURE

        self.get_logger().info("Stand_down command successful")

        time.sleep(2.0)

        self.get_logger().info("Disabling MCF mode...")
        mcf_req = Request()
        mcf_req.header.identity.id = 0
        mcf_req.header.identity.api_id = 1001
        mcf_req.parameter = '{"name":"mcf","switch":0}'
        mcf_response = MockResponse()

        self.send_robot_state_request(mcf_req, mcf_response)

        if not mcf_response.success:
            self.get_logger().error("Failed to disable MCF mode during activation")
            self.robot_status_timer_.cancel()
            super().on_deactivate(state)
            return TransitionCallbackReturn.FAILURE

        self.get_logger().info("MCF mode disabled successfully")

        self.get_logger().info("Enabling sport_mode service...")
        sport_mode_req = Request()
        sport_mode_req.header.identity.id = 0
        sport_mode_req.header.identity.api_id = 1001
        sport_mode_req.parameter = '{"name":"sport_mode","switch":1}'
        sport_mode_response = MockResponse()

        self.send_robot_state_request(sport_mode_req, sport_mode_response)

        if not sport_mode_response.success:
            self.get_logger().error("Failed to enable sport_mode service during activation")
            self.robot_status_timer_.cancel()
            super().on_deactivate(state)
            return TransitionCallbackReturn.FAILURE

        self.get_logger().info("sport_mode service enabled successfully")
        self.get_logger().info("Node activated. Services and subscriptions are now responsive.")
        return TransitionCallbackReturn.SUCCESS

    def on_deactivate(self, state: rclpy.lifecycle.State) -> TransitionCallbackReturn:
        self.get_logger().info("on_deactivate() is called.")
        self.robot_status_timer_.cancel()
        super().on_deactivate(state)
        self.get_logger().info("Node deactivated.")
        return TransitionCallbackReturn.SUCCESS

    def on_cleanup(self, state: rclpy.lifecycle.State) -> TransitionCallbackReturn:
        self.get_logger().info("on_cleanup() is called.")

        self.destroy_publisher(self.publisher_)
        self.destroy_publisher(self.robot_state_publisher_)
        self.destroy_publisher(self.vui_publisher_)
        self.destroy_publisher(self.obstacle_avoidance_publisher_)
        self.destroy_publisher(self.robot_status_publisher_)
        self.destroy_timer(self.robot_status_timer_)
        self.destroy_subscription(self.cmd_vel_subscription)
        self.destroy_subscription(self.sports_mode_subscription)
        self.destroy_subscription(self.sport_response_subscription)
        self.destroy_subscription(self.robot_state_response_subscription)
        self.destroy_subscription(self.vui_subscription)
        self.destroy_service(self.set_mode_srv)
        self.destroy_service(self.set_pose_srv)
        self.destroy_service(self.set_body_height_srv)
        self.destroy_service(self.set_continuous_gait_srv)
        self.destroy_service(self.set_euler_srv)
        self.destroy_service(self.set_foot_raise_height_srv)
        self.destroy_service(self.set_switch_gait_srv)
        self.destroy_service(self.set_switch_joystick_srv)
        self.destroy_service(self.set_speed_level_service_)
        self.destroy_service(self.get_current_mode_srv)
        self.destroy_service(self.set_emergency_stop_srv)
        self.destroy_service(self.set_light_srv)
        self.destroy_service(self.set_obstacle_avoidance_srv)

        self.get_logger().info("Node resources cleaned up.")
        return TransitionCallbackReturn.SUCCESS

    def on_shutdown(self, state: rclpy.lifecycle.State) -> TransitionCallbackReturn:
        self.get_logger().info("on_shutdown() is called.")
        self.on_cleanup(state)
        return TransitionCallbackReturn.SUCCESS

    def sport_state_subscription_callback(self, msg):
        self.op_mode = msg.mode
        self.gait_type = msg.gait_type

    def sport_response_callback(self, msg):
        self.sport_response = msg

    def robot_state_response_callback(self, msg):
        self.robot_state_response = msg

    def cmd_vel_subscription_callback(self, msg):
        if self.emergency_flag:
            req_cmd_vel = Request()
            req_pose = Request()
            req_height = Request()

            req_cmd_vel.header.identity.api_id = 1008
            req_pose.header.identity.api_id = 1007
            req_height.header.identity.api_id = 1013

            lx = msg.linear.x
            ly = msg.linear.y
            az = msg.angular.z
            ay = msg.angular.y

            if self.op_mode == 2:
                js_pose = {"x": np.interp(ly, [-1, 1], [B2_EULER_ROLL_LIMIT, -B2_EULER_ROLL_LIMIT]),
                           "y": np.interp(ay, [-1, 1], [-B2_EULER_PITCH_LIMIT, B2_EULER_PITCH_LIMIT]),
                           "z": np.interp(az, [-1, 1], [-B2_EULER_YAW_LIMIT, B2_EULER_YAW_LIMIT])}
                js_height = {"data": np.interp(lx, [-1, 1], [B2_BODY_HEIGHT_MIN, B2_BODY_HEIGHT_MAX]) + 0.05}

                req_pose.parameter = json.dumps(js_pose)
                req_height.parameter = json.dumps(js_height)
                self.get_logger().info(req_height.parameter)
                self.publisher_.publish(req_pose)
            else:
                if lx or ly or az:
                    js_cmd_vel = {"x": lx,
                                  "y": ly,
                                  "z": az}
                    req_cmd_vel.parameter = json.dumps(js_cmd_vel)
                    self.publisher_.publish(req_cmd_vel)

    def handle_mode(self, request, response):
        mode = request.mode
        req = Request()

        if mode == 'damp':
            response.message = 'Change the mode to Damp'
            req.header.identity.api_id = 1001  # Damp
        elif mode == 'balance_stand':
            response.message = 'Change the mode to BalanceStand'
            req.header.identity.api_id = 1002  # BalanceStand
        elif mode == 'stand_up':
            response.message = 'Change the mode to StandUp'
            req.header.identity.api_id = 1004  # StandUp
        elif mode == 'stand_down':
            response.message = 'Change the mode to StandDown'
            req.header.identity.api_id = 1005  # StandDown
        elif mode == 'sit':
            response.message = 'Change the mode to Sit'
            req.header.identity.api_id = 1009  # Sit
        elif mode == 'hello':
            response.message = 'Change the mode to Hello. Say hello to your robot!'
            req.header.identity.api_id = 1016  # Hello
        elif mode == 'stretch':
            response.message = 'Change the mode to Stretch'
            req.header.identity.api_id = 1017  # Stretch
        elif mode == 'dance1':
            response.message = "Change the mode to Dance 1. Let's dance!"
            req.header.identity.api_id = 1022  # Dance1
        elif mode == 'dance2':
            response.message = "Change the mode to Dance 2. Let's dance!"
            req.header.identity.api_id = 1023  # Dance2
        else:
            response.success = False
            response.message = 'Invalid mode'
            return response

        return self.send_sport_request(req, response)

    def handle_pose(self, request, response):
        req = Request()
        data = {"data": request.flag}
        req.parameter = json.dumps(data)
        req.header.identity.api_id = 1028
        return self.send_sport_request(req, response)

    def handle_body_height(self, request, response):
        if request.height < B2_BODY_HEIGHT_MIN or request.height > B2_BODY_HEIGHT_MAX:
            response.success = False
            response.message = (
                f"Height value is out of range "
                f"[{B2_BODY_HEIGHT_MIN} ~ {B2_BODY_HEIGHT_MAX}]"
            )
            return response

        js = {"data": request.height}

        req = Request()
        req.parameter = json.dumps(js)
        req.header.identity.api_id = 1013  # BodyHeight

        return self.send_sport_request(req, response)

    def handle_continuous_gait(self, request, response):
        js = {"data": request.flag}

        req = Request()
        req.parameter = json.dumps(js)
        req.header.identity.api_id = 1019  # ContinuousGait

        return self.send_sport_request(req, response)

    def handle_euler(self, request, response):
        if request.roll < -B2_EULER_ROLL_LIMIT or request.roll > B2_EULER_ROLL_LIMIT:
            response.success = False
            response.message = f"Roll value is out of range [-{B2_EULER_ROLL_LIMIT} ~ {B2_EULER_ROLL_LIMIT}]"
            return response

        if request.pitch < -B2_EULER_PITCH_LIMIT or request.pitch > B2_EULER_PITCH_LIMIT:
            response.success = False
            response.message = f"Pitch value is out of range [-{B2_EULER_PITCH_LIMIT} ~ {B2_EULER_PITCH_LIMIT}]"
            return response

        if request.yaw < -B2_EULER_YAW_LIMIT or request.yaw > B2_EULER_YAW_LIMIT:
            response.success = False
            response.message = f"Yaw value is out of range [-{B2_EULER_YAW_LIMIT} ~ {B2_EULER_YAW_LIMIT}]"
            return response

        js = {
            "x": request.roll,
            "y": request.pitch,
            "z": request.yaw
        }

        req = Request()
        req.parameter = json.dumps(js)
        req.header.identity.api_id = 1007  # Euler

        return self.send_sport_request(req, response)

    def handle_foot_raise_height(self, request, response):
        if request.height < B2_FOOT_RAISE_MIN or request.height > B2_FOOT_RAISE_MAX:
            response.success = False
            response.message = (
                f"Height value is out of range "
                f"[{B2_FOOT_RAISE_MIN} ~ {B2_FOOT_RAISE_MAX}]"
            )
            return response

        js = {"data": request.height}

        req = Request()
        req.parameter = json.dumps(js)
        req.header.identity.api_id = 1014  # FootRaiseHeight

        return self.send_sport_request(req, response)

    def handle_switch_gait(self, request, response):
        if request.d < 0 or request.d > 4:
            response.success = False
            response.message = "Invalid gait type [0 - 4]"
            return response

        js = {"data": request.d}

        req = Request()
        req.parameter = json.dumps(js)
        req.header.identity.api_id = 1011  # SwitchGait

        return self.send_sport_request(req, response)

    def handle_switch_joystick(self, request, response):
        js = {"data": request.flag}

        req = Request()
        req.parameter = json.dumps(js)
        req.header.identity.api_id = 1027  # SwitchJoystick

        return self.send_sport_request(req, response)

    def handle_speed_level(self, request, response):
        if request.level < -1 or request.level > 1:
            response.success = False
            response.message = "Speed level is out of range [-1 ~ 1]"
            return response

        js = {"data": request.level}

        req = Request()
        req.parameter = json.dumps(js)
        req.header.identity.api_id = 1015  # SpeedLevel

        return self.send_sport_request(req, response)

    def get_current_mode(self, request, response):
        if self.op_mode == 1:
            response.mode = "balance_stand"
        elif self.op_mode == 2:
            response.mode = ""
        elif self.op_mode == 3:
            response.mode = ""
        elif self.op_mode == 4:
            response.mode = ""
        elif self.op_mode == 5:
            response.mode = "stand_down"
        elif self.op_mode == 6:
            response.mode = "stand_up"
        elif self.op_mode == 7:
            response.mode = "damp"
        elif self.op_mode == 8:
            response.mode = ""
        elif self.op_mode == 9:
            response.mode = ""
        elif self.op_mode == 10:
            response.mode = "sit"
        else:
            response.mode = "Unknown"
        return response

    def set_emergency_stop(self, request, response):
        if self.emergency_flag is True:
            req_msg = Request()
            self.emergency_flag = False

            req_msg.header.identity.api_id = 1008

            js_cmd_vel = {"x": 0,
                          "y": 0,
                          "z": 0}

            req_msg.parameter = json.dumps(js_cmd_vel)
            self.publisher_.publish(req_msg)

            time.sleep(0.1)

            req_msg.header.identity.api_id = 1007

            js_pose = {"x": 0,
                       "y": 0,
                       "z": 0}

            req_msg.parameter = json.dumps(js_pose)
            self.publisher_.publish(req_msg)

            time.sleep(1)

            req_msg.header.identity.api_id = 1003
            self.publisher_.publish(req_msg)

            time.sleep(1)

            req_msg.header.identity.api_id = 1005
            self.publisher_.publish(req_msg)

            time.sleep(4)

            req_msg.header.identity.api_id = 1001
            self.publisher_.publish(req_msg)
            response.message = "Emergency Stop Set"
        else:
            self.emergency_flag = True
            response.message = "Emergency Stop Reset"

        response.success = True
        return response

    def send_sport_request(self, request, response):
        if self.emergency_flag and self.op_mode is not None:
            self.sport_response = None

            self.publisher_.publish(request)

            timeout = time.time()
            limit = 2.0

            while True:
                if (time.time() - timeout) > limit:
                    response.success = False
                    break

                if self.sport_response is not None:
                    if (self.sport_response.header.identity.api_id == request.header.identity.api_id and
                        self.sport_response.header.status.code == 0):
                        response.success = True
                        break
                    else:
                        response.success = False
                        break
        else:
            response.success = False

        return response

    def send_robot_state_request(self, request, response):
        self.robot_state_response = None

        self.robot_state_publisher_.publish(request)

        timeout = time.time()
        limit = 0.5

        while True:
            if (time.time() - timeout) > limit:
                response.success = False
                break

            if self.robot_state_response is not None:
                if (self.robot_state_response.header.identity.api_id == request.header.identity.api_id and
                    self.robot_state_response.header.status.code == 0):
                    response.success = True
                    break
                else:
                    response.success = False
                    break

            time.sleep(0.01)

        return response

    def set_light(self, request, response):
        if self.op_mode is not None:
            req = Request()
            req.header.identity.api_id = 1005
            js = {"brightness": request.brightness}
            if request.control is False:
                js = {"brightness": 0}
                req.parameter = json.dumps(js)
                self.vui_publisher_.publish(req)
                response.success = True
                return response
            if request.brightness < 1 or request.brightness > 10:
                response.success = False
                response.message = "Brightness out of range. Pick a value between 1 and 10."
            else:
                req.parameter = json.dumps(js)
                response.success = True
                self.vui_publisher_.publish(req)
        else:
            response.success = False
        return response

    def vui_callback(self, msg):
        if msg.header.identity.api_id == 1006:
            data = json.loads(msg.data)
            if data["brightness"] > 0:
                self.light_state = True
            else:
                self.light_state = False

    def set_obstacle_avoidance(self, request, response):
        if self.op_mode is not None:
            req = Request()
            req.header.identity.api_id = 1001
            js = {"enable": request.control}
            req.parameter = json.dumps(js)
            self.obstacle_avoidance_publisher_.publish(req)
            self.obstacle_avoidance_state = request.control
            response.success = True
        else:
            response.success = False
        return response

    def robot_status_callback(self):
        msg = RobotStatus()
        msg.emergency_stop = not self.emergency_flag
        msg.light_state = self.light_state
        msg.obstacle_avoidance_state = self.obstacle_avoidance_state
        self.robot_status_publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = RobotWriteNode()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
