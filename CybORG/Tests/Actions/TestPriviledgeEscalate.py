from CybORG.Emulator.Actions.Velociraptor.PrivilegeEscalateAction import PrivilegeEscalateAction
from CybORG.Emulator.Actions.Velociraptor.ExploitAction import ExploitAction


credentials_file = "prog_client2.yaml"
hostname="user-host-1"
remote_hostname="10.10.10.13"
remote_username="vagrant"
remote_password="vagrant"
client_port=4444


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
