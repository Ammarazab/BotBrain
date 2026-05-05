#!/usr/bin/env python3
"""
Launch the Isaac Sim 5.0+ runner as a child process and start the
Unitree SDK shim alongside it.

Usage:
  ros2 launch bot_sim_pkg isaac_sim.launch.py robot_model:=go2

Requires `isaacsim` Python package on PATH (Isaac Sim 5.0+ pip install).
"""
import os
import shutil

import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _read_robot_config(workspace_dir: str) -> dict:
    cfg_path = os.path.join(workspace_dir, 'robot_config.yaml')
    if not os.path.exists(cfg_path):
        return {'robot_name': '', 'robot_model': 'go2'}
    with open(cfg_path, 'r') as f:
        return yaml.safe_load(f)['robot_configuration']


def _setup(context, *args, **kwargs):
    sim_pkg = get_package_share_directory('bot_sim_pkg')
    launch_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(launch_dir)))))

    config = _read_robot_config(workspace_dir)
    robot_model = LaunchConfiguration('robot_model').perform(context) or config['robot_model'] or 'go2'
    robot_name  = LaunchConfiguration('robot_name').perform(context) or config['robot_name'] or ''
    headless    = LaunchConfiguration('headless').perform(context)
    isaac_python = LaunchConfiguration('isaac_python').perform(context) or shutil.which('python3') or 'python3'

    runner_path = os.path.join(sim_pkg, 'lib', 'bot_sim_pkg', 'isaac_sim_runner.py')
    if not os.path.exists(runner_path):
        # Fall back to the source tree so launch still works pre-install.
        runner_path = os.path.join(
            workspace_dir, 'src', 'bot_sim_pkg', 'scripts', 'isaac_sim_runner.py'
        )

    isaac_proc = ExecuteProcess(
        cmd=[
            isaac_python, runner_path,
            '--robot', robot_model,
            '--headless', headless,
        ],
        output='screen',
        # Make the Isaac Sim ROS bridge talk on the same DDS as everyone else.
        additional_env={
            'RMW_IMPLEMENTATION': os.environ.get('RMW_IMPLEMENTATION', 'rmw_cyclonedds_cpp'),
        },
    )

    shim = Node(
        package='bot_sim_pkg',
        executable='unitree_sdk_shim_node.py',
        name='unitree_sdk_shim',
        namespace=robot_name,
        parameters=[{
            'joint_prefix': (robot_name + '/') if robot_name else '',
            'publish_rate_hz': 50.0,
            'cmd_vel_topic': '/sim/cmd_vel',
            'joint_states_topic': '/joint_states',
            'imu_topic': '/imu/data',
            'odom_topic': '/odom',
        }],
        output='screen',
    )

    return [isaac_proc, shim]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('robot_model', default_value=''),
        DeclareLaunchArgument('robot_name', default_value=''),
        DeclareLaunchArgument('headless', default_value='false'),
        DeclareLaunchArgument(
            'isaac_python', default_value='',
            description='Override Python interpreter Isaac Sim should use.'),
        OpaqueFunction(function=_setup),
    ])
