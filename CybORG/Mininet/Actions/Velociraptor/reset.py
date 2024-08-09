import json
import argparse
import inspect

from CybORG import CybORG
from CybORG.Emulator.Actions.Velociraptor.ResetAction import ResetAction

def parseCmdLineArgs ():
    # parse the command line
    parser = argparse.ArgumentParser ()

    # add optional arguments
    parser.add_argument ("-host", "--hostname", default="cpswtjustin", help="Hostname, use hostname to figure out hostname")
    parser.add_argument ("-mininet_hostname", "--mininet_hostname", type=str, default="lan3h1", help="Mininet Hostname")
    parser.add_argument ("-data", "--additional_data", help="Additional data as base64 encoded JSON string")
    # parse the args
    args = parser.parse_args ()

    return args

if __name__ == "__main__":
    parsed_args = parseCmdLineArgs ()
    
    hostname = parsed_args.hostname
    mininet_hostname = parsed_args.mininet_hostname
    
    path = str(inspect.getfile(CybORG))
    path = path[:-10]
    credentials_file = f"{path}/Mininet/actions/prog_client.yaml"  # @To-Do make it configurable
    
    reset_action = ResetAction(credentials_file)

    observation=reset_action.execute(hostname, directory=f'/tmp/{mininet_hostname}/ubuntu')
    print("observation is :",observation)
    print('Success is:',observation.success)
    print('md5 chksum are:',observation.md5)