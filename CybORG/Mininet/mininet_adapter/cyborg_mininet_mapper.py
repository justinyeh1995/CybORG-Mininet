from CybORG.Mininet.mininet_adapter.entity import Entity

from CybORG.Mininet.mininet_adapter.utils.mapper_util import build_cyborg_host_to_mininet_host_map, parse_mininet_ip, \
                            build_mininet_host_to_cyborg_ip_map, build_cyborg_ip_to_mininet_host_map
from pydantic import BaseModel, Field
from typing import Dict, List, Set
from ipaddress import IPv4Address, IPv4Network
import collections
from collections import defaultdict
import json

class CybORGMininetMapper(BaseModel, Entity):
    # Inner CybORG lookup
    ip_map: Dict[str, IPv4Address] = Field(default_factory=lambda: collections.defaultdict(IPv4Network))
    cidr_map: Dict[str, IPv4Network] = Field(default_factory=lambda: collections.defaultdict(IPv4Network))
    cyborg_ip_to_host_map: Dict[str, str] = Field(default_factory=lambda: collections.defaultdict(str))
    cyborg_host_to_ip_map: Dict[str, str] = Field(default_factory=lambda: collections.defaultdict(str))
    usable_ip_to_subnet: Dict[str, List[IPv4Address]] = Field(default_factory=lambda: collections.defaultdict(list))
    cyborg_ip_to_subnet: Dict[str, str] = Field(default_factory=lambda: collections.defaultdict(str))
    cyborg_subnet_to_ip_list: Dict[str, List[str]] = Field(default_factory=lambda: collections.defaultdict(list))
    
    # Inner Mininet lookup
    mininet_host_to_ip_map: Dict[str, str] = Field(default_factory=lambda: collections.defaultdict(str))
    mininet_ip_to_host_map: Dict[str, str] = Field(default_factory=lambda: collections.defaultdict(str))

    # CybORG<->Mininet lookup
    cyborg_to_mininet_name_map: Dict[str, str] = Field(default_factory=lambda: collections.defaultdict(str))
    mininet_host_to_cyborg_ip_map: Dict[str, str] = Field(default_factory=lambda: collections.defaultdict(str))
    cyborg_ip_to_mininet_host_map: Dict[str, str] = Field(default_factory=lambda: collections.defaultdict(str))
    cyborg_to_mininet_host_map: Dict[str, str] = Field(default_factory=lambda: collections.defaultdict(str))
    mininet_to_cyborg_host_map: Dict[str, str] = Field(default_factory=lambda: collections.defaultdict(str))
    cyborg_ip_to_mininet_ip_map: Dict[str, str] = Field(default_factory=lambda: collections.defaultdict(str))
    mininet_ip_to_cyborg_ip_map: Dict[str, str] = Field(default_factory=lambda: collections.defaultdict(str))

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
                    self.cyborg_subnet_to_ip_list[network].append(ip)
              
        for cnt, (lan_name, network) in enumerate(self.cidr_map.items()):
            self.cyborg_to_mininet_name_map[lan_name] = f'lan{cnt+1}'
            self.cyborg_to_mininet_name_map[f'{lan_name}_router'] = f'r{cnt+1}'
            num = 1
            for ip in self.cyborg_subnet_to_ip_list.get(str(network), []):
                cyborg_host = self.cyborg_ip_to_host_map.get(ip, "?")
                if cyborg_host.endswith("_router"):
                    mininet_host = f'r{cnt+1}'
                else:
                    mininet_host = f'lan{cnt+1}h{num}'
                    num+=1
                if mininet_host in self.mininet_to_cyborg_host_map:
                    continue
                self.cyborg_to_mininet_host_map[cyborg_host] = mininet_host
                self.mininet_to_cyborg_host_map[mininet_host] = cyborg_host
                
                
        # self.cyborg_to_mininet_host_map = build_cyborg_host_to_mininet_host_map(cyborg)
        self.mininet_host_to_ip_map = {self.cyborg_to_mininet_host_map.get(host): ip for host, ip in self.cyborg_host_to_ip_map.items()}
        self.mininet_ip_to_host_map = {ip: host for host, ip in self.mininet_host_to_ip_map.items()}
        
        from pprint import pprint
        import logging
        import pdb
        #print all dicts
        pprint(self.cyborg_host_to_ip_map)
        # pprint(self.cyborg_ip_to_subnet)
        # pprint(self.cyborg_subnet_to_ip_list)
        # pprint(self.cyborg_to_mininet_name_map)
        # pprint(self.cyborg_to_mininet_host_map)
        # pprint(self.mininet_host_to_ip_map)
        # pprint(self.mininet_ip_to_host_map)
        logging.info("CybORGMininetMapper initialized successfully.")
        # pdb.set_trace()

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