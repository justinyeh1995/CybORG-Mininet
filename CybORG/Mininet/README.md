# Realistic and Lightweight Cyber Agent Training Environment using Network Emulation in Mininet

## Presentation slides for DESTION 2024 on May 13th, 2024

[Google Slides](https://docs.google.com/presentation/d/1f2pZ5q3p6cZK4m2dvq1Tvgj8ODyTyWGp3OVP4xXuaOw/edit?usp=sharing)
[Paper Link](https://www.computer.org/csdl/proceedings-article/destion/2024/759400a028/1Y42Ek9NEsg)

## High Level Architecture

https://drive.google.com/file/d/1VZ-ZIUBdbR0TQSjXfNiUfRoqEBmi0Csw/view?usp=sharing

A good way to understand how each component fits each other, please take a look the integration test at `Tests/test_exploit_action.py`

## Catalog

1. [setup.md](https://github.com/CASTLEGym/CybORG/blob/mininet-cyborg2/CybORG/Mininet/docs/setup.md)
2. dev.md

## Getting Started

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Demo

```bash
git clone https://github.com/CASTLEGym/CybORG.git
cd CybORG
git checkout mininet-cyborg2
pip install -e .
cd CybORG/Mininet
```

## Configuration

📌 Modify the value based on your system configuration in `config.cfg`

```cfg
[SCENARIO]
FILE_PATH=/Simulator/Scenarios/scenario_files/<YOUR SCENARIO FILE>

[PYTHON]
FILE_PATH=<YOUR ABSOLUTE PYTHON EXECUTION FILE PATH>

[ACTION]
FOLDER_PATH=/Mininet/Actions

```

## Run the experiment

```bash
python3 main.py --env <sim | emu> --max_step <step size> --max_episode <number of episodes>
```

## To-Do
Following new implementations in `wrapper` branch, such as `Impact` Action implementation.

## Supporting more actions

📗 Please follow this workflow to support a new action 
