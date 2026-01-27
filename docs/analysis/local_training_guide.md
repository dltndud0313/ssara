# 로컬 설정으로 Isaac Lab 학습 실행하기

이 가이드는 로컬 `scripts` 디렉토리에 **로컬 학습 실행 스크립트(`local_train.py`)**를 생성하여, Isaac Lab 시스템 파일(컨테이너 내부 파일)을 수정하지 않고 안전하게 사용자 지정 태스크를 학습시키는 방법을 설명합니다.

## 1. 개념

Isaac Lab의 기본 `train.py`를 직접 수정하는 것은 시스템 무결성을 해칠 수 있습니다. 대신, **로컬 스크립트(`scripts/local_train.py`)**를 만들어 다음 두 가지 역할을 수행하게 합니다:
1.  사용자 지정 태스크(`custom_quadruped_isaac`)를 가져와서 Gym에 등록합니다.
2.  Isaac Lab의 표준 학습 로직을 실행합니다.

이 방식은 원본 시스템 파일을 **전혀 건드리지 않으면서** 사용자 지정 설정을 적용할 수 있는 가장 안전하고 권장되는 방법입니다.

## 2. 디렉토리 구조

`scripts` 디렉토리를 다음과 같이 구성합니다:

```text
scripts/
├── local_train.py               # [NEW] 로컬 실행용 학습 스크립트
└── custom_quadruped_isaac/      # 구성 패키지
    ├── __init__.py              # gym config 등록
    ├── env_cfg.py               # 환경 구성 정의 (ManagerBasedRLEnvCfg)
    ├── agent_cfg.py             # RSL-RL Runner 구성 정의 (OnPolicyRunnerCfg)
    ├── ...
```

## 3. 구현 단계

### 단계 1 ~ 3: 구성 파일 생성

`env_cfg.py`, `agent_cfg.py`, `__init__.py` 등은 이전과 동일하게 `scripts/custom_quadruped_isaac/` 폴더 내에 생성합니다 (이전 가이드 내용 참조).

### 단계 4: 로컬 실행 스크립트 생성 (`local_train.py`)

`scripts/local_train.py` 파일을 생성하고 아래 내용을 복사해 넣으세요. 이 코드는 Isaac Lab의 기본 `train.py`를 기반으로 하며, 로컬 구성을 로드하는 코드가 추가되어 있습니다.

```python
# scripts/local_train.py

import argparse
import os
import sys

# [중요] 로컬 패키지 경로 추가 및 가져오기
# 현재 파일(local_train.py)이 있는 디렉토리를 sys.path에 추가하여 
# 형제 폴더인 custom_quadruped_isaac를 import 할 수 있게 합니다.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 사용자 지정 태스크 등록 (이 import가 실행되면서 __init__.py의 gym.register가 호출됨)
import custom_quadruped_isaac

# -----------------------------------------------------------------------------
# 아래는 Isaac Lab 표준 train.py의 내용과 동일합니다.
# -----------------------------------------------------------------------------

from isaaclab.app import AppLauncher

# add argparse arguments
parser = argparse.ArgumentParser(description="Train an RL agent with RSL-RL.")
parser.add_argument("--video", action="store_true", default=False, help="Record videos during training.")
parser.add_argument("--video_length", type=int, default=200, help="Length of the recorded video (in steps).")
parser.add_argument("--video_interval", type=int, default=2000, help="Interval between video recordings (in steps).")
parser.add_argument("--cpu", action="store_true", default=False, help="Use CPU pipeline.")
parser.add_argument(
    "--num_envs", type=int, default=None, help="Number of environments to simulate."
)
parser.add_argument("--task", type=str, default=None, help="Name of the task.")
parser.add_argument(
    "--agent", type=str, default="rsl_rl_cfg_entry_point", help="Name of the RL agent configuration entry point."
)
parser.add_argument("--seed", type=int, default=None, help="Seed used for the environment")
parser.add_argument("--max_iterations", type=int, default=None, help="RL Policy training iterations.")
parser.add_argument(
    "--distributed", action="store_true", default=False, help="Run training with multiple GPUs or nodes."
)
parser.add_argument("--export_io_descriptors", action="store_true", default=False, help="Export IO descriptors.")
parser.add_argument(
    "--ray-proc-id", "-rid", type=int, default=None, help="Automatically configured by Ray integration, otherwise None."
)

# append RSL-RL cli arguments
import rsl_rl.cli_args as cli_args  # [주의] import 경로가 상황에 따라 다를 수 있으나 보통 rsl_rl이 설치되어 있습니다.
# 만약 위 라인에서 에러가 나면 isaaclab_rl.rsl_rl 등을 확인해야 합니다.
# 원본 코드에서는 파일 상단에서 import하지 않고 parser 구성 중에 사용되는 경우가 많습니다.

# 여기서는 원본 train.py의 로직을 그대로 가져오기 위해 필요한 import들을 상단에 정리합니다.
import gymnasium as gym
import torch
import time
from datetime import datetime
from isaaclab.envs import DirectMARLEnv, DirectMARLEnvCfg, DirectRLEnvCfg, ManagerBasedRLEnvCfg, multi_agent_to_single_agent
from isaaclab.utils.dict import print_dict
from isaaclab.utils.io import dump_yaml
from isaaclab_rl.rsl_rl import RslRlBaseRunnerCfg, RslRlVecEnvWrapper, RslRlOnPolicyRunnerCfg
import isaaclab_tasks
from isaaclab_tasks.utils import get_checkpoint_path
from isaaclab_tasks.utils.hydra import hydra_task_config
from rsl_rl.runners import DistillationRunner, OnPolicyRunner

# Parser 구성 계속
cli_args.add_rsl_rl_args(parser)
AppLauncher.add_app_launcher_args(parser)
args_cli, hydra_args = parser.parse_known_args()

if args_cli.video:
    args_cli.enable_cameras = True

sys.argv = [sys.argv[0]] + hydra_args

# launch omniverse app
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True
torch.backends.cudnn.deterministic = False
torch.backends.cudnn.benchmark = False

@hydra_task_config(args_cli.task, args_cli.agent)
def main(env_cfg: ManagerBasedRLEnvCfg | DirectRLEnvCfg | DirectMARLEnvCfg, agent_cfg: RslRlBaseRunnerCfg):
    """Train with RSL-RL agent."""
    # override configurations with non-hydra CLI arguments
    agent_cfg = cli_args.update_rsl_rl_cfg(agent_cfg, args_cli)
    env_cfg.scene.num_envs = args_cli.num_envs if args_cli.num_envs is not None else env_cfg.scene.num_envs
    agent_cfg.max_iterations = (
        args_cli.max_iterations if args_cli.max_iterations is not None else agent_cfg.max_iterations
    )

    env_cfg.seed = agent_cfg.seed
    env_cfg.sim.device = args_cli.device if args_cli.device is not None else env_cfg.sim.device
    
    if args_cli.distributed and args_cli.device is not None and "cpu" in args_cli.device:
        raise ValueError("Distributed training requires GPU.")

    if args_cli.distributed:
        env_cfg.sim.device = f"cuda:{app_launcher.local_rank}"
        agent_cfg.device = f"cuda:{app_launcher.local_rank}"
        seed = agent_cfg.seed + app_launcher.local_rank
        env_cfg.seed = seed
        agent_cfg.seed = seed

    # specify directory for logging experiments
    log_root_path = os.path.join("logs", "rsl_rl", agent_cfg.experiment_name)
    log_root_path = os.path.abspath(log_root_path)
    print(f"[INFO] Logging experiment in directory: {log_root_path}")
    
    log_dir = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if agent_cfg.run_name:
        log_dir += f"_{agent_cfg.run_name}"
    log_dir = os.path.join(log_root_path, log_dir)

    if isinstance(env_cfg, ManagerBasedRLEnvCfg):
        env_cfg.export_io_descriptors = args_cli.export_io_descriptors
    
    env_cfg.log_dir = log_dir

    # create isaac environment
    env = gym.make(args_cli.task, cfg=env_cfg, render_mode="rgb_array" if args_cli.video else None)

    if isinstance(env.unwrapped, DirectMARLEnv):
        env = multi_agent_to_single_agent(env)

    if agent_cfg.resume or agent_cfg.algorithm.class_name == "Distillation":
        resume_path = get_checkpoint_path(log_root_path, agent_cfg.load_run, agent_cfg.load_checkpoint)

    if args_cli.video:
        video_kwargs = {
            "video_folder": os.path.join(log_dir, "videos", "train"),
            "step_trigger": lambda step: step % args_cli.video_interval == 0,
            "video_length": args_cli.video_length,
            "disable_logger": True,
        }
        env = gym.wrappers.RecordVideo(env, **video_kwargs)

    start_time = time.time()
    env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)

    if agent_cfg.class_name == "OnPolicyRunner":
        runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=log_dir, device=agent_cfg.device)
    elif agent_cfg.class_name == "DistillationRunner":
        runner = DistillationRunner(env, agent_cfg.to_dict(), log_dir=log_dir, device=agent_cfg.device)
    else:
        raise ValueError(f"Unsupported runner class: {agent_cfg.class_name}")

    if agent_cfg.resume or agent_cfg.algorithm.class_name == "Distillation":
        runner.load(resume_path)

    dump_yaml(os.path.join(log_dir, "params", "env.yaml"), env_cfg)
    dump_yaml(os.path.join(log_dir, "params", "agent.yaml"), agent_cfg)

    runner.learn(num_learning_iterations=agent_cfg.max_iterations, init_at_random_ep_len=True)
    env.close()

if __name__ == "__main__":
    main()
    simulation_app.close()
```

## 4. 실행 명령

새로 생성한 로컬 스크립트를 사용하여 실행합니다.

```bash
./isaaclab.sh -p scripts/local_train.py --task Isaac-Velocity-Flat-Custom-Quad-v0 --num_envs=512
```

### 작동 원리:
1.  **`./isaaclab.sh -p`**: Python 환경을 시작합니다.
2.  **`scripts/local_train.py`**: 로컬 파일이 실행됩니다. 이 파일은 시스템 파일(`train.py`)의 복사본이므로 기능상 동일하지만, 로컬 수정을 포함할 수 있습니다.
3.  **`import custom_quadruped_isaac`**: 스크립트 실행 시 가장 먼저 로컬 태스크 등록이 수행됩니다.
4.  **시스템 파일 보존**: 컨테이너나 Isaac Lab 소스 트리의 어떤 파일도 수정하지 않았으므로 업데이트나 재시작 시 안전합니다.
