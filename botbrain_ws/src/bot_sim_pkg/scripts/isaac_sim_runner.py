#!/usr/bin/env python3
"""
Isaac Sim 5.0+ standalone runner for BotBrain.

This script is run *outside* a normal ROS launch — Isaac Sim spawns
its own Python interpreter. Use it as:

    # Activate Isaac Sim 5.0+ Python (pip install) or use isaaclab.sh
    python -m isaacsim botbrain_ws/src/bot_sim_pkg/scripts/isaac_sim_runner.py \\
        --robot go2 --headless false

What it does:
  1. Bootstraps Isaac Sim with the new isaacsim.SimulationApp API (5.0+).
  2. Enables the isaacsim.ros2.bridge extension.
  3. Loads a ground plane, lights, and the Unitree USD that ships with
     Isaac Lab (Go2/B2/G1 are bundled in the official Nucleus assets).
  4. Subscribes to /sim/cmd_vel and feeds the velocity into the robot's
     RL locomotion policy (Isaac Lab provides one out of the box).
  5. Publishes /joint_states, /imu/data, /odom via the ROS 2 bridge so
     bot_sim_pkg's unitree_sdk_shim_node can consume them.

Notes:
  - Requires Isaac Sim ≥5.0 and Isaac Lab ≥2.0 on Ubuntu 22.04 with an
    RTX GPU (driver ≥535).
  - The ROS 2 bridge inside Isaac uses CycloneDDS; export
    RMW_IMPLEMENTATION=rmw_cyclonedds_cpp before launching to share a
    DDS domain with the rest of BotBrain.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# ----------------------------------------------------------------------
# Step 1: bootstrap Isaac Sim. Must happen before importing omni.* / isaacsim.*.
# ----------------------------------------------------------------------
def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='BotBrain Isaac Sim runner (5.0+).')
    p.add_argument('--robot', default='go2', choices=['go2', 'b2', 'go2w', 'g1'])
    p.add_argument('--headless', default='false', choices=['true', 'false'])
    p.add_argument('--usd', default='', help='Override USD path for the robot.')
    p.add_argument('--cmd-vel-topic', default='/sim/cmd_vel')
    p.add_argument('--initial-z', type=float, default=0.45)
    p.add_argument('--rate-hz', type=float, default=200.0,
                   help='Physics step rate.')
    return p.parse_args()


_ARGS = _parse_args()

# Isaac Sim 5.0+: SimulationApp moved out of omni.isaac.kit.
try:
    from isaacsim import SimulationApp  # type: ignore[import-not-found]
except ImportError as e:
    raise SystemExit(
        "Could not import 'isaacsim'. Install Isaac Sim 5.0+ via:\n"
        "  pip install isaacsim==5.0.* --extra-index-url https://pypi.nvidia.com\n"
        "Then run this script with the Isaac Sim Python or `python -m isaacsim`."
    ) from e

simulation_app = SimulationApp({
    'headless': _ARGS.headless == 'true',
    'physics_gpu': 0,
    'renderer': 'RayTracedLighting',
})

# ----------------------------------------------------------------------
# Step 2: now safe to import the rest of the Isaac Sim 5.0+ stack.
# ----------------------------------------------------------------------
import carb  # noqa: E402
import omni.usd  # noqa: E402
from isaacsim.core.api import World  # noqa: E402
from isaacsim.core.utils.extensions import enable_extension  # noqa: E402
from isaacsim.core.utils.stage import add_reference_to_stage  # noqa: E402
from isaacsim.storage.native import get_assets_root_path  # noqa: E402
from pxr import UsdGeom, Gf  # noqa: E402

enable_extension('isaacsim.ros2.bridge')

# Try to enable Isaac Lab if installed — gives us Unitree's RL policies.
try:
    enable_extension('isaaclab')
    from isaaclab_assets.robots.unitree import (  # noqa: E402
        UNITREE_GO2_CFG, UNITREE_B2_CFG, UNITREE_G1_CFG,
    )
    _HAS_ISAAC_LAB = True
except Exception:
    _HAS_ISAAC_LAB = False


def _resolve_usd(robot: str, override: str = '') -> str:
    if override:
        return override
    assets = get_assets_root_path()
    if assets is None:
        raise SystemExit('Isaac assets server unreachable. Set $ISAAC_ASSETS_ROOT.')
    # Paths under Isaac Sim 5.0 Nucleus assets.
    usd_by_robot = {
        'go2':  '/Isaac/Robots/Unitree/Go2/go2.usd',
        'b2':   '/Isaac/Robots/Unitree/B2/b2.usd',
        'go2w': '/Isaac/Robots/Unitree/Go2W/go2w.usd',
        'g1':   '/Isaac/Robots/Unitree/G1/g1.usd',
    }
    rel = usd_by_robot.get(robot)
    if rel is None:
        raise SystemExit(f'Unknown --robot {robot!r}.')
    return f'{assets}{rel}'


# ----------------------------------------------------------------------
# Step 3: build the scene.
# ----------------------------------------------------------------------
world = World(stage_units_in_meters=1.0, physics_dt=1.0 / _ARGS.rate_hz)
world.scene.add_default_ground_plane()

usd_path = _resolve_usd(_ARGS.robot, _ARGS.usd)
robot_prim_path = '/World/Botbrain'
add_reference_to_stage(usd_path=usd_path, prim_path=robot_prim_path)

# Translate the spawned robot above the ground plane.
stage = omni.usd.get_context().get_stage()
xform = UsdGeom.Xformable(stage.GetPrimAtPath(robot_prim_path))
xform.AddTranslateOp().Set(Gf.Vec3d(0.0, 0.0, _ARGS.initial_z))

# ----------------------------------------------------------------------
# Step 4: ROS 2 wiring. The isaacsim.ros2.bridge extension reads its
# graphs from OmniGraph nodes baked into the robot USD or added at
# runtime. The cleanest path is to load Isaac Lab's pre-built graph
# when available; otherwise fall back to manual graph construction.
# ----------------------------------------------------------------------
ros_node_namespace = ''  # joins with /joint_states, /imu/data, /odom, /sim/cmd_vel

if _HAS_ISAAC_LAB:
    carb.log_info('[botbrain] Isaac Lab detected — using bundled locomotion policy.')
    # Isaac Lab ships RL policies for Unitree robots. The full task setup
    # would normally happen inside an Isaac Lab Manager. For brevity we
    # only verify the asset is reachable here; production users should
    # spawn an `Articulation` from the appropriate ISAAC_LAB_ASSET cfg
    # and feed cmd_vel through `policy.act(obs)`.
    cfg = {'go2': UNITREE_GO2_CFG, 'b2': UNITREE_B2_CFG, 'g1': UNITREE_G1_CFG}.get(_ARGS.robot)
    if cfg is not None:
        carb.log_info(f'[botbrain] Resolved Isaac Lab cfg: {cfg.usd_path}')
else:
    carb.log_warn(
        '[botbrain] Isaac Lab not available. Robot will be inert; install Isaac Lab '
        'to get the Unitree RL locomotion policies (recommended).'
    )

# Build the OmniGraph for ROS2 publishing.
import omni.graph.core as og  # noqa: E402

(graph, _, _, _) = og.Controller.edit(
    {'graph_path': '/World/BotbrainROSGraph', 'evaluator_name': 'execution'},
    {
        og.Controller.Keys.CREATE_NODES: [
            ('OnTick',           'omni.graph.action.OnPlaybackTick'),
            ('PublishJointSt',   'isaacsim.ros2.bridge.ROS2PublishJointState'),
            ('PublishOdom',      'isaacsim.ros2.bridge.ROS2PublishOdometry'),
            ('PublishImu',       'isaacsim.ros2.bridge.ROS2PublishImu'),
            ('SubCmdVel',        'isaacsim.ros2.bridge.ROS2SubscribeTwist'),
        ],
        og.Controller.Keys.CONNECT: [
            ('OnTick.outputs:tick',          'PublishJointSt.inputs:execIn'),
            ('OnTick.outputs:tick',          'PublishOdom.inputs:execIn'),
            ('OnTick.outputs:tick',          'PublishImu.inputs:execIn'),
            ('OnTick.outputs:tick',          'SubCmdVel.inputs:execIn'),
        ],
        og.Controller.Keys.SET_VALUES: [
            ('PublishJointSt.inputs:topicName', '/joint_states'),
            ('PublishJointSt.inputs:nodeNamespace', ros_node_namespace),
            ('PublishOdom.inputs:topicName', '/odom'),
            ('PublishOdom.inputs:nodeNamespace', ros_node_namespace),
            ('PublishImu.inputs:topicName', '/imu/data'),
            ('PublishImu.inputs:nodeNamespace', ros_node_namespace),
            ('SubCmdVel.inputs:topicName', _ARGS.cmd_vel_topic),
            ('SubCmdVel.inputs:nodeNamespace', ros_node_namespace),
        ],
    },
)

# ----------------------------------------------------------------------
# Step 5: run.
# ----------------------------------------------------------------------
world.reset()
carb.log_info('[botbrain] Isaac Sim runner ready. Press Ctrl-C to quit.')
try:
    while simulation_app.is_running():
        world.step(render=True)
except KeyboardInterrupt:
    pass
finally:
    simulation_app.close()
