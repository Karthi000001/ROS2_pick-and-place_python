# ROS 2 Pick-and-Place Demo

A minimal, well-structured Python simulation of an AI-powered  
bin-picking orchestrator — the core system used in warehouse  
robotics deployments.

**Author:** Karthikeyan Raja  
**Target role:** Deployment Engineer — Sereact GmbH  
**Stack:** Python 3.10 · ROS 2 Humble · Docker

---

## What this project demonstrates

| Skill | Where to look |
|---|---|
| ROS 2 node architecture | `ros2_pick_place/orchestrator.py` |
| State machine design | `ros2_pick_place/state.py` |
| Perception pipeline concept | `ros2_pick_place/perception.py` |
| Motion planning interface | `ros2_pick_place/motion.py` |
| Gripper control | `ros2_pick_place/gripper.py` |
| Config-driven deployment | `config/settings.yaml` |
| Unit + integration testing | `tests/` |
| Docker containerisation | `Dockerfile`, `docker-compose.yml` |
| CI/CD | `.github/workflows/ci.yml` |

---

## Project structure

```
ros2_pick_place_demo/
│
├── main.py                         # Entry point — run the demo here
│
├── ros2_pick_place/                # Main Python package
│   ├── __init__.py
│   ├── orchestrator.py             # Coordinates the full pick cycle
│   ├── state.py                    # PickState enum (IDLE → SUCCESS)
│   ├── perception.py               # Object detection simulation
│   ├── motion.py                   # Trajectory planning & execution
│   └── gripper.py                  # Open / close gripper
│
├── utils/
│   ├── __init__.py
│   └── config_loader.py            # Loads config/settings.yaml
│
├── config/
│   └── settings.yaml               # All tuneable parameters
│
├── tests/
│   ├── test_perception.py          # Unit tests for PerceptionModule
│   ├── test_gripper.py             # Unit tests for GripperController
│   └── test_orchestrator.py        # Integration tests for the cycle
│
├── Dockerfile                      # ROS 2 Humble container
├── docker-compose.yml              # Service definition
├── requirements.txt                # Python dependencies
└── .github/workflows/ci.yml        # GitHub Actions CI
```

---

## Quick start (no ROS 2 needed)

```bash
# 1. Clone
git clone https://github.com/<your-username>/ros2_pick_place_demo.git
cd ros2_pick_place_demo

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the demo
python main.py
```

**Example output:**

```
=======================================================
  ROS 2 Pick-and-Place Demo
  Author : Karthikeyan Raja
  Target : Sereact GmbH — Deployment Engineer
=======================================================

Config: bin=A1  place=P1  retries=3  conf_threshold=0.75

[Config] Loaded from config/settings.yaml
[10:42:01] [Orchestrator] Orchestrator ready | bin=A1 place=P1
[10:42:01] [Orchestrator] State → DETECTING
[Perception] Scanning bin zone: A1
[Perception]  box_A        pos=(0.42, 0.18, 0.31)  conf=0.94
[Perception]  cylinder_C   pos=(0.39, 0.22, 0.28)  conf=0.81
[10:42:01] [Orchestrator] Selected: box_A at (0.42, 0.18, 0.31) conf=0.94
[10:42:01] [Orchestrator] State → PLANNING
[Motion] Planning to (0.420, 0.180, 0.310)
[Motion] Planned 5 waypoints
[10:42:01] [Orchestrator] State → EXECUTING
[Gripper] Opening
[Motion] Step 1/5  20%  joints=[...]
...
[Gripper] Closing on object
[10:42:02] [Orchestrator] State → PLACING
[Motion] Moving to place zone: P1
[Gripper] Opening
[Motion] Returning home
[10:42:02] [Orchestrator] State → SUCCESS

=======================================================
  RESULT : SUCCESS ✓
  Object : box_A
  Time   : 2.41 s
  Retries: 0
=======================================================
```

---

## Command-line options

```bash
# Override bin and place zones
python main.py --bin B2 --place P2

# Override retry count
python main.py --retries 1

# Use a different config file
python main.py --config config/settings.yaml
```

---

## Run tests

```bash
pytest tests/ -v
```

All 15 tests should pass. Tests cover:
- Normal successful pick
- Empty bin → FAILED
- Low-confidence detection → FAILED  
- Motion planning failure → retry
- Recovery after one failed attempt

---

## Run with Docker

```bash
# Build the image
docker build -t pick-place-demo .

# Run the demo
docker run --rm pick-place-demo

# Run tests inside the container
docker run --rm pick-place-demo pytest tests/ -v
```

---

## Architecture

```
                ┌─────────────────────┐
                │  PickPlaceOrchestrator │
                │  (orchestrator.py)   │
                └──────────┬──────────┘
                           │ coordinates
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
  │ Perception   │  │   Motion     │  │   Gripper    │
  │ Module       │  │   Planner    │  │ Controller   │
  │              │  │              │  │              │
  │ detect(zone) │  │ plan_to_pose │  │ open()       │
  │ → candidates │  │ execute()    │  │ close()      │
  └──────────────┘  └──────────────┘  └──────────────┘

  State machine:
  IDLE → DETECTING → PLANNING → EXECUTING → PLACING → SUCCESS
                                                    ↘ FAILED
```

**ROS 2 topics published** (when running inside ROS 2):

| Topic | Type | Description |
|---|---|---|
| `/pick_status` | `std_msgs/String` | JSON with current state + timestamp |
| `/system_ready` | `std_msgs/Bool` | `True` when state is IDLE |

---

## Design decisions

**Why simulate hardware?**  
Allows the full orchestration logic to be demonstrated, tested, and  
explained without physical hardware — important for a portfolio project.

**Why separate modules?**  
Each module (Perception, Motion, Gripper) has one responsibility. This  
makes the code easy to test independently and easy to swap for real  
hardware drivers in a production deployment.

**Why YAML config?**  
Settings (bin zone, confidence threshold, retry count) change per  
customer site. Keeping them in a YAML file means no code changes are  
needed for a new deployment — just update the config.

**Why Docker?**  
Packaging the ROS 2 environment in a container ensures the system runs  
identically on any customer machine, and makes rollbacks trivial.

---

## Next steps (production upgrade path)

| Component | Demo | Production |
|---|---|---|
| Perception | Random simulation | FoundationPose / PickNet DNN |
| Motion planning | Linear interpolation | MoveIt 2 + KDL IK solver |
| Gripper | Simulated delay | Robotiq 2F-140 ROS 2 driver |
| State publishing | std_msgs/String | Custom ROS 2 action server |
| Config | YAML file | ROS 2 parameters + launch files |
