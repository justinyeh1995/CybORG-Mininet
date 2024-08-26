import argparse
import inspect
import json
from pathlib import Path
from CybORG import CybORG

def parseCmdLineArgs ():
    # parse the command line
    parser = argparse.ArgumentParser ()

    # add optional arguments
    # parser.add_argument ("-ip", "--ip", default="0.0.0.0", help="IP Address")
    parser.add_argument ("-m", "--remote_hostname", default="0.0.0.0", help="Remote IP Address")
    parser.add_argument ("-conn_key", "--conn_key", default="", help="The connection key from the exploit action")
    
    # parse the args
    args = parser.parse_args ()

    return args

if __name__ == "__main__":
    parsed_args = parseCmdLineArgs ()
    
    remote_hostname = parsed_args.remote_hostname    
    conn_key = parsed_args.conn_key
    
    ssh_known_hosts_map_json_file = Path('/', 'tmp', '.ssh', 'known_hosts.json')
    if not ssh_known_hosts_map_json_file.exists():
        raise FileNotFoundError(f"File {ssh_known_hosts_map_json_file} does not exist...")
    
    with open('/tmp/.ssh/known_hosts.json', 'r') as f:
        ssh_known_hosts_map = json.load(f)
        
    file_path = ssh_known_hosts_map.get(remote_hostname, '~/.ssh/known_hosts')
    
    print(f"{conn_key},{remote_hostname},{file_path}")
    

    
