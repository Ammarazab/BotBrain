<p align="center">
  <a href="https://botbot.bot" target="_blank">
    <img src="https://cdn.prod.website-files.com/672ed723fbdc1589fa127239/672ed83e9ab7d55f18a3c43f_BotBot%20Purple%20Logo%20(2)-p-500.png" alt="BotBot" width="180">
  </a>
</p>

# b2_pkg

**Unitree B2 Quadruped Robot Hardware Interface Package**

The `b2_pkg` package provides the ROS 2 hardware abstraction layer for the
Unitree **B2** industrial quadruped. It mirrors `go2_pkg` and uses the same
Unitree SDK 2 ROS 2 channels (sportmodestate, lowstate, sport API, robot
state API), but ships with B2-specific kinematic envelopes, footprint, and
URDF dimensions.

References:

- Unitree B2 developer portal: https://support.unitree.com/home/en/B2_developer
- Unitree ROS 2 SDK & description: https://github.com/unitreerobotics/unitree_ros2

## Package Purpose

This package interfaces with the Unitree B2 robot through ROS 2 topics, enabling:

- **Hardware Communication**: Real-time bidirectional data exchange with the B2
- **Sensor Integration**: Publishing odometry, IMU, joint states, and battery data
- **Motion Control**: Receiving and executing velocity commands from twist_mux
- **Video Streaming**: Publishing the B2 onboard camera feed
- **Robot Services**: Mode switching, gait control, pose adjustment, and safety features
- **Controller Integration**: Translating joystick inputs to robot-specific commands

## Nodes

All nodes in this package are **lifecycle nodes**, providing managed state
transitions for robust startup, shutdown, and error recovery.

### Lifecycle Management

#### Common Lifecycle States

| State | Description |
|-------|-------------|
| **Unconfigured** | Initial state after node creation, no resources allocated |
| **Configured** | Resources created (publishers, subscribers, services), ready to activate |
| **Active** | Node fully operational, processing data and executing functions |
| **Deactivated** | Node paused, resources maintained but processing stopped |
| **Finalized** | All resources cleaned up, node ready for termination |

#### Standard Lifecycle Transitions

| Transition | Description |
|------------|-------------|
| `configure` | Allocate resources (create publishers, subscribers, services) |
| `activate` | Start processing (begin publishing, accepting commands) |
| `deactivate` | Pause processing (stop publishing but maintain resources) |
| `cleanup` | Destroy resources (close connections, free memory) |
| `shutdown` | Emergency cleanup and immediate termination |

#### Managing Lifecycle States

```bash
# Check current state
ros2 lifecycle get /{namespace}/robot_read_node

# Transition through states
ros2 lifecycle set /{namespace}/robot_read_node configure
ros2 lifecycle set /{namespace}/robot_read_node activate
```

`bot_state_machine` automatically manages lifecycle transitions during
system startup and shutdown.

---

### robot_read_node

Lifecycle node that reads sensor data from the B2 robot and publishes to ROS 2 topics.

**Executable**: `b2_read.py`

**Description**: Subscribes to Unitree ROS 2 topics, processes robot state data,
and publishes standard ROS 2 sensor messages. Provides odometry, IMU, joint
states, battery status, and LiDAR data. Motor index ordering is identical to
the Go2 (FR=0..2, FL=3..5, RR=6..8, RL=9..11).

#### Publishers

| Topic | Message Type | Description |
|-------|--------------|-------------|
| `/{namespace}/odom` | `nav_msgs/Odometry` | Robot odometry (position, velocity) in base_link frame |
| `/{namespace}/imu/data` | `sensor_msgs/Imu` | IMU data (orientation, angular velocity, linear acceleration) |
| `/{namespace}/joint_states` | `sensor_msgs/JointState` | Joint positions for all 12 leg joints |
| `/{namespace}/battery` | `sensor_msgs/BatteryState` | Battery voltage, current, percentage |
| `/{namespace}/imu_temp` | `std_msgs/Float32` | IMU temperature in Celsius |
| `/{namespace}/pointcloud` | `sensor_msgs/PointCloud2` | LiDAR point cloud data (if equipped) |

#### Subscribers

| Topic | Message Type | Description |
|-------|--------------|-------------|
| `/lf/sportmodestate` | `unitree_go/SportModeState` | Unitree sport mode state |
| `/lf/lowstate` | `unitree_go/LowState` | Unitree low-level state |
| `/utlidar/robot_pose` | `geometry_msgs/PoseStamped` | Robot pose from Unitree LiDAR |
| `/utlidar/cloud` | `sensor_msgs/PointCloud2` | Point cloud from Unitree LiDAR |

#### Parameters

| Parameter Name | Type | Default Value | Description |
|----------------|------|---------------|-------------|
| `prefix` | string | `""` | Topic prefix (namespace) for published data |

---

### lifecycle_robot_write_node

Lifecycle node that receives ROS 2 commands and sends them to the B2 robot.

**Executable**: `b2_write.py`

**Description**: Subscribes to velocity commands from twist_mux and sends them
to the B2 robot via Unitree ROS 2 API topics. Provides services for mode
switching, gait control, pose adjustment, and safety features. The B2 has a
larger pose envelope than Go2; this node enforces the B2-specific limits:

| Service param | B2 limit |
|---------------|----------|
| `body_height` (delta) | -0.20 m to +0.15 m |
| `foot_raise_height` | 0.0 m to 0.20 m |
| `euler.roll` | ±0.75 rad |
| `euler.pitch` | ±0.75 rad |
| `euler.yaw` | ±0.6 rad |

#### Publishers

| Topic | Message Type | Description |
|-------|--------------|-------------|
| `/{namespace}/robot_status` | `bot_custom_interfaces/msg/RobotStatus` | Robot operational status |
| `/api/sport/request` | `unitree_api/msg/Request` | Unitree sport mode API requests |
| `/api/robot_state/request` | `unitree_api/msg/Request` | Unitree robot state API requests |
| `/api/vui/request` | `unitree_api/msg/Request` | Unitree voice UI API requests |
| `/api/obstacles_avoid/request` | `unitree_api/msg/Request` | Unitree obstacle avoidance API requests |

#### Services

| Service Name | Service Type | Description |
|--------------|--------------|-------------|
| `/{namespace}/mode` | `bot_custom_interfaces/srv/Mode` | Switch robot operational mode |
| `/{namespace}/switch_gait` | `bot_custom_interfaces/srv/SwitchGait` | Change gait pattern |
| `/{namespace}/body_height` | `bot_custom_interfaces/srv/BodyHeight` | Adjust body height |
| `/{namespace}/foot_raise_height` | `bot_custom_interfaces/srv/FootRaiseHeight` | Set foot lift height |
| `/{namespace}/speed_level` | `bot_custom_interfaces/srv/SpeedLevel` | Set speed level |
| `/{namespace}/pose` | `bot_custom_interfaces/srv/Pose` | Set body pose |
| `/{namespace}/euler` | `bot_custom_interfaces/srv/Euler` | Set orientation using Euler angles |
| `/{namespace}/continuous_gait` | `bot_custom_interfaces/srv/ContinuousGait` | Enable continuous gait transitions |
| `/{namespace}/switch_joystick` | `bot_custom_interfaces/srv/SwitchJoystick` | Switch joystick control modes |
| `/{namespace}/current_mode` | `bot_custom_interfaces/srv/CurrentMode` | Query current mode |
| `/{namespace}/emergency_stop` | `std_srvs/srv/SetBool` | Trigger emergency stop |
| `/{namespace}/light_control` | `bot_custom_interfaces/srv/LightControl` | Control LED lights |
| `/{namespace}/obstacle_avoidance` | `bot_custom_interfaces/srv/ObstacleAvoidance` | Toggle onboard obstacle avoidance |

**Note**: On `activate`, this node automatically performs the same
initialization sequence as the Go2: stand_down → disable MCF → enable
sport_mode service.

---

### controller_commands_node

Lifecycle node that translates game-controller input to B2 commands.

**Executable**: `b2_controller_commands.py`

Button mapping is identical to `go2_pkg` for cross-platform muscle memory.

---

### robot_video_stream

Lifecycle node that captures and publishes the B2 onboard camera.

**Executable**: `b2_video_stream.py`

The B2 onboard front camera multicasts an RTP/H264 stream on the same
multicast group as the Go2 (`230.1.1.1:1720`) when the Unitree video
relay is running, so the GStreamer pipeline is unchanged.

| Parameter Name | Type | Default Value | Description |
|----------------|------|---------------|-------------|
| `prefix` | string | `""` | Topic prefix for published images |
| `network_interface` | string | `"eno1"` | Network interface for the video multicast |

Topics: `/{namespace}/b2_camera` (raw) and `/{namespace}/b2_compressed_camera` (JPEG).

---

## Launch Files

### robot_interface.launch.py

```bash
ros2 launch b2_pkg robot_interface.launch.py
```

Reads `robot_config.yaml` and starts:

1. **robot_read_node**
2. **lifecycle_robot_write_node**
3. **controller_commands_node**
4. **robot_video_stream**

This launch file is automatically included by `bot_bringup` when
`robot_model: "b2"` is set in `robot_config.yaml`.

## Configuration Files

### nav2_params.yaml

Nav2 parameters tuned for B2 dimensions and dynamics. Compared to Go2:

- Footprint: `[[0.65, 0.30], [0.65, -0.30], [-0.65, -0.30], [-0.65, 0.30]]` (~1.30 m × 0.60 m)
- Local inflation radius: 0.85 m
- Global inflation radius: 0.90 m
- Velocity smoother: max 0.8 m/s linear, 1.2 rad/s angular (autonomous-nav profile, well below the B2's 6 m/s capability)

### camera_config.yaml

Front/back RealSense calibration positions are shifted forward and higher
than Go2 to reflect the B2's taller dorsal mounting plate.

## Robot Description Files

### XACRO Files

Located in [xacro/](xacro/):

- **robot.xacro** - Main B2 description
- **leg.xacro** - Leg kinematic chain
- **const.xacro** - B2-specific constants (length 1.10 m, leg ~0.70 m, mass ~60 kg, joint torques up to 320 Nm)
- **materials.xacro** - Visual materials

### Meshes

The XACROs reference these mesh files in [meshes/](meshes/):

- `trunk.dae` - B2 body
- `hip.dae` - Hip joint
- `thigh.dae` / `thigh_mirror.dae` - Thigh links
- `calf.dae` / `calf_mirror.dae` - Calf links
- `foot.dae` - Foot contact link
- `b2_interface.stl` - BotBrain mounting plate (B2-specific)

> **Important:** This package is shipped without binary mesh files because
> the official Unitree B2 meshes are distributed in their own repository
> under their own license. To populate this folder:
>
> ```bash
> # Clone Unitree's ROS 2 description set
> git clone https://github.com/unitreerobotics/unitree_ros2.git /tmp/unitree_ros2
>
> # Copy B2 meshes into b2_pkg
> cp /tmp/unitree_ros2/example/src/src/b2_description/meshes/*.{dae,stl} \
>    botbrain_ws/src/b2_pkg/meshes/
> ```
>
> If your copy of `unitree_ros2` exposes the description as `b2w_description`
> (B2-W variant), source from there instead. The `b2_interface.stl` BotBrain
> mounting plate ships separately under `hardware/`.

## Transforms (TF)

| Parent Frame | Child Frame | Source | Rate |
|--------------|-------------|--------|------|
| `odom` | `base_link` | Odometry integration | 50 Hz |

The complete kinematic tree is published by `robot_state_publisher`
using joint states from this package.

## Integration with BotBrain System

### Automatic Loading

```yaml
# robot_config.yaml
robot_configuration:
  robot_model: "b2"   # Triggers b2_pkg loading
```

`bot_bringup` will:
1. Read `robot_model: "b2"`
2. Construct package name `b2_pkg`
3. Include `b2_pkg/launch/robot_interface.launch.py`
4. Load description from `b2_pkg/xacro/robot.xacro`

## Usage

### Standalone Testing

```bash
# Source workspace
source install/setup.bash

# Launch B2 interface only
ros2 launch b2_pkg robot_interface.launch.py

# Verify nodes are running
ros2 node list | grep b2

# Expected output:
# /robot_name/robot_read_node
# /robot_name/lifecycle_robot_write_node
# /robot_name/controller_commands_node
# /robot_name/robot_video_stream
```

## Directory Structure

```
b2_pkg/
├── launch/
│   └── robot_interface.launch.py     # Main hardware interface launcher
│
├── scripts/
│   ├── b2_read.py                    # Sensor data publisher node
│   ├── b2_write.py                   # Command executor node
│   ├── b2_controller_commands.py     # Controller translator node
│   └── b2_video_stream.py            # Video publisher node
│
├── config/
│   ├── nav2_params.yaml              # Navigation parameters for B2
│   └── camera_config.yaml            # Camera mounting parameters
│
├── xacro/
│   ├── robot.xacro                   # Main robot description
│   ├── leg.xacro                     # Leg kinematic chain
│   ├── const.xacro                   # B2 constants
│   └── materials.xacro               # Visual materials
│
├── meshes/                           # (populate from unitree_ros2)
│
├── maps/
│   └── [environment maps]            # Pre-built maps for B2
│
├── b2_pkg/
│   └── tools/
│       └── b2.py                     # LangChain agent helpers
│
├── b2_setup.bash                     # Environment setup script
├── CMakeLists.txt                    # Build configuration
├── package.xml                       # Package manifest
└── README.md                         # This file
```

---

<p align="center">Made with ❤️ in Brazil</p>

<p align="right">
  <img src="https://cdn.prod.website-files.com/672ed723fbdc1589fa127239/67522c0342667cac3a16a994_Bot%20icon%20(1).png" alt="Bot icon" width="110">
</p>
