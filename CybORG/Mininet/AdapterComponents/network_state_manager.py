import logging
from typing import Dict
from pydantic import BaseModel, Field
# from CybORG.Mininet.AdapterComponents.entity import Entity

class NetworkStateManager(BaseModel):
    
    info_dict: Dict[str, dict] = Field(default_factory=lambda: dict())

    def update_network_state(self, action_type, server_name, obs, username='root'):
        if action_type == "PrivilegeEscalate" and obs.success.name == "TRUE":
            self.update_reward_information_dict(server_name, username)
            logging.debug (f"Privilege Escalated on {server_name}, the info dict is now: {self.info_dict}")
        
        elif action_type == "Remove" and obs.success.name == "TRUE":
            self.delete_reward_information_dict(server_name, username)
            logging.debug (f"Removed {server_name} from the network, the info dict is now: {self.info_dict}")

        elif action_type == "Restore" and obs.success.name == "TRUE":
            self.delete_reward_information_dict(server_name, username)
            logging.debug (f"Restored {server_name} to its original state, the info dict is now: {self.info_dict}")
        
        
    def update_reward_information_dict(self, server_name, username='root'):
        if server_name not in self.info_dict:
            self.info_dict[server_name] = {'Sessions': []}
        self.info_dict[server_name]['Sessions'].append({'Username': username})
        
        return self.info_dict

    def delete_reward_information_dict(self, server_name, username='root'):
        if server_name in self.info_dict:
            sessions = self.info_dict[server_name]['Sessions']
            self.info_dict[server_name]['Sessions'] = [session for session in sessions if session['Username'] != username]
            
            # If there are no more sessions, remove the server entry
            if not self.info_dict[server_name]['Sessions']:
                del self.info_dict[server_name]
        
        return self.info_dict
    
    def get_network_state(self):
        return self.info_dict
    