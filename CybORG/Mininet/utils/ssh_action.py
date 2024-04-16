import argparse
from CybORG.Emulator.Actions.SshAction import SshAction

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
    
    ip = parsed_args.ip
    sshAction = SshAction(parsed_args.ip, "root", "1234", 22)
    #sshAction = SshAction("172.17.0.3", "sftp_user", "art54")
    
    observation = sshAction.execute(None)

    print(observation)
    print(f"Token: {observation.token}")
    print(f"Available Exploit: {observation.available_exploit}")
    print(f"Local Socket Info: {observation.local_socket_info}")
    print(f"Remote Socket Info: {observation.remote_socket_info}")
    print(f"PID: {observation.pid}")
    
    print("foo")