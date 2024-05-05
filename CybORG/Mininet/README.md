## Catalog

1. setup.md
2. dev.md

## Configuration

Open `config.ini`
Modify the value based on your system configuration

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
cd Mininet
python3 main.py --env <sim/emu> 
```
