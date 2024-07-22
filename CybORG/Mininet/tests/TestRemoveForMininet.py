import argparse
import inspect
from CybORG import CybORG

from CybORG.Emulator.Actions.Velociraptor.RemoveActionForMininet import RemoveAction
from CybORG.Emulator.Actions.Velociraptor.ExploitActionForMininet import ExploitAction


path = str(inspect.getfile(CybORG))
path = path[:-10]
credentials_file = f"{path}/Mininet/actions/prog_client.yaml"  # @To-Do make it configurable
hostname="cpswtjustin"
remote_hostname="10.0.112.13"
remote_username="root"
remote_password="1234"
client_port=4321


exploit_action= ExploitAction(credentials_file,hostname,remote_hostname,remote_username,remote_password,client_port)
observation=exploit_action.execute(None)
print("Connection Key is:",observation.connection_key)
conn_key= observation.connection_key


remove_action = RemoveAction(credentials_file,hostname,conn_key)

observation=remove_action.execute(None)

print('Malicious file removed?:',observation.malicious_file_removed)
print('Connection Terminated?:',observation.connection_removed)
