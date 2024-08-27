# Realistic and Lightweight Cyber Agent Training Environment using Network Emulation in Mininet

## High-Level Architectural Overview

![CASTLEGym-Mininet drawio (1)](https://github.com/user-attachments/assets/378151a0-f496-4873-b92d-d7fa2b60edd2)

🟢  The green part except `Mininet API` resides in `Mininet/AdapterComponents`. They are the subcomponents that lives entirely in the object created by a class called `MininetAdapter` which is in `Mininet/MininetAdapter.py`. \
`Mininet API` resides in `Mininet/MininetAPI`, and it deals with configuring and setting up a Mininet process. This module is originally developed by Dr. Gokhale's lab.
  
🟠 The orange part resides in a class called `CybORGFactory` in `Mininet/CustomFactory.py`.
  
🟣 The purple part resides in a class called `AgentFactory` in `Mininet/CustomFactory.py`. 


A good way to understand how each component fits each other is to take a look at the integration test in `Tests/test_exploit_action.py`

## Installation

Take a look at [setup.md](https://github.com/CASTLEGym/CybORG/blob/mininet-cyborg2/CybORG/Mininet/docs/setup.md)

## Getting Started

```bash
# Create your virtual environment
python3 -m venv venv
source venv/bin/activate

# Clone the repo
git clone https://github.com/CASTLEGym/CybORG.git
cd CybORG
git checkout mininet-cyborg2

# Install packages
pip install -e .
```

## Configuration

📌 Modify the value based on your system configuration in `config.cfg`

```cfg
[PYTHON]
FILE_PATH=<YOUR ABSOLUTE PYTHON EXECUTION FILE PATH>
```

## Run the experiment

```bash
cd CybORG/Mininet
python3 main.py --env <sim | emu> --max_step <step size> --max_episode <number of episodes> --scenario <your desired scenario file located in Shared/Scenarios>
```

## Supporting more actions

📗 Please follow the workflow in `MininetAdapter.step()` to support a new action.

Let's take `Impact` Action as an example,

First, make sure you understand the action string spitted out from Agents. In this case, it could be `Impact Op_Server0`.
`MininetAdapter.parse_action_string(action_string)` will parse this into `Op_Server0`, `IP ADDRESS OF Op_Server0`, `Impact`

Then, you should update `BlueActionTranslator` class or `RedActionTranslator` class. The goal is to translate the action string (Here it would be `IP ADDRESS OF Op_Server0` and `Impact`) into a bash command that will be sent to `mininet cli`

There are two things to look after when updating  `BlueActionTranslator` class or `RedActionTranslator` class in `action_translator.py`, 

1. Implement the translation function
```python3
# One could decide its own method signature 
def impact(self, target_host: str) -> str:
  action_string = ""
  # Translation happens here ...
  return action_string
```
2. Register your action translation function into the member field `action_map`
```python3
self.action_map = {
  ...
  "Impact": self.impact
}
```

>But what exactly should be in the `impact` function?

- I would recommend creating a new folder in `Mininet/Actions`, let's call it `Impact/`.
  Write a bash script that runs inside the Mininet process. Be aware that this process runs as `root` user ❗️

After doing so, think about what the observation should look like. Please take a look at `results_bundler.py` and its utility functions.  

Remember to think about the side effects caused by this action, it could affect the member fields in `MininetAdapter` class such as 
```python3
self.md5: Dict[str, dict] = {}
self.connection_key: Dict = {}
self.used_ports: Dict = {}
self.exploited_hosts: List = []
self.priviledged_hosts: List = []
self.old_exploit_outcome: Dict = {}
self.network_state: Dict = {}
self.available_ports: List = random.sample(range(4000, 5000 + 1), 50)
```

Finally, write an integration test to test your idea!

## To-Do

1. Continue to monitor and sync with the new implementations in `wrapper` branch, such as the newly updated `Impact` Action implementation.

2. Use Docker containers as hosts within Mininet. [Containernet](https://containernet.github.io/)

## Presentation slides for DESTION 2024 on May 13th, 2024

[Google Slides](https://docs.google.com/presentation/d/1f2pZ5q3p6cZK4m2dvq1Tvgj8ODyTyWGp3OVP4xXuaOw/edit?usp=sharing) \
[Paper Link](https://www.computer.org/csdl/proceedings-article/destion/2024/759400a028/1Y42Ek9NEsg)

