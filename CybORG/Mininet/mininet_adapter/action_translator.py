import traceback 
import inspect
from CybORG import CybORG, CYBORG_VERSION
from CybORG.Emulator.Actions.Velociraptor.DiscoverNetworkServicesAction import DiscoverNetworkServicesAction
from CybORG.Emulator.Actions.Velociraptor.DiscoverRemoteSystemsAction import DiscoverRemoteSystemsAction
from CybORG.Emulator.Actions.SshAction import SshAction
from CybORG.Emulator.Actions.DeployDecoyAction import DeployDecoy

from pprint import pprint

class ActionTranslator:
    def __init__(self):
        self.path = str(inspect.getfile(CybORG))[:-7]

    def translate(self, action):
        raise NotImplementedError


class RedActionTranslator(ActionTranslator):
    def __init__(self):
        super().__init__()  # Correctly calls the __init__ method of ActionTranslator
        
    def translate(self, action_type, target_host, cyborg_to_mininet_host_map, mininet_host_to_ip_map) -> str:
        host = cyborg_to_mininet_host_map['User0'] # red host is always user0
        timeout = 60
        # @To-Do code smells
        if action_type == "DiscoverRemoteSystems":
            print("Red Discover Remote Systems")
            action = "nmap -sn"
            target = target_host
        elif action_type == "DiscoverNetworkServices":
            print("Red Discover Network Services")
            action = "nmap -sV"
            target = target_host
        elif action_type == "ExploitRemoteService":
            print("Red Exploit Network Services")
            action = f"/home/ubuntu/justinyeh1995/CASTLEGym/CybORG/castle.new.venv/bin/python3 {self.path}/Mininet/utils/ssh_action.py --ip" # @To-Do needs to be configurable in the future
            target = mininet_host_to_ip_map.get(target_host, cyborg_to_mininet_host_map['User0'])
        elif action_type == "PrivilegeEscalate":
            print("Red Privilege Escalate")
            # @To-Do Not Implemented as of now
        else:
            action = "sleep 1" # dummy
            target = "" # dummy
            
        cmd = f'{host} timeout {timeout} {action} {target}'
        
        return cmd


class BlueActionTranslator(ActionTranslator):
    def __init__(self):
        super().__init__()  # Correctly calls the __init__ method of ActionTranslator
        self.decoy_bin_path = self.path + f'/Emulator/Velociraptor/Executables/Decoy'
        self.decoy_service_name_to_port = {
            'DecoyApache': 80, 
            'DecoySSHD': 22, 
            'DecoyVsftpd': 21, 
            'DecoyFemitter': 21, 
            'DecoyTomcat': 443, 
            'DecoyHarakaSMPT': 25
        }
        
    def translate(self, action_type, target_host, cyborg_to_mininet_host_map, mininet_host_to_ip_map) -> str:
        host = cyborg_to_mininet_host_map['Defender'] # red host is always user0
        timeout = 60
        # @To-Do code smells
        # blue host is undecided at the moment
        cmd = 'lan1h1 ping -c 1 lan2h2'
        if action_type == "Remove":
            print("Blue Remove")
        elif action_type == "Restore":
            print("Blue Restore")
        elif action_type == "Monitor":
            print("Blue Monitor")
        elif action_type.startswith("Decoy"):
            print("Blue Decoy")
            action = f"/home/ubuntu/justinyeh1995/CASTLEGym/CybORG/castle.new.venv/bin/python3 {self.path}/Mininet/utils/deploy_decoy_action.py --ip" # @To-Do needs to be configurable in the future
            target = mininet_host_to_ip_map.get(target_host, cyborg_to_mininet_host_map['User0'])
            port = self.decoy_service_name_to_port.get(action_type, 80
            cmd = f"{host} echo 'nameserver 8.8.8.8' >> /etc/resolv.conf && timeout {timeout} {action} {target} --port {port}"
        return cmd
