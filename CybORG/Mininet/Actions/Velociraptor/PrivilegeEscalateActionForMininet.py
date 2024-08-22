from pathlib import Path
from typing import Union
from CybORG.Shared import Observation
from CybORG.Simulator.State import State
from CybORG.Emulator.Actions.Velociraptor.SSHConnectionImpactActionForMininet import SSHConnectionImpactAction
from CybORG.Emulator.Observations.Velociraptor.PrivilegeEscalateObservation import PrivilegeEscalateObservation


import json 

class PrivilegeEscalateAction: 
  
    def __init__(self, credentials_file,hostname, connection_key=None, remote_host_name=None,remote_username=None, remote_password=None,client_port=None):
        self.credentials_file=credentials_file
        self.conn_key=connection_key
        self.hostname = hostname
        self.remote_hostname=remote_host_name
        self.remote_username=remote_username
        self.remote_password=remote_password
        self.client_port= client_port

        ssh_known_hosts_map_json_file = Path('/', 'tmp', '.ssh', 'known_hosts.json')
        if not ssh_known_hosts_map_json_file.exists():
            raise FileNotFoundError(f"File {ssh_known_hosts_map_json_file} does not exist...")
       
        with open('/tmp/.ssh/known_hosts.json', 'r') as f:
            self.ssh_known_hosts_map = json.load(f)

    def run_command(self,command='CLOSE'):
       ssh_connection_client_action = SSHConnectionImpactAction(
           credentials_file=self.credentials_file,
           hostname=self.hostname,
           connection_key=self.conn_key,
           command=command
       )
       ssh_connection_client_observation = ssh_connection_client_action.execute(None)
       return ssh_connection_client_observation.Stdout

    def execute(self, state: Union[State, None]) -> Observation:
        if self.conn_key == None:
            return PrivilegeEscalateObservation(success=False)

        out1 = self.run_command("whoami")
        file_path = self.ssh_known_hosts_map.get(self.remote_hostname, '~/.ssh/known_hosts')
        out2 = self.run_command(f"grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' {file_path}") # @To-Do use a temp known_hosts file instead and see castle-vm to understand how know_hosts are set up 
        out3 = self.run_command(f"ss -tunap | grep ':{self.client_port}'") # @To-Do ask if this is appropriate!
        return PrivilegeEscalateObservation(success=True,user=out1,explored_host=out2,pid=out3)


if __name__=="__main__":
    credentials_file = "prog_client.yaml"
    connection_key = "FOOBAR"
    hostname = "user-host-1"
    remote_hostname = "10.10.10.13"
    remote_username = "vagrant"
    remote_password = "vagrant"
    client_port = 4444

    pes_action=PrivilegeEscalateAction(
        credentials_file, connection_key, hostname, remote_hostname, remote_username, remote_password, client_port
    )
   
    observation= pes_action.execute(None)
    print(observation.user,observation.explored_host,observation.pid)
    print('Please clean the mess by killing the SSHConnectionServer.py/SSHConnectionServerClient.py')

