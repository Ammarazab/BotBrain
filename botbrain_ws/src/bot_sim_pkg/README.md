<p align="center">
  <a href="https://botbot.bot" target="_blank">
    <img src="https://cdn.prod.website-files.com/672ed723fbdc1589fa127239/672ed83e9ab7d55f18a3c43f_BotBot%20Purple%20Logo%20(2)-p-500.png" alt="BotBot" width="180">
  </a>
</p>

# bot_sim_pkg

**Simulation backends for BotBrain — Isaac Sim 5.0+ and Gazebo Harmonic.**

This package lets you run the entire BotBrain stack — frontend dashboard,
Nav2, RTABMap, twist_mux, mode services, the lifecycle write/read nodes —
against a simulated robot, on **Ubuntu 22.04 + ROS 2 Humble**.

It does **not** patch the existing `*_pkg` (`go2_pkg`, `b2_pkg`, ...).
Instead, a small **Unitree SDK shim node** translates between the
simulator's generic ROS topics (`/joint_states`, `/imu/data`, `/odom`,
`/cmd_vel`) and the Unitree-DDS topic shape (`/lf/sportmodestate`,
`/lf/lowstate`, `/api/sport/request`, ...). The real `*_write.py` and
`*_read.py` keep working unchanged.

## Architecture

```
┌─────────────────────┐   /sim/cmd_vel  ┌───────────────────┐
│  Sim backend        │ ◄─────────────  │ unitree_sdk_shim  │
│  (Isaac / Gazebo)   │                 │  (this package)   │
│  publishes          │ /joint_states   │                   │
│  /joint_states      │ ──────────────► │ re-publishes as   │
│  /imu/data          │ /imu/data       │   /lf/lowstate    │
│  /odom              │ ──────────────► │   /lf/sportmodestate
└─────────────────────┘ /odom           └─────────┬─────────┘
                       ──────────────►           │
                                                 ▼
        ┌──────────────────────────────────────────────────────┐
        │ go2_pkg / b2_pkg / ... lifecycle write & read nodes  │
        │ (UNCHANGED — they think they're talking to real HW)  │
        └────────────────────────┬─────────────────────────────┘
                                 │
                                 ▼
                  twist_mux ─► Nav2 ─► RTABMap ─► dashboard
```

## Backend selection

| Use case                                   | Recommendation |
|--------------------------------------------|----------------|
| Locomotion / RL fidelity, photoreal cameras | **Isaac Sim 5.0+** with Isaac Lab |
| Quick Nav2 / SLAM / dashboard iteration    | **Gazebo Harmonic** (kinematic locomotion fallback) |

You can switch at any time with one launch arg.

## Quick start

```bash
# 1. Set robot_model in workspace robot_config.yaml (e.g. "go2" or "b2")

# 2. Source your built workspace
source install/setup.bash

# 3a. Gazebo
ros2 launch bot_bringup bringup.launch.py use_sim:=true sim_backend:=gazebo

# 3b. Isaac Sim
ros2 launch bot_bringup bringup.launch.py use_sim:=true sim_backend:=isaac

# Real hardware (default — unchanged)
ros2 launch bot_bringup bringup.launch.py
```

The frontend dashboard, joystick, and Nav2 stack come up the same way
in either mode — the dashboard cannot tell the difference.

---

## Backend 1 — Gazebo Harmonic

### Install (Ubuntu 22.04 + ROS 2 Humble)

```bash
# Add OSRF Gazebo apt source
sudo wget https://packages.osrfoundation.org/gazebo.gpg \
     -O /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) \
     signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] \
     http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | \
     sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null

sudo apt update
sudo apt install gz-harmonic ros-humble-ros-gzharmonic
```

### What gets launched

`launch/gazebo.launch.py` starts (in order):

1. **`gz sim`** with `worlds/empty.sdf` (ground plane + lighting + IMU/sensors plugins).
2. **`ros_gz_sim create`** spawns the URDF rendered from `<robot_model>_pkg/xacro/robot.xacro`.
3. **`ros_gz_bridge`** for `/clock` so `use_sim_time` works.
4. **`kinematic_locomotion_node.py`** — integrates `cmd_vel` → pose, teleports the model via `gz service set_pose`, publishes `/joint_states`, `/imu/data`, `/odom`. This is intentionally simple: realistic legged controllers in Gazebo are flaky, and for Nav2/SLAM the kinematic approximation is fine.
5. **`unitree_sdk_shim_node.py`** — translates everything onto Unitree topics so `*_write.py`/`*_read.py` work.

### Tuning

`config/sim.yaml` exposes the publish rate, fake battery voltage/SOC,
spawn height, and the cmd-vel topic. You can also pass `world:=...sdf`
to load a different scene.

---

## Backend 2 — Isaac Sim 5.0+

### Install (Ubuntu 22.04 + RTX GPU + driver ≥535)

```bash
# Create a Python venv that Isaac Sim will own
python3.10 -m venv ~/isaacsim_venv
source ~/isaacsim_venv/bin/activate
pip install --upgrade pip

# Isaac Sim 5.0+ is now pip-installable
pip install --extra-index-url https://pypi.nvidia.com isaacsim==5.0.* \
            isaacsim-extscache-physics==5.0.* \
            isaacsim-extscache-kit==5.0.* \
            isaacsim-extscache-kit-sdk==5.0.*

# Optional but recommended: Isaac Lab 2.0+ for Unitree RL policies
pip install isaaclab==2.0.*
```

### What gets launched

`launch/isaac_sim.launch.py` runs `scripts/isaac_sim_runner.py` as a
child process under the Isaac Sim Python interpreter, then starts the
shim. The runner:

1. Bootstraps `isaacsim.SimulationApp` (the 5.0+ API; the old
   `omni.isaac.kit.SimulationApp` is gone).
2. Enables `isaacsim.ros2.bridge` (renamed from
   `omni.isaac.ros2_bridge` in 5.0).
3. Loads the Unitree USD from the assets server
   (`/Isaac/Robots/Unitree/{Go2,B2,Go2W,G1}/...`) and adds it under
   `/World/Botbrain`.
4. If Isaac Lab is available, picks up `UNITREE_GO2_CFG` / `UNITREE_B2_CFG`
   / `UNITREE_G1_CFG` and uses the bundled RL locomotion policy. Without
   Isaac Lab the robot is inert (you'll still get topics, but no walking).
5. Builds an OmniGraph that publishes `/joint_states`, `/imu/data`,
   `/odom` and subscribes to `/sim/cmd_vel`.

### Talking to the rest of BotBrain

Isaac Sim's ROS 2 bridge uses CycloneDDS. Make sure the rest of
your stack does too (the existing `<robot>_setup.bash` already exports
`RMW_IMPLEMENTATION=rmw_cyclonedds_cpp`). The launch sets the env
explicitly when spawning the Isaac child process.

### Headless mode

```bash
ros2 launch bot_bringup bringup.launch.py \
     use_sim:=true sim_backend:=isaac headless:=true
```

---

## What the shim does (in detail)

### Inbound (sim → BotBrain)

| Sim topic       | Re-published as |
|-----------------|-----------------|
| `/joint_states` | `LowState.motor_state[i].q / .dq` (Unitree ordering: FR,FL,RR,RL × hip,thigh,calf) |
| `/imu/data`     | `LowState.imu_state` and `SportModeState.imu_state` |
| `/odom`         | `SportModeState.position[]`, `.velocity[]`, `.body_height`, `.yaw_speed` |

The shim also fakes `LowState.power_v` and `LowState.bms_state.soc` from
parameters so the dashboard battery widget doesn't show NaN.

### Outbound (BotBrain → sim)

| Unitree topic                       | Action |
|-------------------------------------|--------|
| `/api/sport/request` `api_id=1008` (Move) | Parse JSON `{"x","y","z"}`, publish on `/sim/cmd_vel` |
| `/api/sport/request` `api_id=1001/1002/1004/1005/1009` | Update internal mode FSM (Damp / BalanceStand / StandUp / StandDown / Sit) so `SportModeState.mode` matches |
| `/api/sport/request` `api_id=1011` (SwitchGait) | Update `SportModeState.gait_type` |
| `/api/sport/request` (any other)    | Acked with status `0` |
| `/api/robot_state/request`          | Acked with status `0` (so MCF disable / sport_mode enable in `*_write.on_activate` succeed) |
| `/api/vui/request`                  | Acked, payload echoed |
| `/api/obstacles_avoid/request`      | Acked |

This is intentionally permissive: every request returns success so the
existing lifecycle initialisation sequences complete.

---

## Directory structure

```
bot_sim_pkg/
├── launch/
│   ├── sim_bringup.launch.py        # Top-level: pick isaac or gazebo
│   ├── gazebo.launch.py             # Gazebo Harmonic backend
│   └── isaac_sim.launch.py          # Isaac Sim 5.0+ backend
│
├── scripts/
│   ├── unitree_sdk_shim_node.py     # The core bridge (always runs)
│   ├── kinematic_locomotion_node.py # Gazebo cmd_vel→pose+odom fallback
│   └── isaac_sim_runner.py          # Standalone Isaac Sim 5.0+ script
│
├── bot_sim_pkg/
│   └── unitree_shim_helpers.py      # Shared constants + math
│
├── config/
│   └── sim.yaml                     # Default sim parameters
│
├── worlds/
│   └── empty.sdf                    # Default Gazebo world
│
├── package.xml
├── CMakeLists.txt
└── README.md
```

## Limitations & caveats

- **Gazebo** locomotion is kinematic only — no contact forces, no ground
  reaction. For Nav2/SLAM/dashboard work this is fine; for gait
  research use Isaac Sim instead.
- **Isaac Sim** without Isaac Lab will spawn the robot but won't walk.
  Install `isaaclab` to get Unitree's pre-trained policies.
- The shim acks every Unitree API request with success — it does not
  enforce safety envelopes the real robot would. Limits are still
  enforced inside the `*_write.py` services, just not in the response
  payload.
- The mock battery never drains. PRs welcome.

---

<p align="center">Made with ❤️ in Brazil</p>
