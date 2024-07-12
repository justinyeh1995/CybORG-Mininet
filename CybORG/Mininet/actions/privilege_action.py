import argparse

from CybORG.Emulator.Actions.Velociraptor.SSHConnectionServerAction import SSHConnectionServerAction
from CybORG.Emulator.Actions.Velociraptor.SSHConnectionImpactAction import SSHConnectionImpactAction
from CybORG.Emulator.Observations.Velociraptor.PrivilegeEscalateObservation import PrivilegeEscalateObservation

def parseCmdLineArgs ():
    # parse the command line
    parser = argparse.ArgumentParser ()

    # add optional arguments
    # parser.add_argument ("-ip", "--ip", default="0.0.0.0", help="IP Address")
    parser.add_argument ("-host", "--hostname", default="cpswtjustin", help="Hostname, use hostname to figure out hostname")
    parser.add_argument ("-remote", "--remote", default="0.0.0.0", help="Remote IP Address")

    # parse the args
    args = parser.parse_args ()

    return args

if __name__ == "__main__":
  
    parsed_args = parseCmdLineArgs ()
    
    # ip = parsed_args.ip
    hostname = parsed_args.hostname
    remote_ip = parsed_args.remote
    
    # print(f"At IP Address: {ip}")
    print(f"Attacker Hostname: {hostname}")
    print(f"Remote IP: {remote_ip}")

    credentials_file = "/home/ubuntu/justinyeh1995/CASTLEGym/CybORG/CybORG/Mininet/actions/prog_client.yaml"  # @To-Do make it configurable

    ssh_connection_server_action = SSHConnectionServerAction(
        credentials_file=credentials_file,
        hostname=hostname,
        remote_hostname=remote_ip,
        remote_username="root", # 'velociraptor'
        remote_password="1234",
        client_port=4444
    )
    
    ssh_connection_server_observation = ssh_connection_server_action.execute(None)
    
    ssh_connection_client_action_gain_root_access = SSHConnectionImpactAction(
        credentials_file=credentials_file,
        hostname=hostname,
        connection_key=ssh_connection_server_observation.connection_key,
        command="sudo su -"
    )
    
    ssh_connection_client_observation_2 = ssh_connection_client_action_gain_root_access.execute(None)
    
    ssh_connection_client_action_3 = SSHConnectionImpactAction(
        credentials_file=credentials_file,
        hostname=hostname,
        connection_key=ssh_connection_server_observation.connection_key,
        command="CLOSE"
    )
    
    # ssh_connection_client_observation_3 = ssh_connection_client_action_3.execute(None)
    print(ssh_connection_client_observation_2.data)
    print("foo")