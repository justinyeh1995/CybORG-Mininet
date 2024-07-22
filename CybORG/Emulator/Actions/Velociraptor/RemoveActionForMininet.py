from typing import Union

from CybORG.Shared import Observation
from CybORG.Simulator.State import State

from CybORG.Emulator.Actions.Velociraptor.SSHConnectionImpactActionForMininet import SSHConnectionImpactAction

from CybORG.Emulator.Observations.Velociraptor.RemoveObservation import RemoveObservation

import argparse

import inspect
from CybORG import CybORG

class RemoveAction:
    def __init__(self, credentials_file,hostname,connection_key):
        self.credentials_file=credentials_file
        self.conn_key=connection_key
        self.hostname = hostname

    def run_command(self,command='CLOSE'):
        ssh_connection_client_action = SSHConnectionImpactAction(
            credentials_file=self.credentials_file,
            hostname=self.hostname,
            connection_key=self.conn_key,
            command=command
        )
        ssh_connection_client_observation = ssh_connection_client_action.execute(None)
       
        print("\n->OUTPUT from run_command =",ssh_connection_client_observation.Stdout)
        return ssh_connection_client_observation.Stdout

    def execute(self, state: Union[State, None]) -> Observation:
        out = self.run_command('rm cmd.sh && echo "Success" || echo "Failure"')
        out1 = self.run_command()
        return RemoveObservation(success=True,mal_file_removed=out,connection_removed=out1)

def parseCmdLineArgs ():
    # parse the command line
    parser = argparse.ArgumentParser ()

    # add optional arguments
    # parser.add_argument ("-ip", "--ip", default="0.0.0.0", help="IP Address")
    parser.add_argument ("-m", "--hostname", default="cpswtjustin", help="Hostname, use hostname to figure out hostname")
    parser.add_argument ("-n", "--conn_key", default="", help="connection_key from exploit action")

    # parse the args
    args = parser.parse_args ()

    return args

if __name__ == "__main__":
    parsed_args = parseCmdLineArgs ()
    
    # ip = parsed_args.ip
    hostname = parsed_args.hostname
    conn_key = parsed_args.conn_key

    path = str(inspect.getfile(CybORG))
    path = path[:-10]
    credentials_file = f"{path}/Mininet/actions/prog_client.yaml" 

    remove_action=RemoveAction(credentials_file,conn_key,hostname)
    remove_action.execute(None)
