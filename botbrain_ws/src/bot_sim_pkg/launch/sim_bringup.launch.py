#!/usr/bin/env python3
"""
Top-level sim launcher. Picks Isaac Sim or Gazebo based on `sim_backend`.

  ros2 launch bot_sim_pkg sim_bringup.launch.py sim_backend:=isaac
  ros2 launch bot_sim_pkg sim_bringup.launch.py sim_backend:=gazebo
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def _setup(context, *args, **kwargs):
    backend = LaunchConfiguration('sim_backend').perform(context).lower()
    sim_pkg = get_package_share_directory('bot_sim_pkg')

    if backend == 'isaac':
        target = os.path.join(sim_pkg, 'launch', 'isaac_sim.launch.py')
    elif backend == 'gazebo':
        target = os.path.join(sim_pkg, 'launch', 'gazebo.launch.py')
    else:
        raise SystemExit(f"sim_backend must be 'isaac' or 'gazebo', got {backend!r}")

    return [IncludeLaunchDescription(
        PythonLaunchDescriptionSource(target),
        launch_arguments={
            'robot_model': LaunchConfiguration('robot_model'),
            'robot_name':  LaunchConfiguration('robot_name'),
            'headless':    LaunchConfiguration('headless'),
        }.items(),
    )]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('sim_backend', default_value='gazebo',
                              description='isaac or gazebo'),
        DeclareLaunchArgument('robot_model', default_value=''),
        DeclareLaunchArgument('robot_name', default_value=''),
        DeclareLaunchArgument('headless', default_value='false'),
        OpaqueFunction(function=_setup),
    ])
