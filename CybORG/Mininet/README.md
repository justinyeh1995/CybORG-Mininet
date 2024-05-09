## Catalog

1. [setup.md](https://github.com/CASTLEGym/CybORG/blob/mininet/CybORG/Mininet/docs/setup.md)
2. dev.md

## Demo
```
git clone https://github.com/CASTLEGym/CybORG.git
cd CybORG
git checkout mininet
pip install -e .
cd CybORG/Mininet
```

## Configuration

Modify the value based on your system configuration in `config.ini`

```ini
[SCENARIO]
FILE_PATH=/Simulator/Scenarios/scenario_files/<YOUR SCENARIO FILE>

[PYTHON]
FILE_PATH=<YOUR ABSOLUTE PYTHON EXECUTION FILE PATH>

[ACTION]
FOLDER_PATH=/Mininet/actions

[DECOY]
FOLDER_PATH=/Emulator/Velociraptor/Executables/Decoy
```

## Run the experiment

```bash
python3 main.py --env <sim | emu> --max_step <step size> --max_episode <number of episodes>
```
