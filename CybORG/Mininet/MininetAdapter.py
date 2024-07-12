from pprint import pprint
import traceback 
from typing import List, Dict
import configparser # for configuration parsing
import inspect

import logging
from logging import RootLogger
from rich.logging import RichHandler

from CybORG import CybORG

from CybORG.Shared import Observation

from CybORG.Mininet.mininet_adapter import YamlTopologyManager, \
                                    MininetCommandInterface, \
                                    CybORGMininetMapper, \
                                    RedActionTranslator, BlueActionTranslator, \
                                    ResultsBundler, \
                                    RewardCalculator

class MininetAdapter:
    def __init__(self):
        logging.basicConfig(handlers=[RichHandler()])
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        
        self.path = str(inspect.getfile(CybORG))[:-10]
        
        config = configparser.ConfigParser ()
        config.read ('config.ini')

        self.topology_manager = YamlTopologyManager()
        self.command_interface = MininetCommandInterface()
        self.mapper = CybORGMininetMapper()
        self.blue_action_translator = BlueActionTranslator(path=self.path, 
                                                           config=config,
                                                           logger=self.logger)
        self.red_action_translator = RedActionTranslator(path=self.path,
                                                         config=config,
                                                         logger=self.logger)
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
        self.logger.info("===Resetting Mininet Environment===")
        self.clean()

        self.mapper.init_mapping(self.cyborg)

        # Create YAML topology file
        file_path = 'network_topology.yaml'
        # This involves updating topology data and mappings
        
        try:
            self.topology_manager.generate_topology_data(self.cyborg, self.mapper.cyborg_to_mininet_name_map)

        except Exception as e:
            traceback.format_exc()
            raise e

        self.topology_manager.save_topology(file_path)
        
        # Start Mininet with the topology
        try:
            expect_text = self.command_interface.start_mininet(file_path)
        
        except Exception as e:
            traceback.format_exc()
            raise e
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
        self.logger.info(f"---> in MininetAdapter {agent_type} step")
        target, cyborg_action = self.parse_action_string(action_string)
        isSuccess = True # Always True man..

        try:
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
        except Exception as e:
            traceback.print_exc()
            raise e

        try:
            mininet_cli_text = self.command_interface.send_command(mininet_command)
            
            self.logger.info("===Mininet-Cli-Text====")
            self.logger.debug(mininet_cli_text)
        
        except Exception as e:
            traceback.print_exc()
            raise e

        try:    
            mininet_obs = self.results_bundler.bundle(target, cyborg_action, isSuccess, mininet_cli_text, self.mapper)
            
            self.logger.info("===Obs===")
            self.logger.debug(mininet_obs.data)

        except Exception as e:
            traceback.print_exc()
            raise e

        try:
            reward = self.reward_calculator.reward(mininet_obs.data, self.mapper)

            self.logger.info("===Rewards===")
            self.logger.debug(reward)

        except Exception as e:
            traceback.print_exc()
            raise e

        print("*********")

        return mininet_obs, reward

    
    def clean(self):
        self.command_interface.clean()

if __name__ == "__main__":
    print("Hello Mininet Adapter!")

