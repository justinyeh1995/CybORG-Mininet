import argparse
from CybORG.Emulator.Actions.DeployDecoyAction import DeployDecoy

def parseCmdLineArgs ():
    # parse the command line
    parser = argparse.ArgumentParser ()

    # add optional arguments
    parser.add_argument ("-ip", "--ip", default="0.0.0.0", help="IP Address")

    # parse the args
    args = parser.parse_args ()

    return args

if __name__ == "__main__":

    parsed_args = parseCmdLineArgs ()
    
    deploy_decoy = DeployDecoy(parsed_args.ip, 'root', '1234', 'apache', 80)
    
    observation = deploy_decoy.execute(None)

    print(observation)

    print("foo")