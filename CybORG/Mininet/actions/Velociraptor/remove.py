import argparse
import inspect
from CybORG import CybORG

from CybORG.Emulator.Actions.Velociraptor.RemoveActionForMininet import RemoveAction

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
    credentials_file = f"{path}/Mininet/actions/prog_client.yaml"  # @To-Do make it configurable

    remove_action = RemoveAction(credentials_file, hostname, conn_key)

    observation=remove_action.execute(None)
    
    print("Success?:", observation.success)

    print('Malicious file removed?:',observation.malicious_file_removed)
    print('Connection Terminated?:',observation.connection_removed)