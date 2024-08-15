import collections
from pathlib import Path
import re
from mininet.net import Mininet   #main network class


def generate_client_config_file(net: Mininet):
    for host in net.hosts:
        # Generate the client config file on each host
        if host.name.startswith('lan'):
            host.cmd(f'./velociraptor --config /etc/velociraptor/server.config.yaml config client > tmp/velociraptor/client_{host.name}.config.yaml')
            update_config_file(
                f'tmp/velociraptor/client_{host.name}.config.yaml',
                r'https://(\S+)(:\d+)',
                host.IP()
            )

def update_config_file(file_path, pattern, substitution):
    if not Path(file_path).exists():
    # Create the file if it does not exist
        print(f"Folder path: {Path(file_path).parent} does not exist, creating it")
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Use regex to replace localhost and port in api_connection_string
    updated_content = re.sub(
        pattern,
        substitution,
        content
    )
    
    with open(file_path, 'w') as file:
        file.write(updated_content)


def startVelociraptorClients( net):
    pids = collections.defaultdict(list)
    for host in net.hosts:
        if host.name.startswith('lan'):
            # Start the velociraptor client on each host
            net[host].cmd(f'velociraptor --config /tmp/velociraptor/client_{host.name}.config.yaml client -v > /dev/null 2>&1 &')

        # net[host].cmd('systemctl start velociraptor_server &')
        pid = net[host].cmd('echo $!')
        pids[host].append(pid)
    return pids