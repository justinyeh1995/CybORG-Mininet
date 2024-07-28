from pprint import pprint
import time
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
                                    RedActionTranslator, BlueActionTranslator, ActionTranslator, \
                                    ResultsBundler, \
                                    RewardCalculator
from tqdm import tqdm

class MininetAdapter:
    """_summary_
    Controls the lifecycle of the Mininet environment and the translation of CybORG actions to Mininet commands.
    """
    def __init__(self):
        self.md5: Dict[str, dict] = {}
        self.connection_key: Dict = {}
        self.used_ports: Dict = {}
        self.exploited_hosts: List = []
        self.priviledged_hosts: List = []
        self.old_exploit_outcome: Dict = {}
        self.network_state: Dict = {}
        self.available_ports: List = random.sample(range(4000, 5000 + 1), 50)
            
    
    def set_environment(self, cyborg: CybORG):
        """_summary_
            The connection with cyborg instance is established here, 
            the main purpose is to use its initial network data to setup the mininet environment
        Args:
            cyborg (CybORG): _description_
        """
        # Setup based on cyborg environment...
        self.cyborg = cyborg

        
    def _setup(self):
        # Setup code (previously in __init__)
        logging.basicConfig(handlers=[RichHandler()])
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        
        self.path = str(inspect.getfile(CybORG))[:-10]
        
        config = configparser.ConfigParser()
        config.read('config.ini')

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

        self.blue_action_translator.register(self)
        self.red_action_translator.register(self)
        self.results_bundler.register(self)
        
       
    def __enter__(self):
        self._setup()
        return self
    
    
    def __exit__(self, exc_type, exc_value, traceback):
        # Cleanup code
        self.clean()
        if exc_type is not None:
            # Log the exception
            self.logger.error(f"An exception occurred: {exc_type}, {exc_value}")
        self.logger.info("Mininet Adapter Cleaned")
        # Return False to propagate exceptions
        return False
        

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
        try:
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
                logging.error ("Error in starting Mininet")
                # self.clean()
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
            
            while not self.is_service_responsive():
                logging.info ("Waiting for Velociraptor server to become responsive...")
            
            logging.info ("===Perform ResetAction to retrieve initial md5 checksums===")
            # Add tqdm progess bar
            for host in tqdm(self.mapper.mininet_host_to_ip_map.keys(), desc="Processing hosts"):
                if host.startswith("r"):
                    continue
                
                reset_action_string = self.red_action_translator.get_reset_action_string(host, \
                                            self.mapper.cyborg_to_mininet_host_map, \
                                            self.mapper.mininet_host_to_ip_map)
                # logging.debug (f"Reset Action String: {reset_action_string}")
                
                try:
                    expect_text = self.command_interface.send_command(reset_action_string)
                    # logging.debug (expect_text)
                
                except Exception as e:
                    traceback.print_exc()
                    raise e
                
                cyborg_host = self.mapper.mininet_to_cyborg_host_map.get(host, host)
                
                try:
                    mininet_obs = self.results_bundler.bundle(f"{host}", "Reset", True, expect_text, self.mapper)
                    if mininet_obs.success.name == "TRUE":
                        self.md5[cyborg_host] = mininet_obs.data["MD5"]
                    else:
                        logging.error (f"Failed to retrieve initial MD5 checksums for {cyborg_host}")
                        # self.clean()
                        raise ValueError(f"Failed to retrieve initial MD5 checksums for {cyborg_host}")
                    
                except Exception as e:
                    traceback.print_exc()
                    raise e
                
            logging.debug (f"Initial MD5 checksums are: {self.md5}")
        
            
            logging.info("===Resetting Mininet Environment Completed===")
        
        except KeyboardInterrupt:
            logging.error ("Keyboard Interrupt in Reset")
            # self.clean()
            raise KeyboardInterrupt

    
    def step(self, action_string: str, agent_type: str) -> Observation:
        '''Performing emulation
           Translate CybORG action to Mininet command and send it
           Retrieve the results and create observations
        '''
        # @To-Do: bad nested try catch, refactor this code
        try:
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
                # traceback.print_exc()
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
                # traceback.print_exc()
                raise e

            try:    
                if cyborg_action == "ExploitRemoteService" and \
                    self.mapper.mininet_host_to_ip_map.get(target) in self.exploited_hosts:  # this event happens
                    
                    logging.debug (f" Since {self.mapper.mininet_host_to_ip_map.get(target)} is already exploited,\n" + 
                                "we will use the previously stored observation.\n Skipping sending text to result bundler")
                    
                    mininet_obs = self.old_exploit_outcome[self.mapper.mininet_host_to_ip_map.get(target)]
                
                else:
                    
                    mininet_obs = self.results_bundler.bundle(target, cyborg_action, isSuccess, mininet_cli_text, self.mapper)
                    
                    # post processing to manage the states of the cluster
                    if cyborg_action == "ExploitRemoteService" and mininet_obs.success.name == "TRUE":
                        
                        logging.debug (f" This is the first time {self.mapper.mininet_host_to_ip_map.get(target)} \
                                        has gotten exploited,\n" + 
                                    "the adapter will store this observation for future use")
                        
                        # Deserializing the additional data
                        additional_data = mininet_obs.data["Additional Info"]
                        remote_ip = additional_data["Attacked IP"]
                        client_port = additional_data["Attacker Port"]
                        connection_key = additional_data["Connection Key"]
                        
                        if client_port in self.available_ports:
                            self.available_ports.remove(client_port)
                        
                        self.old_exploit_outcome.update({remote_ip: mininet_obs})
                        self.exploited_hosts.append(remote_ip)
                        self.connection_key.update({remote_ip:connection_key})
                    
                    if cyborg_action == "PrivilegeEscalate" and mininet_obs.success.name == "TRUE":
                        
                        logging.info (f"Privilege Escalation on {self.mapper.mininet_host_to_ip_map.get(target)} is successful")
                        
                        self.priviledged_hosts.append(target)
                
                # if mininet_obs.success: update  
                self.logger.info("===Obs===")
                self.logger.debug(mininet_obs.data)

            except Exception as e:
                # traceback.print_exc()
                raise e

            try:
                if agent_type == "Blue" and \
                    self.red_action_translator.last_action in ['ExploitRemoteService', 'DiscoverNetworkServices']:
                    
                    logging.info ("Modify Blue Observation given Previous Red Observation")
                    
                    mininet_obs.data = self.results_bundler.modify_blue_observation_by_red(mininet_obs.data, \
                                                                                    self.results_bundler.last_red_observation.data, \
                                                                                    self.red_action_translator.last_action, \
                                                                                    self.red_action_translator.last_target)
                    self.results_bundler.last_blue_observation = mininet_obs
                    
            except Exception as e:
                # traceback.print_exc()
                raise e

            try:
                reward = self.reward_calculator.reward(mininet_obs.data, self.mapper)

                self.logger.info("===Rewards===")
                self.logger.debug(reward)

            except Exception as e:
                # traceback.print_exc()
                raise e

            print("*********")

            return mininet_obs, reward
        
        except KeyboardInterrupt:
            logging.error ("Keyboard Interrupt in Step, raise to main")
            # self.clean()
            raise KeyboardInterrupt


    def is_service_responsive(self, max_retries=300, retry_interval=1):
        """
        Check if the Velociraptor service is up and responding with valid data.
        
        :param command_interface: The interface used to send commands to Mininet
        :param max_retries: Maximum number of retry attempts (default 300, i.e., 5 minutes)
        :param retry_interval: Time to wait between retries in seconds (default 1 second)
        :return: Boolean indicating whether the service is responsive
        """
        logging.info(f"Testing if Velociraptor server is responsive, will retry for up to {max_retries * retry_interval} seconds due to warm-up time")
        
        for attempt in range(max_retries):
            cmd = 'lan3h1 wget -t 1 -T 1 -O - http://127.0.0.1:8001 2>&1'
            expect_text = self.command_interface.send_command(cmd)
            
            if "connected" in expect_text:
                logging.info(f"Velociraptor server is fully responsive after {attempt + 1} attempts!")
                return True
        
            logging.debug(f"Attempt {attempt + 1} failed.")
            time.sleep(retry_interval)
        
        logging.error(f"Velociraptor server did not become responsive after {max_retries} attempts")
        return False
    
    
    def clean(self):
        self.command_interface.clean()
        

if __name__ == "__main__":
    print("Hello Mininet Adapter!")

