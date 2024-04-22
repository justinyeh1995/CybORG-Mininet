## Gather Actions & Observations

```python
"""
<red/blue>_action: str 
"""
"DiscoverRemoteSysyems x.x.x.x/yy"
"""
<red/blue>_observation: dict
"""
{'success': <TrinaryEnum.UNKNOWN: 2>}

"""
actions = {"Red": red_action, "Blue": blue_action}
"""
{'Blue': 'Sleep', 'Red': 'ExploitRemoteService 10.0.190.38'}
"""
observations = {"Red": red_observation, "Blue": blue_observation}
"""
{'Blue': {'success': <TrinaryEnum.UNKNOWN: 2>},
 'Red': {'10.0.162.119': {'Interface': [{'IP Address': IPv4Address('10.0.162.119')}],
                          'Processes': [{'Connections': [{'local_address': IPv4Address('10.0.162.119'),
                                                          'local_port': 4444,
                                                          'remote_address': IPv4Address('10.0.190.38'),
                                                          'remote_port': 59658}],
                                         'Process Type': <ProcessType.REVERSE_SESSION_HANDLER: 10>}]},
         '10.0.190.38': {'Interface': [{'IP Address': IPv4Address('10.0.190.38')}],
                         'Processes': [{'Connections': [{'Status': <ProcessState.OPEN: 2>,
                                                         'local_address': IPv4Address('10.0.190.38'),
                                                         'local_port': 443}],
                                        'Process Type': <ProcessType.WEBSERVER: 7>},
                                       {'Connections': [{'local_address': IPv4Address('10.0.190.38'),
                                                         'local_port': 59658,
                                                         'remote_address': IPv4Address('10.0.162.119'),
                                                         'remote_port': 4444}],
                                        'Process Type': <ProcessType.REVERSE_SESSION: 11>}],
                         'Sessions': [{'Agent': 'Red',
                                       'ID': 2,
                                       'Type': <SessionType.RED_REVERSE_SHELL: 11>}],
                         'System info': {'Hostname': 'Enterprise1',
                                         'OSType': <OperatingSystemType.LINUX: 3>}},
         'success': <TrinaryEnum.TRUE: 1>}}
```

create a state_snapshot of the current step

```python
state_snapshot = game_state_manager.create_state_snapshot(actions, observations)
```

store state_snapshot of the current step
```python
"""
i is the current episode number
j is the current step number

your for loop should taken care of this
"""

game_state_manager.store_state(state_snapshot, i, j)
```


