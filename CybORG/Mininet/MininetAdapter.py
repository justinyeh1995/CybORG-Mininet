from pprint import pprint
import traceback 
from typing import List, Dict
import configparser # for configuration parsing
import inspect
import random

import logging
from logging import RootLogger
from rich.logging import RichHandler

from CybORG import CybORG

from CybORG.Shared import Observation

from CybORG.Mininet.mininet_adapter import YamlTopologyManager, \
                                    TopologyAssetManager, \
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

        self.topology_asset_manager = TopologyAssetManager()
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

        self.connection_key={}
        self.used_ports={}
        self.exploited_hosts=[]
        self.priviledged_hosts=[]
        self.old_exploit_outcome={}
        self.network_state={}
        self.available_ports: List = random.sample(range(4000, 5000 + 1), 50)
        
        self.blue_action_translator.register(self)
        self.red_action_translator.register(self)
        self.topology_asset_manager.register(self)
        
    
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
        file_path = './systems/tmp/network_topology.yaml'
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
            # @To-Do is there a better design or this is the best way to handle resources like self.exploited_hosts
            if cyborg_action == "ExploitRemoteService" and \
                self.mapper.mininet_host_to_ip_map[target] in self.exploited_hosts:  # this event happens
                
                logging.debug (f" Target is: {self.mapper.mininet_host_to_ip_map.get(target)},\n" + 
                               f"Exploited hosts are: {self.exploited_hosts}")
                
                mininet_cli_text = "We have already exploited this host. Skipping sending command to Mininet!"
            
            else:
            
                mininet_cli_text = self.command_interface.send_command(mininet_command)
            
            self.logger.info("===Mininet-Cli-Text====")
            self.logger.debug(mininet_cli_text)
        
        except Exception as e:
            traceback.print_exc()
            raise e

        try:    
            if cyborg_action == "ExploitRemoteService" and self.mapper.mininet_host_to_ip_map.get(target) in self.exploited_hosts:  # this event happens
                
                logging.debug (f" Since {self.mapper.mininet_host_to_ip_map.get(target)} is already exploited,\n" + 
                               "we will use the previously stored observation.\n Skipping sending text to result bundler")
                
                mininet_obs = self.old_exploit_outcome[self.mapper.mininet_host_to_ip_map.get(target)]
            
            else:
                
                mininet_obs = self.results_bundler.bundle(target, cyborg_action, isSuccess, mininet_cli_text, self.mapper)
                
                # post processing to manage the states of the cluster
                if cyborg_action == "ExploitRemoteService" and mininet_obs.success.name == "TRUE":
                    
                    logging.debug (f" This is the first time {self.mapper.mininet_host_to_ip_map.get(target)} has gotten exploited,\n" + 
                                   "the adapter will store this observation for future use")
                
                    additional_data = mininet_obs.data["Additional Info"]
                    remote_ip = additional_data["Attacked IP"]
                    client_port = additional_data["Attacker Port"]
                    connection_key = additional_data["Connection Key"]
                    
                    if client_port in self.available_ports:
                        self.available_ports.remove(client_port)
                    
                    self.old_exploit_outcome.update({remote_ip: mininet_obs})
                    self.exploited_hosts.append(remote_ip)
                    self.connection_key.update({remote_ip:connection_key})
            
            # if mininet_obs.success: update  
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

