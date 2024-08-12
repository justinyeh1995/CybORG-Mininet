import argparse
import inspect
from CybORG import CybORG

from CybORG.Emulator.Actions.Velociraptor.PrivilegeEscalateActionForMininet import PrivilegeEscalateAction
from CybORG.Emulator.Actions.Velociraptor.ExploitActionForMininet import ExploitAction


path = str(inspect.getfile(CybORG))
path = path[:-10]
credentials_file = f"{path}/Mininet/actions/prog_client.yaml"  # @To-Do make it configurable
hostname="cpswtjustin"
remote_hostname="10.0.112.2"
remote_username="root"
remote_password="1234"
client_port=4322

exploit_action= ExploitAction(credentials_file,hostname,remote_hostname,remote_username,remote_password,client_port)
observation=exploit_action.execute(None)
print("Connection Key is:",observation.connection_key)
conn_key= observation.connection_key

pes_action=PrivilegeEscalateAction(credentials_file,hostname,conn_key,remote_hostname,remote_username,remote_password,client_port)

observation=pes_action.execute(None)
print("Success is:",observation.success)
print("Current User?:",observation.user)
print("Any new host explored?:",observation.explored_host)
print("PID of malicious process?",observation.pid)
print('!!Please clean the mess after test!!')

print('!! Cleaning mess, just for this testing, in real action cleaning need to be done by Blue Agent!!')
cleaned= pes_action.run_command("CLOSE")
print('!!cleaned and connection',cleaned,'!!')
