import argparse

from CybORG.Emulator.Actions.Velociraptor.RemoveAction import RemoveAction

def parseCmdLineArgs ():
    # parse the command line
    parser = argparse.ArgumentParser ()

    # add optional arguments
    # parser.add_argument ("-ip", "--ip", default="0.0.0.0", help="IP Address")
    parser.add_argument ("-host", "--hostname", default="cpswtjustin", help="Hostname, use hostname to figure out hostname")
    parser.add_argument ("-conn_key", "--conn_key", default="cpswtjustin", help="connection_key from exploit action")

    # parse the args
    args = parser.parse_args ()

    return args

if __name__ == "__main__":
  
    parsed_args = parseCmdLineArgs ()
    
    # ip = parsed_args.ip
    hostname = parsed_args.hostname
    conn_key = parsed_args.conn_key

    credentials_file = "/home/ubuntu/justinyeh1995/CASTLEGym/CybORG/CybORG/Mininet/actions/prog_client.yaml"

    remove_action = RemoveAction(credentials_file, hostname, conn_key)

    observation=remove_action.execute(None)

    print('Malicious file removed?:',observation.malicious_file_removed)
    print('Connection Terminated?:',observation.connection_removed)