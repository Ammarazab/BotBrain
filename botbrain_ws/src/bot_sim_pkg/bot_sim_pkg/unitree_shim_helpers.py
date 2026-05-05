"""Shared helpers between the shim and the Gazebo locomotion node."""
import math


# Canonical Unitree motor index ordering (Go2 / B2 / Go2-W).
MOTOR_NAME_BY_INDEX = [
    'FR_hip_joint',   'FR_thigh_joint', 'FR_calf_joint',     # 0,1,2
    'FL_hip_joint',   'FL_thigh_joint', 'FL_calf_joint',     # 3,4,5
    'RR_hip_joint',   'RR_thigh_joint', 'RR_calf_joint',     # 6,7,8
    'RL_hip_joint',   'RL_thigh_joint', 'RL_calf_joint',     # 9,10,11
]


def yaw_to_quaternion(yaw: float):
    """Return (x, y, z, w) for a rotation about Z."""
    half = yaw * 0.5
    return (0.0, 0.0, math.sin(half), math.cos(half))
