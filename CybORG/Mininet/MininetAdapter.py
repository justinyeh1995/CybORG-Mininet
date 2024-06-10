from pprint import pprint
import traceback 
from typing import List, Dict
import configparser # for configuration parsing
import inspect

from CybORG import CybORG, CYBORG_VERSION

from CybORG.Shared import Observation

from CybORG.Mininet.mininet_api.custom_utils import IP_components
from CybORG.Mininet.mininet_adapter import YamlTopologyManager, \
                                    MininetCommandInterface, \
                                    CybORGMininetMapper, \
                                    RedActionTranslator, BlueActionTranslator, \
                                    ResultsBundler, \
                                    RewardCalculator

class MininetAdapter:
    def __init__(self):
        self.path = str(inspect.getfile(CybORG))[:-10]
        
        config = configparser.ConfigParser ()
        config.read ('config.ini')

        self.topology_manager = YamlTopologyManager()
        self.command_interface = MininetCommandInterface()
        self.mapper = CybORGMininetMapper()
        self.blue_action_translator = BlueActionTranslator(path=self.path, 
                                                           config=config)
        self.red_action_translator = RedActionTranslator(path=self.path, 
                                                           config=config)
        self.results_bundler = ResultsBundler()
        
        self.reward_calculator = RewardCalculator(self.path + config["SCENARIO"]["FILE_PATH"])

    
    def set_environment(self, cyborg):
        # Setup based on cyborg environment...
        self.cyborg = cyborg
 

    def parse_action_string(self, action_string):
        print("--> in MininetAdapter parse_action_string")
        print(action_string)
        action_str_split = action_string.split(" ")
        action_type = action_str_split[0]
        n = len(action_str_split)
        target_host = action_str_split[-1] if n > 1 else ""
        # Update target host if it's an IP address to get the hostname
        target_host = self.mapper.cyborg_ip_to_host_map.get(target_host, target_host)
                
        return self.mapper.cyborg_to_mininet_host_map.get(target_host, target_host), action_type 

    
    def reset(self):
        print("===Resetting===")
        self.clean()

        self.mapper.init_mapping(self.cyborg)

        # Create YAML topology file
        file_path = 'network_topology.yaml'
        # This involves updating topology data and mappings
        self.topology_manager.generate_topology_data(self.cyborg, self.mapper.cyborg_to_mininet_name_map)
        self.topology_manager.save_topology(file_path)
        
        # Start Mininet with the topology
        expect_text = self.command_interface.start_mininet(file_path)
        # pprint(expect_text)

        self.mapper.update_mapping(expect_text, self.topology_manager.topology_data)

        ##########################
        # Test if DNS is working #
        ##########################

        print("===Ping Test===")
        expect_text = self.command_interface.send_command('lan1h1 ping -c 1 google.com')
        print(expect_text)

    
    def step(self, action_string: str, agent_type: str) -> Observation:
        '''Performing emulation
           Translate CybORG action to Mininet command and send it
           Retrieve the results and create observations
        '''
        print(f"---> in MininetAdapter {agent_type} step")
        target, cyborg_action = self.parse_action_string(action_string)
        isSuccess = True # Always True man..
        
        if agent_type == "Blue":
            mininet_command = self.blue_action_translator.translate(cyborg_action, 
                                                                target, 
                                                                self.mapper.cyborg_to_mininet_host_map,
                                                                self.mapper.mininet_host_to_ip_map)  
        elif agent_type == "Red":
            mininet_command = self.red_action_translator.translate(cyborg_action, 
                                                                target,
                                                                self.mapper.cyborg_to_mininet_host_map,
                                                                self.mapper.mininet_host_to_ip_map)

        mininet_cli_text = self.command_interface.send_command(mininet_command)
        
        print("===Mininet Cli Text====")
        print(mininet_cli_text)
        
        mininet_obs = self.results_bundler.bundle(target, cyborg_action, isSuccess, mininet_cli_text, self.mapper)
        
        print("===Obs===")
        pprint(mininet_obs.data)

        reward = self.reward_calculator.reward(mininet_obs.data, self.mapper)

        print("===Rewards===")
        print(reward)
        print("*********")

        return mininet_obs, reward

    
    def clean(self):
        self.command_interface.clean()

if __name__ == "__main__":
    print("Hello Mininet Adapter!")

