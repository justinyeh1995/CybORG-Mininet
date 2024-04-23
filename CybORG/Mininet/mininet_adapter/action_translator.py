import traceback 

from CybORG.Emulator.Actions.Velociraptor.DiscoverNetworkServicesAction import DiscoverNetworkServicesAction
from CybORG.Emulator.Actions.Velociraptor.DiscoverRemoteSystemsAction import DiscoverRemoteSystemsAction
from CybORG.Emulator.Actions.SshAction import SshAction
from CybORG.Emulator.Actions.DeployDecoyAction import DeployDecoy

from pprint import pprint

class ActionTranslator:
    def __init__(self, path: str, config):
        self.path = path
        self.python_exe = config["PYTHON"]["FILE_PATH"]
        self.action_folder_path = self.path + config["ACTION"]["FOLDER_PATH"]

    def translate(self, action):
        raise NotImplementedError


class RedActionTranslator(ActionTranslator):
    def __init__(self, path: str, config):
        super().__init__(path, config)  # Correctly calls the __init__ method of ActionTranslator
        self.action_map = {
            "DiscoverRemoteSystems": self.discover_remote_systems,
            "DiscoverNetworkServices": self.discover_network_services,
            "ExploitRemoteService": self.exploit_remote_service,
            "PrivilegeEscalate": self.privilege_escalate
        }

    def translate(self, action_type, target_host, cyborg_to_mininet_host_map, mininet_host_to_ip_map) -> str:
        action_method = self.action_map.get(action_type)
        if action_method:
            return action_method(target_host, cyborg_to_mininet_host_map, mininet_host_to_ip_map)
        else:
            print("Not Implemented Action...\nSleep for a sec")
            return "sleep 1"

    def discover_remote_systems(self, target_host, cyborg_to_mininet_host_map, mininet_host_to_ip_map):
        print("Red Discover Remote Systems")
        host = cyborg_to_mininet_host_map['User0']
        action = "nmap -sn"
        target = target_host
        return f'{host} timeout 60 {action} {target}'

    def discover_network_services(self, target_host, cyborg_to_mininet_host_map, mininet_host_to_ip_map):
        print("Red Discover Network Services")
        host = cyborg_to_mininet_host_map['User0']
        action = "nmap -sV"
        target = target_host
        return f'{host} timeout 60 {action} {target}'

    def exploit_remote_service(self, target_host, cyborg_to_mininet_host_map, mininet_host_to_ip_map):
        print("Red Exploit Network Services")
        host = cyborg_to_mininet_host_map['User0']
        action = f"{self.python_exe} {self.action_folder_path}/ssh_action.py --ip"
        target = mininet_host_to_ip_map.get(target_host, cyborg_to_mininet_host_map['User0'])
        return f'{host} timeout 60 {action} {target}'

    def privilege_escalate(self, target_host, cyborg_to_mininet_host_map, mininet_host_to_ip_map):
        print("Red Privilege Escalate")
        # @To-Do Not Implemented as of now
        return "sleep 1"


class BlueActionTranslator(ActionTranslator):
    def __init__(self, path: str, config):
        super().__init__(path, config)  # Correctly calls the __init__ method of ActionTranslator
        self.decoy_service_name_to_port = {
            'DecoyApache': 80, 
            'DecoySSHD': 22, 
            'DecoyVsftpd': 21, 
            'DecoyFemitter': 21, 
            'DecoyTomcat': 443, 
            'DecoyHarakaSMPT': 25
        }
        
        self.action_map = {
            "Remove": self.remove,
            "Restore": self.restore,
            "Monitor": self.monitor,
            "Decoy": self.deploy_decoy
        }

    def translate(self, action_type, target_host, cyborg_to_mininet_host_map, mininet_host_to_ip_map) -> str:
        if action_type.startswith("Decoy"):
            action_type = "Decoy"
        action_method = self.action_map.get(action_type) # @To-Do slick logic here, needs to be better
        if action_method:
            return action_method(action_type, target_host, cyborg_to_mininet_host_map, mininet_host_to_ip_map)
        else:
            print("Not Implemented Action...\nSleep for a sec")
            return "sleep 1"

    def remove(self, action_type, target_host, cyborg_to_mininet_host_map, mininet_host_to_ip_map):
        print("Blue Remove")
        # @To-Do Not Implemented as of now
        return "sleep 1"

    def restore(self, action_type, target_host, cyborg_to_mininet_host_map, mininet_host_to_ip_map):
        print("Blue Restore")
        # @To-Do Not Implemented as of now
        return "sleep 1"

    def monitor(self, action_type, target_host, cyborg_to_mininet_host_map, mininet_host_to_ip_map):
        print("Blue Monitor")
        # @To-Do Not Implemented as of now
        return "sleep 1"

    def deploy_decoy(self, action_type, target_host, cyborg_to_mininet_host_map, mininet_host_to_ip_map):
        print("Blue Decoy")
        host = cyborg_to_mininet_host_map['Defender']
        action = f"{self.python_exe} {self.action_folder_path}/deploy_decoy_action.py --ip"
        target = mininet_host_to_ip_map.get(target_host, cyborg_to_mininet_host_map['User0'])
        port = self.decoy_service_name_to_port.get(action_type, 80)
        return f"{host} {action} {target} --port {port}"