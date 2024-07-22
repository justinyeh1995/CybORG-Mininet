import yaml
import traceback 
from typing import Dict, List, Any #@To-Do bad design: go figure out the type..
import logging

from CybORG.Mininet.mininet_adapter.entity import Entity
from CybORG.Mininet.Wrappers.BlueEmulationWrapper import BlueEmulationWrapper

class TopologyAssetManager(Entity):
    """_summary_
    Manage the process of generating the initial blue observations and info for a new topology
    Args:
    """
    def __init__(self, topology_data: Dict = None):
        self.init_blue_obs_info = {
            "Defender": ["10.0.120.144/28", "10.0.120.156", "Defender", "None", "No"], 
            "Enterprise0": ["10.0.120.144/28", "10.0.120.152", "Enterprise0", "None", "No"], 
            "Enterprise1": ["10.0.120.144/28", "10.0.120.158", "Enterprise1", "None", "No"], 
            "Enterprise2": ["10.0.120.144/28", "10.0.120.155", "Enterprise2", "None", "No"], 
            "Op_Host0": ["10.0.110.32/28", "10.0.110.38", "Op_Host0", "None", "No"], 
            "Op_Host1": ["10.0.110.32/28", "10.0.110.42", "Op_Host1", "None", "No"], 
            "Op_Host2": ["10.0.110.32/28", "10.0.110.46", "Op_Host2", "None", "No"], 
            "Op_Server0": ["10.0.110.32/28", "10.0.110.34", "Op_Server0", "None", "No"], 
            "User0": ["10.0.214.176/28", "10.0.214.186", "User0", "None", "No"], 
            "User1": ["10.0.214.176/28", "10.0.214.187", "User1", "None", "No"], 
            "User2": ["10.0.214.176/28", "10.0.214.182", "User2", "None", "No"], 
            "User3": ["10.0.214.176/28", "10.0.214.180", "User3", "None", "No"], 
            "User4": ["10.0.214.176/28", "10.0.214.189", "User4", "None", "No"]
        }
        self.init_blue_obs = None
        
        
    def reset(self) -> None:
        """The function that resets the blue initial observations and info"""
        self.convert_init_blue_info()
        self.init_blue_obs = self.generate_init_blue_obs()
        return self.init_blue_obs
        
        
    def generate_init_blue_obs(self) -> Any:
        """Create the initial blue observations for the new topology"""
        try:
            blue_emulation_wrapper = BlueEmulationWrapper(None)
            blue_observation=blue_emulation_wrapper.reset(self.init_blue_obs_info)
            
            logging.info ("Initial Blue Observations for new topology created successfully.")
            
            return blue_observation
        
        except Exception as e:
            logging.error ("An error occurred while creating the initial blue observations:")
            logging.exception (e)
            traceback.print_exc()
            raise
            
    def convert_init_blue_info(self) -> None:
        """Update the initial blue observations with the new topology info"""
        if self.mininet_adpator is None:
            raise ValueError("Mininet Adapter is not initialized.")
         
        try:
            for host_name, info in self.init_blue_obs_info.items():
                ip = self.mininet_adpator.mapper.cyborg_host_to_ip_map[host_name]
                subnet = self.mininet_adpator.mapper.cyborg_ip_to_subnet[ip]
                # print("Host Name:", host_name)
                # print("IP:", ip)
                # print("Subnet:", subnet)
                info[0] = subnet
                info[1] = ip
                
            logging.info ("Initial Blue Info for new topology updated successfully.")
        
        except Exception as e:
            logging.error ("An error occurred while updating the info:")
            logging.exception (e)
            traceback.print_exc()     


    def get_init_blue_info(self) -> Dict:
        return self.init_blue_obs_info
    
    def get_inti_blue_obs(self) -> Any:
        return self.init_blue_obs
    # def __getattribute__(self, name: str) -> yaml.Any:
    #     return super().__getattribute__(name)
