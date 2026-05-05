#!/usr/bin/env python3
"""
Launch BotBrain inside Gazebo Harmonic on Ubuntu 22.04 + ROS 2 Humble.

Pipeline:
  1. gz sim                    starts the sim with our world
  2. xacro                     renders the selected robot (go2/b2/...) URDF
  3. ros_gz_sim create         spawns the URDF model
  4. ros_gz_bridge             bridges /clock + (optional) /sim/cmd_vel
  5. kinematic_locomotion_node integrates cmd_vel → odom + teleports model
  6. unitree_sdk_shim_node     re-publishes everything onto Unitree topics

The shim makes the real *_pkg/scripts/*_read.py + *_write.py work
without modification. Wire `bot_bringup` with `use_sim:=true sim_backend:=gazebo`
to launch this alongside the rest of the BotBrain stack.

Prereqs (Ubuntu 22.04):
  sudo apt install ros-humble-ros-gz gz-harmonic
"""
import os

import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    OpaqueFunction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
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
    world_path  = LaunchConfiguration('world').perform(context) or os.path.join(sim_pkg, 'worlds', 'empty.sdf')
    headless    = LaunchConfiguration('headless').perform(context).lower() == 'true'

    robot_pkg = get_package_share_directory(f'{robot_model}_pkg')
    xacro_path = os.path.join(robot_pkg, 'xacro', 'robot.xacro')

    # Render URDF from XACRO at launch time.
    urdf_path = os.path.join('/tmp', f'{robot_model}_botbrain_sim.urdf')
    os.system(f'ros2 run xacro xacro {xacro_path} prefix:= -o {urdf_path}')

    gz_args = f'-r {world_path}'
    if headless:
        gz_args = f'-r -s --headless-rendering {world_path}'

    actions = []

    # 1. Gazebo
    actions.append(IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': gz_args}.items(),
    ))

    # 2. Spawn the robot URDF in Gazebo.
    actions.append(Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'botbrain_robot',
            '-file', urdf_path,
            '-x', '0', '-y', '0', '-z', '0.45',
        ],
        output='screen',
    ))

    # 3. Bridge /clock so use_sim_time works.
    actions.append(Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen',
    ))

    # 4. Kinematic locomotion (turns cmd_vel → pose + odom + joint_states + imu).
    actions.append(Node(
        package='bot_sim_pkg',
        executable='kinematic_locomotion_node.py',
        name='kinematic_locomotion',
        namespace=robot_name,
        parameters=[{
            'cmd_vel_topic': '/sim/cmd_vel',
            'world_name': 'botbrain_world',
            'model_name': 'botbrain_robot',
            'joint_prefix': (robot_name + '/') if robot_name else '',
            'publish_rate_hz': 50.0,
            'teleport': True,
        }],
        output='screen',
    ))

    # 5. Unitree SDK shim — re-publishes sim state onto /lf/* and /api/sport/*.
    actions.append(Node(
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
    ))

    return actions


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('robot_model', default_value=''),
        DeclareLaunchArgument('robot_name', default_value=''),
        DeclareLaunchArgument('world', default_value=''),
        DeclareLaunchArgument('headless', default_value='false'),
        OpaqueFunction(function=_setup),
    ])
