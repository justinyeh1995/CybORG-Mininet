import traceback 
import socket
import json
import base64

from CybORG.Mininet.AdapterComponents.entity import Entity


class ActionTranslator(Entity):
    """_summary_
    Bascially this class is used to translate the actions from CybORG to Mininet, this is the parent class for the Red and Blue Team's action translator
    It defines the common methods and attributes that the Red and Blue Team's action translator will have
    It is a child class of the Entity class
    It has a reset action string method that is used to reset the environment 
    Args:
        Entity (_type_): _description_
    """
    def __init__(self, path: str, config, logger):
        self.logger = logger
        self.path = path
        self.last_action: str = None
        self.last_target: str = None
        self.hostname = socket.gethostname()
        self.python_exe_filepath = config["PYTHON"]["FILE_PATH"]
        self.action_folder_path = self.path + config["ACTION"]["FOLDER_PATH"]
        self.sys_script = self.path + config["ACTION"]["SYS_SCRIPT_PATH"]
        self.velociraptor_server_mininet_hostname = None

    def translate(self, action):
        raise NotImplementedError
    
    def get_reset_action_string(self, target_host, cyborg_to_mininet_host_map, mininet_host_to_ip_map):
        # action = f"{self.python_exe_filepath} {self.action_folder_path}/Velociraptor/reset.py"
        action = f"bash {self.action_folder_path}/ResetAction/reset.sh"
        return f'{cyborg_to_mininet_host_map["Defender"]} {action} --mininet_hostname "{target_host}" --python-path \'{self.python_exe_filepath}\' --action-folder \'{self.action_folder_path}\'' 


class RedActionTranslator(ActionTranslator):
    """_summary_
    Bascially this class is used to translate the actions from CybORG to Mininet, this is the Red Team's action translator
    You can think of this as a string builder for the actions that the Red Team will take in the Mininet environment
    Args:
        ActionTranslator (_type_): _description_
    """
    def __init__(self, path: str, config, logger):
        super().__init__(path, config, logger)  # Correctly calls the __init__ method of ActionTranslator
        self.action_map = {
            "DiscoverRemoteSystems": self.discover_remote_systems,
            "DiscoverNetworkServices": self.discover_network_services,
            "ExploitRemoteService": self.exploit_remote_service,
            "PrivilegeEscalate": self.privilege_escalate
        }

    def translate(self, action_type, target_host, cyborg_to_mininet_host_map, mininet_host_to_ip_map) -> str:
        self.last_action = action_type
        self.last_target = mininet_host_to_ip_map.get(target_host, "")
        action_method = self.action_map.get(action_type)
        if action_method:
            return action_method(target_host, cyborg_to_mininet_host_map, mininet_host_to_ip_map)
        else:
            print("Not Implemented Action...\nSleep for a sec")
            self.logger.debug(f"Action is {action_method}")
            return "sleep 1"

    def discover_remote_systems(self, target_host, cyborg_to_mininet_host_map, mininet_host_to_ip_map):
        print("Red Discover Remote Systems")
        host = cyborg_to_mininet_host_map['User0']
        action = "nmap -oX - -sn"
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
        hostname = socket.gethostname()
        
        # Serialize additional data
        additional_data = {
            'available_ports': self.mininet_adpator.available_ports
        }
        json_str = json.dumps(additional_data)
        base64_data = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
        
        # action = f"{self.python_exe_filepath} {self.action_folder_path}/Velociraptor/exploit_action.py"
        action = f"{self.action_folder_path}/ExploitAction/exploit.sh"

        target = mininet_host_to_ip_map.get(target_host, cyborg_to_mininet_host_map['User0'])
        
        return f'{host} bash {action} -m {target} -data {base64_data} --python-path \'{self.python_exe_filepath}\' --action-folder \'{self.action_folder_path}\' --sys-script \'{self.sys_script}\''

    def privilege_escalate(self, target_host, cyborg_to_mininet_host_map, mininet_host_to_ip_map):
        print("Red Privilege Escalate")
        host = cyborg_to_mininet_host_map['User0']
        # action = f"{self.python_exe_filepath} {self.action_folder_path}/Velociraptor/privilege_action.py"
        action = f"bash {self.action_folder_path}/PrivilegeEscalateAction/privilege.sh"
        target = mininet_host_to_ip_map.get(target_host, cyborg_to_mininet_host_map['User0'])
        conn_key = self.mininet_adpator.connection_key[target]
        
        return f'{host} {action} -m {target} --conn_key {conn_key}' # This might take a while to run so we take out the timeout as a temporary solution
    
    def impact(self, target_host):
        print("Red Impact")
        # @To-Do Not Implemented as of now
        return "bash sleep 1"


class BlueActionTranslator(ActionTranslator):
    """_summary_
    Bascially this class is used to translate the actions from CybORG to Mininet, this is the Blue Team's action translator
    You can think of this as a string builder for the actions that the Blue Team will take in the Mininet environment
    Args:
        ActionTranslator (_type_): _description_
    """
    def __init__(self, path: str, config, logger):
        super().__init__(path, config, logger)  # Correctly calls the __init__ method of ActionTranslator
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
            "Decoy": self.deploy_decoy,
            "Analyse": self.analyse,
            "Sleep": self.sleep,
            "Monitor": self.monitor,
        }

    def translate(self, action_type, target_host, cyborg_to_mininet_host_map, mininet_host_to_ip_map) -> str:
        if action_type.startswith("Decoy"):
            action_method = self.action_map.get("Decoy")
        else:
            action_method = self.action_map.get(action_type) # @To-Do slick logic here, needs to be better
        
        if action_method:
            return action_method(action_type, target_host, cyborg_to_mininet_host_map, mininet_host_to_ip_map)
        else:
            print("Not Implemented Action...\nSleep for a sec")
            return "sleep 1"

    def remove(self, action_type, target_host, cyborg_to_mininet_host_map, mininet_host_to_ip_map):
        print("Blue Remove")
        # @To-Do Not Implemented as of now
        host = cyborg_to_mininet_host_map['Defender']
        # action = f"{self.python_exe_filepath} {self.action_folder_path}/Velociraptor/remove.py"
        action = f"bash {self.action_folder_path}/RemoveAction/remove.sh"        
        
        target = mininet_host_to_ip_map.get(target_host, cyborg_to_mininet_host_map['User0'])
        conn_key = self.mininet_adpator.connection_key.get(target)
        
        # return f"{host} {action} --hostname {self.hostname} --conn_key {conn_key}"
        return f"{host} {action} -n {conn_key}"

    def restore(self, action_type, target_host, cyborg_to_mininet_host_map, mininet_host_to_ip_map):
        print("Blue Restore")
        # @To-Do Not Implemented as of now
        return "bash sleep 1"

    def monitor(self, action_type, target_host, cyborg_to_mininet_host_map, mininet_host_to_ip_map):
        print("Blue Monitor")
        # @To-Do Not Implemented as of now
        return "bash sleep 1"
    
    def sleep(self, action_type, target_host, cyborg_to_mininet_host_map, mininet_host_to_ip_map):
        host = cyborg_to_mininet_host_map['Defender']
        return f" {host} sleep 1"

    def deploy_decoy(self, action_type, target_host, cyborg_to_mininet_host_map, mininet_host_to_ip_map):
        print("Blue Decoy")
        host = cyborg_to_mininet_host_map['Defender']
        action = f"{self.python_exe_filepath} {self.action_folder_path}/DecoyAction/deploy_decoy_action.py"
        target = mininet_host_to_ip_map.get(target_host, cyborg_to_mininet_host_map['User0'])
        port = self.decoy_service_name_to_port.get(action_type, 80)
        cyborg_hostname = self.mininet_adpator.mapper.cyborg_ip_to_host_map.get(target)
        decoyname = action_type[5:]
        return f"{host} {action} --ip {target} --port {port} --decoyname {decoyname} --cyborg_hostname {cyborg_hostname}"
    
    def analyse(self, action_type, target_host, cyborg_to_mininet_host_map, mininet_host_to_ip_map):
        host = cyborg_to_mininet_host_map['Defender']
        # action  = f"{self.python_exe_filepath} {self.action_folder_path}/Velociraptor/analyse.py"
        action = f"bash {self.action_folder_path}/AnalyseAction/analyse.sh"
        
        hostname = socket.gethostname()
        # Serialize additional data
        
        target = self.mininet_adpator.mapper.mininet_to_cyborg_host_map.get(target_host)
        additional_data = self.mininet_adpator.md5.get(target, {})
        json_str = json.dumps(additional_data)
        base64_data = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
        # @To-Do lan1h4 velociraptor server is not correctly setup and is expected cause the config file specify the ip already
        return f'{host} {action} --mininet_hostname \'{target_host}\' --additional_data {base64_data} --python-path \'{self.python_exe_filepath}\' --action-folder \'{self.action_folder_path}\'' 
