import argparse
from CybORG.Emulator.Actions.DeployDecoyAction import DeployDecoy

def parseCmdLineArgs ():
    # parse the command line
    parser = argparse.ArgumentParser ()

    # add optional arguments
    parser.add_argument ("-ip", "--ip", default="0.0.0.0", help="IP Address")
    parser.add_argument ("-cyborg_hostname", "--cyborg_hostname", default="User3", help="Hostname")
    parser.add_argument ("-decoyname", "--decoyname", default='Apache', type=str, help="Decoy services")
    parser.add_argument ("-port", "--port", default=80, type=int, help="Port Number")


    # parse the args
    args = parser.parse_args ()

    return args

if __name__ == "__main__":

    parsed_args = parseCmdLineArgs ()
    
    deploy_decoy = DeployDecoy(parsed_args.ip, 'root', '1234', parsed_args.decoyname, parsed_args.port)
    
    observation = deploy_decoy.execute(None)

    print(observation)
    print("Decoied Service:", parsed_args.decoyname)
    print("Decoy Deployed IP:", parsed_args.ip)
    print("Decoy Deployed Hostname:", parsed_args.cyborg_hostname)
