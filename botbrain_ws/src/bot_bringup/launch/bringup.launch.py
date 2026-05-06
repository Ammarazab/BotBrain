import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
)
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_xml.launch_description_sources import XMLLaunchDescriptionSource
import yaml


def _build_actions(context, *args, **kwargs):
    launch_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(launch_dir)))))
    config_file = os.path.join(workspace_dir, 'robot_config.yaml')
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)['robot_configuration']

    # Allow CLI overrides (`robot_model:=b2`) and fall back to a sensible
    # default so an empty robot_config.yaml doesn't blow up with `_pkg`.
    cli_robot_model = LaunchConfiguration('robot_model').perform(context).strip()
    cli_robot_name  = LaunchConfiguration('robot_name').perform(context).strip()
    robot_name  = cli_robot_name  or config.get('robot_name', '')  or ''
    robot_model = cli_robot_model or config.get('robot_model', '') or 'go2'
    print(f"Robot name: {robot_name!r}, robot model: {robot_model!r}")

    use_sim_str = LaunchConfiguration('use_sim').perform(context).lower()
    use_sim = use_sim_str in ('1', 'true', 'yes')
    sim_backend = LaunchConfiguration('sim_backend').perform(context)

    # ------------------------------------------------------------------
    # Common: description, twist_mux, joystick, rosbridge.
    # ------------------------------------------------------------------
    description_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('bot_description'),
                'launch',
                'description.launch.py'
            )
        )
    )

    twist_mux_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('bot_bringup'),
                'launch',
                'twist_mux.launch.py'
            )
        )
    )

    joystick_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('joystick_bot'),
                'launch',
                'js.launch.py'
            )
        ),
        launch_arguments={'namespace': robot_name}.items(),
    )

    rosbridge_launch = IncludeLaunchDescription(
        XMLLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('rosbridge_server'),
                'launch',
                'rosbridge_websocket_launch.xml'
            )
        ),
        launch_arguments={
            'cbor_compression': 'true',
            'namespace': robot_name
        }.items(),
    )

    actions = [description_launch, twist_mux_launch, joystick_launch, rosbridge_launch]

    # ------------------------------------------------------------------
    # Robot stack: real hardware *or* simulator (mutually exclusive).
    # ------------------------------------------------------------------
    if use_sim:
        # Sim brings up its own backend (Isaac Sim or Gazebo) plus the
        # unitree_sdk_shim that re-publishes onto /lf/* and /api/sport/*.
        # We still launch the real *_write.py / *_read.py because they
        # subscribe to the same Unitree topics — the shim makes them
        # work transparently.
        sim_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    get_package_share_directory('bot_sim_pkg'),
                    'launch',
                    'sim_bringup.launch.py'
                )
            ),
            launch_arguments={
                'sim_backend': sim_backend,
                'robot_model': robot_model,
                'robot_name': robot_name,
                'headless': LaunchConfiguration('headless'),
            }.items(),
        )
        actions.append(sim_launch)

    robot_interface_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory(robot_model + '_pkg'),
                'launch',
                'robot_interface.launch.py'
            )
        )
    )
    actions.append(robot_interface_launch)

    return actions


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time', default_value='False',
            description='Use simulation time'),
        DeclareLaunchArgument(
            'use_sim', default_value='false',
            description='Run in simulation instead of on real hardware.'),
        DeclareLaunchArgument(
            'robot_model', default_value='',
            description="Override robot model from robot_config.yaml (go2, b2, g1, ...)."),
        DeclareLaunchArgument(
            'robot_name', default_value='',
            description='Override robot namespace from robot_config.yaml.'),
        DeclareLaunchArgument(
            'sim_backend', default_value='gazebo',
            description="When use_sim:=true, choose 'gazebo' or 'isaac'."),
        DeclareLaunchArgument(
            'headless', default_value='false',
            description='Run the simulator without a GUI.'),
        OpaqueFunction(function=_build_actions),
    ])
