import argparse
import inspect
from CybORG import CybORG

from CybORG.Emulator.Actions.Velociraptor.SSHConnectionServerAction import SSHConnectionServerAction
from CybORG.Emulator.Actions.Velociraptor.SSHConnectionImpactAction import SSHConnectionImpactAction
from CybORG.Emulator.Actions.Velociraptor.PrivilegeEscalateActionForMininet import PrivilegeEscalateAction
from CybORG.Emulator.Observations.Velociraptor.PrivilegeEscalateObservation import PrivilegeEscalateObservation

def parseCmdLineArgs ():
    # parse the command line
    parser = argparse.ArgumentParser ()

    # add optional arguments
    # parser.add_argument ("-ip", "--ip", default="0.0.0.0", help="IP Address")
    parser.add_argument ("-host", "--hostname", default="cpswtjustin", help="Hostname, use hostname to figure out hostname")
    parser.add_argument ("-remote", "--remote_hostname", default="0.0.0.0", help="Remote IP Address")
    parser.add_argument ("-conn_key", "--conn_key", default="", help="The connection key from the exploit action")
    parser.add_argument ("-client_port", "--client_port", default=4444, help="The client port used for the ssh session in previous exploit action" )
    
    # parse the args
    args = parser.parse_args ()

    return args

if __name__ == "__main__":
  
    parsed_args = parseCmdLineArgs ()
    
    hostname = parsed_args.hostname
    remote_hostname = parsed_args.remote_hostname    
    remote_username ="root"
    remote_password ="1234"
    conn_key = parsed_args.conn_key
    client_port = parsed_args.client_port
    
    print(f"Attacker Hostname: {hostname}")
    print(f"Remote IP: {remote_hostname}")
    print(f"Connection Key is: {conn_key}")

    path = str(inspect.getfile(CybORG))
    path = path[:-10]
    credentials_file = f"{path}/Mininet/actions/prog_client.yaml"  # @To-Do make it configurable

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
