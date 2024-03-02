import subprocess
import pexpect
import yaml
import collections
import pprint
import re
import traceback 
from typing import List, Dict
from ipaddress import IPv4Address, IPv4Network
from Mininet.mininet_utils.custom_utils import IP_components
from Mininet.mininet_adapter import YamlTopologyManager, \
                                    MininetCommandInterface, \
                                    CybORGMininetMapper, \
                                    RedActionTranslator, BlueActionTranslator, \
                                    ResultsBundler
from Mininet.utils.util import parse_action, parse_mininet_ip, \
                            set_name_map, get_routers_info, get_lans_info, get_links_info, \
                            translate_discover_remote_systems, \
                            translate_discover_network_services, \
                            translate_exploit_network_services, \
                            translate_restore, translate_remove 
                       

class MininetAdapter:
    def __init__(self):
        self.topology_manager = YamlTopologyManager()
        self.command_interface = MininetCommandInterface()
        self.mapper = CybORGMininetMapper()
        self.blue_action_translator = BlueActionTranslator()
        self.red_action_translator = RedActionTranslator()
        self.results_bundler = ResultsBundler()

    
    def set_environment(self, cyborg):
        # Setup based on cyborg environment...
        self.cyborg = cyborg
        
    
    def reset(self):
        self.clean()

        self.mapper.init_mapping(self.cyborg)

        # Create YAML topology file
        file_path = './network_topology.yaml'
        # This involves updating topology data and mappings
        self.topology_manager.generate_topology_data(self.cyborg, self.mapper.cyborg_to_mininet_name_map)
        self.topology_manager.save_topology(file_path)
        
        # Start Mininet with the topology
        expect_text = self.command_interface.start_mininet(file_path)

        self.mapper.update_mapping(expect_text)


    def perform_emulation(self):
        # Example of performing emulation
        # Translate CybORG action to Mininet command and send it
        cyborg_action = "some_action_from_cyborg"
        mininet_command = self._translate_action_to_command(cyborg_action)
        mininet_cli_text = self.command_interface.send_command(mininet_command)
        return self.results_bundler.bundle(mininet_cli_text)

    
    def clean(self):
        self.command_interface.clean()

