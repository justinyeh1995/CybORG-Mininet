from pathlib import Path
from pprint import pprint
import time
import traceback 
from typing import List, Dict, Tuple
import configparser # for configuration parsing
import inspect
import random

import logging
from logging import RootLogger
from rich.logging import RichHandler
from tqdm import tqdm

from CybORG import CybORG

from CybORG.Shared import Observation

from CybORG.Mininet.AdapterComponents import YamlTopologyManager, \
                                    MininetCommandInterface, \
                                    CybORGMininetMapper, \
                                    RedActionTranslator, BlueActionTranslator, \
                                    ResultsBundler, \
                                    NetworkStateManager, \
                                    RewardCalculator

class MininetAdapter:
    """_summary_
    Controls the lifecycle of the Mininet environment and the translation of CybORG actions to Mininet commands.
    """
    def __init__(self, scenario: str = "Scenario2"):
        self.path = str(inspect.getfile(CybORG))[:-10]
        self.scenario_file_path =  self.path + f'/Shared/Scenarios/{scenario}.yaml'
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
        
        self.config = configparser.ConfigParser()
        self.config.read(self.path+'/Mininet/config.cfg')

        self.topology_manager = YamlTopologyManager()
        self.mapper = CybORGMininetMapper()
        
        self.command_interface = MininetCommandInterface(config=self.config)
        
        self.blue_action_translator = BlueActionTranslator(path=self.path, 
                                                           config=self.config,
                                                           logger=self.logger)
        self.red_action_translator = RedActionTranslator(path=self.path,
                                                         config=self.config,
                                                         logger=self.logger)
        self.results_bundler = ResultsBundler()
        
        self.network_state_manager = NetworkStateManager()
        
        self.reward_calculator = RewardCalculator(self.scenario_file_path)

        self.blue_action_translator.register(self)
        self.red_action_translator.register(self)
        self.results_bundler.register(self)
        self.command_interface.register(self)
        
       
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
        

    def parse_action_string(self, action_string: str) -> Tuple[str, str, str]:
        """_summary_

        Args:
            action_string (str): The natural language action string from CybORG

        Returns:
            tuple: A tuple containing the targeted cyborg hostname, mininet hostname, and the action type
        """
        logging.info("--> in MininetAdapter parse_action_string")
        logging.debug (action_string)
        action_str_split = action_string.split(" ")
        action_type = action_str_split[0]
        n = len(action_str_split)
        target_host = action_str_split[-1] if n > 1 else ""
        target_host = self.mapper.cyborg_ip_to_host_map.get(target_host, target_host)
                
        return (target_host, 
                self.mapper.cyborg_to_mininet_host_map.get(target_host, target_host), 
                action_type) 

    
    def reset(self):
        self.logger.info("===Resetting Mininet Environment===")
        
        try:
            self.clean()
        except Exception as e:
            logging.error ("Error in cleaning Mininet")
            raise e

        try:
            self.mapper.init_mapping(self.cyborg)
        except Exception as e:
            logging.error ("Error in mapping CybORG namespace and Mininet namespace")
            raise
        
        try:
            self.topology_manager.generate_topology_data(self.cyborg, 
                            self.mapper.cyborg_to_mininet_name_map, 
                            self.mapper.cyborg_to_mininet_host_map)
        except Exception as e:
            logging.error ("Error in generating topology data")
            raise e

        # Create YAML topology file
        system_folder_path = Path(self.path + self.config["Mininet"]["SYS_FOLDER_PATH"])
        logging.debug (f"System folder path is: {system_folder_path}")
        # import pdb; pdb.set_trace()
        file_path = f'{system_folder_path}/tmp/network_topology.yaml'
        
        try:
            self.topology_manager.save_topology(file_path)
        except Exception as e:
            logging.error ("Error in saving topology file")
            raise e
        
        # Start Mininet with the topology
        try:
            expect_text = self.command_interface.start_mininet(file_path)
        except Exception as e:
            logging.error ("Error in starting Mininet")
            raise e

        try:
            print("===DNS Test===")
            expect_text = self.command_interface.send_command('lan1h1 ping -c 1 google.com')
            print(expect_text)
        except Exception as e:
            raise e
                
        # while not self.is_service_responsive():
        #     logging.info ("Waiting for Velociraptor server to become responsive...")
        
        logging.info ("===Perform ResetAction to retrieve initial md5 checksums===")
        # Add tqdm progess bar
        for host in tqdm(self.mapper.mininet_host_to_ip_map.keys(), desc="Processing hosts"):
            if host.startswith("r"):
                continue
            
            reset_action_string = self.red_action_translator.get_reset_action_string(host, \
                                        self.mapper.cyborg_to_mininet_host_map, \
                                        self.mapper.mininet_host_to_ip_map)
            
            try:
                expect_text = self.command_interface.send_command(reset_action_string)            
            except Exception as e:
                logging.error ("Error in reset command")
                raise e
            
            cyborg_host = self.mapper.mininet_to_cyborg_host_map.get(host, host)
            
            try:
                mininet_obs = self.results_bundler.bundle(f"{host}", "Reset", expect_text, self.mapper)
                if mininet_obs.success.name == "TRUE":
                    self.md5[cyborg_host] = mininet_obs.data["MD5"]
                else:
                    logging.error (f"Failed to retrieve initial MD5 checksums for {cyborg_host}")
                    raise ValueError(f"Failed to retrieve initial MD5 checksums for {cyborg_host}")        
            except Exception as e:
                raise e
            
        logging.debug (f"Initial MD5 checksums are: {self.md5}")
        logging.info("===Resetting Mininet Environment Completed===")


    
    def step(self, action_string: str, agent_type: str) -> Observation:
        '''Performing emulation
           Translate CybORG action to Mininet command and send it
           Retrieve the results and create observations
        '''
        self.logger.info(f"---> in MininetAdapter {agent_type} step")
        cyborg_hostname, mininet_hostname, cyborg_action = self.parse_action_string(action_string)

        try:
            if agent_type == "Blue":
                mininet_command = self.blue_action_translator.translate(cyborg_action, 
                                                                    mininet_hostname, 
                                                                    self.mapper.cyborg_to_mininet_host_map,
                                                                    self.mapper.mininet_host_to_ip_map)  
            elif agent_type == "Red":
                mininet_command = self.red_action_translator.translate(cyborg_action, 
                                                                    mininet_hostname,
                                                                    self.mapper.cyborg_to_mininet_host_map,
                                                                    self.mapper.mininet_host_to_ip_map)
        except Exception as e:
            raise e

        try:
            # @To-Do is there a better design or this is the best way to handle resources like self.exploited_hosts
            if cyborg_action == "ExploitRemoteService" and \
                self.mapper.mininet_host_to_ip_map[mininet_hostname] in self.exploited_hosts:  # this event happens
                
                logging.debug (f" Target is: {self.mapper.mininet_host_to_ip_map.get(mininet_hostname)},\n" + 
                            f"Exploited hosts are: {self.exploited_hosts}")
                
                mininet_cli_text = "We have already exploited this host. Skipping sending command to Mininet!"
            
            else:
            
                mininet_cli_text = self.command_interface.send_command(mininet_command)
            
            self.logger.info("===Mininet-Cli-Text====")
            self.logger.debug(mininet_cli_text)
        
        except Exception as e:
            raise e

        try:    
            if cyborg_action == "ExploitRemoteService" and \
                self.mapper.mininet_host_to_ip_map.get(mininet_hostname) in self.exploited_hosts:  # this event happens
                
                logging.debug (f" Since {self.mapper.mininet_host_to_ip_map.get(mininet_hostname)} is already exploited,\n" + 
                            "we will use the previously stored observation.\n Skipping sending text to result bundler")
                
                mininet_obs = self.old_exploit_outcome[self.mapper.mininet_host_to_ip_map.get(mininet_hostname)]
            
            else:
                
                mininet_obs = self.results_bundler.bundle(mininet_hostname, cyborg_action, mininet_cli_text, self.mapper)
                
                # post processing to manage the states of the cluster
                if cyborg_action == "ExploitRemoteService" and mininet_obs.success.name == "TRUE":
                    
                    logging.debug (f" This is the first time {self.mapper.mininet_host_to_ip_map.get(mininet_hostname)} \
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
                    
                    logging.info (f"Privilege Escalation on {self.mapper.mininet_host_to_ip_map.get(mininet_hostname)} is successful")
                    
                    self.priviledged_hosts.append(mininet_hostname)
            
            # if mininet_obs.success: update  
            self.logger.info("===Obs===")
            self.logger.debug(mininet_obs.data)

            # store the last observation
            self.logger.info("===Record this obs as the last observation===")
            self.results_bundler.update_last_observation(cyborg_action=cyborg_action, obs=mininet_obs)
        
        except Exception as e:
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
            raise e

        try:
            self.network_state_manager.update_network_state(cyborg_action, 
                                                            cyborg_hostname, 
                                                            mininet_obs, "root")
            reward = self.reward_calculator.reward(self.network_state_manager.get_network_state())
            
            self.logger.info("===Rewards===")
            self.logger.debug(reward)

        except Exception as e:
            raise e

        logging.info("*********")

        return mininet_obs, reward


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
            cmd = 'lan3h1 wget -t 1 -T 1 -O - http://127.0.0.1:8001 2>&1' # @To-Do make it configurable
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
