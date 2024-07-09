# import collections
# from pprint import pprint
# import json
# from ipaddress import IPv4Address, IPv4Network
# import re
# import traceback 
# from typing import List, Dict
# from pydantic import BaseModel
# from CybORG.Mininet.mininet_adapter.utils.util import build_cyborg_to_mininet_name_map, parse_mininet_ip, \
#                             build_mininet_host_to_cyborg_ip_map, build_cyborg_ip_to_mininet_host_map

# class CybORGMininetMapper(BaseModel):
#     def __init__(self):
#         # Inner CybORG lookup
#         self.ip_map = {}
#         self.cidr_map = {}
#         self.cyborg_ip_to_host_map = {} # @To-Do Add type hint
#         self.cyborg_host_to_ip_map = {}
#         self.usable_ip_to_subnet: Dict[str, list] = collections.defaultdict(list) 
#         self.cyborg_ip_to_subnet = {}

#         # Inner Mininet lookup
#         self.mininet_host_to_ip_map = {}
#         self.mininet_ip_to_host_map = {}

#         # CybORG<->Mininet lookup
#         self.cyborg_to_mininet_name_map = {}
#         self.mininet_host_to_cyborg_ip_map = {}
#         self.cyborg_ip_to_mininet_host_map = {}
#         self.cyborg_to_mininet_host_map = {}
#         self.mininet_to_cyborg_host_map = {}
#         self.cyborg_ip_to_mininet_ip_map = {}
#         self.mininet_ip_to_cyborg_ip_map = {}
    
#     def init_mapping(self, cyborg) -> None: 
#         self.ip_map = cyborg.get_ip_map()
#         self.cidr_map = {lan_name: network for lan_name, network in cyborg.environment_controller.subnet_cidr_map.items()}

#         self.cyborg_ip_to_host_map = {str(ip): host for host, ip in self.ip_map.items()}
#         self.cyborg_host_to_ip_map = {host: str(ip) for host, ip in self.ip_map.items()}

#         self.usable_ip_to_subnet = {str(network): list(network.hosts()) for network in self.cidr_map.values()} # Dict[str]: list of IPV4Address
        
#         for network, usable_ips in self.usable_ip_to_subnet.items():
#             for ip in self.cyborg_ip_to_host_map:
#                 if IPv4Address(ip) in usable_ips:
#                     self.cyborg_ip_to_subnet.update({ip: network})
        
#         # generate router ip 
#         self.cyborg_to_mininet_name_map = build_cyborg_to_mininet_name_map(cyborg)
#         self.mininet_host_to_ip_map = {}
    
#     def update_mapping(self, output: str, topology_data: dict) -> None:
        
#         matches = parse_mininet_ip(output)

#         # Create a dictionary to map host names to their IP addresses
#         self.mininet_host_to_ip_map = {match.group('host'): match.group('ip') for match in matches}

#         self.mininet_ip_to_host_map = {match.group('ip'): match.group('host') for match in matches}

#         self.mininet_host_to_cyborg_ip_map = build_mininet_host_to_cyborg_ip_map(topology_data) 

#         self.cyborg_ip_to_mininet_host_map = build_cyborg_ip_to_mininet_host_map(topology_data)

#         self.cyborg_to_mininet_host_map = { 
#             self.cyborg_ip_to_host_map[cyborg_ip]:self.cyborg_ip_to_mininet_host_map[cyborg_ip] 
#             for cyborg_ip in self.cyborg_ip_to_host_map}

#         self.mininet_to_cyborg_host_map = {
#             self.cyborg_ip_to_mininet_host_map[cyborg_ip]:self.cyborg_ip_to_host_map[cyborg_ip] 
#             for cyborg_ip in self.cyborg_ip_to_host_map}
        
#         self.cyborg_ip_to_mininet_ip_map = { 
#             self.cyborg_host_to_ip_map[cyborg_h]:self.mininet_host_to_ip_map[mininet_h] 
#                 for cyborg_h, mininet_h in self.cyborg_to_mininet_host_map.items()}
        
#         self.mininet_ip_to_cyborg_ip_map = {
#             self.mininet_host_to_ip_map[mininet_h]:self.cyborg_host_to_ip_map[cyborg_h] 
#                 for cyborg_h, mininet_h in self.cyborg_to_mininet_host_map.items()}

    
#     def __str__(self):
#         # For a more user-friendly representation
#         return (f"CybORGMininetMapper:\n"
#                 f"  CybORG IP -> Host Mapping: {len(self.cyborg_ip_to_host_map)} items\n"
#                 f"  Mininet Host -> IP Mapping: {len(self.mininet_host_to_ip_map)} items\n"
#                 f"  CybORG to Mininet Name Mapping: {len(self.cyborg_to_mininet_name_map)} items\n"
#                 f"  Mininet Host to CybORG IP Mapping: {len(self.mininet_host_to_cyborg_ip_map)} items\n"
#                 f"  CybORG IP to Mininet Host Mapping: {len(self.cyborg_ip_to_mininet_host_map)} items\n"
#                 f"  CybORG to Mininet Host Mapping: {len(self.cyborg_to_mininet_host_map)} items\n"
#                 f"  Mininet to CybORG Host Mapping: {len(self.mininet_to_cyborg_host_map)} items\n"
#                 f"  CybORG IP to Mininet IP Mapping: {len(self.cyborg_ip_to_mininet_ip_map)} items\n"
#                 f"  Mininet IP to CybORG IP Mapping: {len(self.mininet_ip_to_cyborg_ip_map)} items")

    
#     def __repr__(self):
#         # For a more detailed, developer-focused representation
#         # Convert the relevant attributes to a dictionary
#         mapper_dict = {
#             'cidr_map': self.cidr_map,
#             'cyborg_ip_to_host_map': self.cyborg_ip_to_host_map,
#             'cyborg_host_to_ip_map': self.cyborg_host_to_ip_map,
#             'mininet_host_to_ip_map': self.mininet_host_to_ip_map,
#             'mininet_ip_to_host_map': self.mininet_ip_to_host_map,
#             'cyborg_to_mininet_name_map': self.cyborg_to_mininet_name_map,
#             'mininet_host_to_cyborg_ip_map': self.mininet_host_to_cyborg_ip_map,
#             'cyborg_ip_to_mininet_host_map': self.cyborg_ip_to_mininet_host_map,
#             'cyborg_to_mininet_host_map': self.cyborg_to_mininet_host_map,
#             'mininet_to_cyborg_host_map': self.mininet_to_cyborg_host_map,
#             'cyborg_ip_to_mininet_ip_map': self.cyborg_ip_to_mininet_ip_map,
#             'mininet_ip_to_cyborg_ip_map': self.mininet_ip_to_cyborg_ip_map
#         }
#         # pprint(mapper_dict)
#         # Use json.dumps for pretty printing
#         return f"CybORGMininetMapper(\n{json.dumps(mapper_dict, indent=2)}\n)"
        
# import collections
# from pprint import pprint
# import json
# import re
# import traceback 
from CybORG.Mininet.mininet_adapter.utils.util import build_cyborg_to_mininet_name_map, parse_mininet_ip, \
                            build_mininet_host_to_cyborg_ip_map, build_cyborg_ip_to_mininet_host_map
from pydantic import BaseModel, Field
from typing import Dict, List
from ipaddress import IPv4Address, IPv4Network
import collections
import json

class CybORGMininetMapper(BaseModel):
    # Inner CybORG lookup
    ip_map: Dict[str, IPv4Address] = Field(default_factory=dict)
    cidr_map: Dict[str, IPv4Network] = Field(default_factory=dict)
    cyborg_ip_to_host_map: Dict[str, str] = Field(default_factory=dict)
    cyborg_host_to_ip_map: Dict[str, str] = Field(default_factory=dict)
    usable_ip_to_subnet: Dict[str, List[IPv4Address]] = Field(default_factory=lambda: collections.defaultdict(list))
    cyborg_ip_to_subnet: Dict[str, str] = Field(default_factory=dict)

    # Inner Mininet lookup
    mininet_host_to_ip_map: Dict[str, str] = Field(default_factory=dict)
    mininet_ip_to_host_map: Dict[str, str] = Field(default_factory=dict)

    # CybORG<->Mininet lookup
    cyborg_to_mininet_name_map: Dict[str, str] = Field(default_factory=dict)
    mininet_host_to_cyborg_ip_map: Dict[str, str] = Field(default_factory=dict)
    cyborg_ip_to_mininet_host_map: Dict[str, str] = Field(default_factory=dict)
    cyborg_to_mininet_host_map: Dict[str, str] = Field(default_factory=dict)
    mininet_to_cyborg_host_map: Dict[str, str] = Field(default_factory=dict)
    cyborg_ip_to_mininet_ip_map: Dict[str, str] = Field(default_factory=dict)
    mininet_ip_to_cyborg_ip_map: Dict[str, str] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True

    def init_mapping(self, cyborg) -> None:
        self.ip_map = cyborg.get_ip_map()
        self.cidr_map = {lan_name: network for lan_name, network in cyborg.environment_controller.subnet_cidr_map.items()}

        self.cyborg_ip_to_host_map = {str(ip): host for host, ip in self.ip_map.items()}
        self.cyborg_host_to_ip_map = {host: str(ip) for host, ip in self.ip_map.items()}

        self.usable_ip_to_subnet = {str(network): list(network.hosts()) for network in self.cidr_map.values()}
        
        for network, usable_ips in self.usable_ip_to_subnet.items():
            for ip in self.cyborg_ip_to_host_map:
                if IPv4Address(ip) in usable_ips:
                    self.cyborg_ip_to_subnet[ip] = network
        
        self.cyborg_to_mininet_name_map = build_cyborg_to_mininet_name_map(cyborg)

    def update_mapping(self, output: str, topology_data: dict) -> None:
        matches = parse_mininet_ip(output)

        self.mininet_host_to_ip_map = {match.group('host'): match.group('ip') for match in matches}
        self.mininet_ip_to_host_map = {match.group('ip'): match.group('host') for match in matches}

        self.mininet_host_to_cyborg_ip_map = build_mininet_host_to_cyborg_ip_map(topology_data)
        self.cyborg_ip_to_mininet_host_map = build_cyborg_ip_to_mininet_host_map(topology_data)

        self.cyborg_to_mininet_host_map = {
            self.cyborg_ip_to_host_map[cyborg_ip]: self.cyborg_ip_to_mininet_host_map[cyborg_ip]
            for cyborg_ip in self.cyborg_ip_to_host_map
        }

        self.mininet_to_cyborg_host_map = {
            self.cyborg_ip_to_mininet_host_map[cyborg_ip]: self.cyborg_ip_to_host_map[cyborg_ip]
            for cyborg_ip in self.cyborg_ip_to_host_map
        }
        
        # Redundant
        self.cyborg_ip_to_mininet_ip_map = {
            self.cyborg_host_to_ip_map[cyborg_h]: self.mininet_host_to_ip_map[mininet_h]
            for cyborg_h, mininet_h in self.cyborg_to_mininet_host_map.items()
        }
        # Redundant
        self.mininet_ip_to_cyborg_ip_map = {
            self.mininet_host_to_ip_map[mininet_h]: self.cyborg_host_to_ip_map[cyborg_h]
            for cyborg_h, mininet_h in self.cyborg_to_mininet_host_map.items()
        }

    def __str__(self):
        return (f"CybORGMininetMapper:\n"
                f"  CybORG IP -> Host Mapping: {len(self.cyborg_ip_to_host_map)} items\n"
                f"  Mininet Host -> IP Mapping: {len(self.mininet_host_to_ip_map)} items\n"
                f"  CybORG to Mininet Name Mapping: {len(self.cyborg_to_mininet_name_map)} items\n"
                f"  Mininet Host to CybORG IP Mapping: {len(self.mininet_host_to_cyborg_ip_map)} items\n"
                f"  CybORG IP to Mininet Host Mapping: {len(self.cyborg_ip_to_mininet_host_map)} items\n"
                f"  CybORG to Mininet Host Mapping: {len(self.cyborg_to_mininet_host_map)} items\n"
                f"  Mininet to CybORG Host Mapping: {len(self.mininet_to_cyborg_host_map)} items\n"
                f"  CybORG IP to Mininet IP Mapping: {len(self.cyborg_ip_to_mininet_ip_map)} items\n"
                f"  Mininet IP to CybORG IP Mapping: {len(self.mininet_ip_to_cyborg_ip_map)} items")

    def dict(self, *args, **kwargs):
        # Custom dict method to handle non-serializable types
        base_dict = super().dict(*args, **kwargs)
        for key, value in base_dict.items():
            if isinstance(value, dict):
                base_dict[key] = {str(k): str(v) for k, v in value.items()}
            elif isinstance(value, collections.defaultdict):
                base_dict[key] = dict(value)
        return base_dict

    def json(self, *args, **kwargs):
        return json.dumps(self.dict(), *args, **kwargs)