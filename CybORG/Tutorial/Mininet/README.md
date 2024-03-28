## Mininet Adapter 

`mininet_utils` contains the Mininet API (in python) that is responsible for generating the topology. Any prerequisite configuration such as starting SSH servers automatically once the topology created is done at `custom_lan.py`, the routing rules are configured at `custom_topo.py`

`mininet_adapter` contains the middleware that binds Mininet API and CybORG API.

`MininetAdapter.py` is the main class that runs the `mininet_adapter` logic. Should be placed along with your CybORG object.

`Tests` covered `mininet_adapter` (on going work)

`main.py` is the standalone program that runs the experiment.