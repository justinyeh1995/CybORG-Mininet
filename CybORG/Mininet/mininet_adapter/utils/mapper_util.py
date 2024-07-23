import re
import collections
from pprint import pprint
from typing import Iterator, Pattern, Dict
from CybORG.Mininet.mininet_api import custom_utils as cu

###########################
# CybORG-2-Mininet Mapper #
###########################

def find_matches(pattern_str: str, raw_text: str) -> Iterator[re.Match]:
    # Define a regex pattern to extract hostnames and IP addresses
    pattern: Pattern = re.compile(pattern_str)
    
    # Find all matches in the decoded output
    match: Iterator[re.Match] = pattern.finditer(raw_text)
    
    return match

def build_cyborg_to_mininet_name_map(cyborg) -> Dict:
    cyborg_to_mininet_name_map = collections.defaultdict(str)
    
    for cnt, (lan_name, network) in enumerate(cyborg.environment_controller.subnet_cidr_map.items()):
            cyborg_to_mininet_name_map[lan_name] = f'lan{cnt+1}'
            cyborg_to_mininet_name_map[f'{lan_name}_router'] = f'r{cnt+1}'
        
    return cyborg_to_mininet_name_map


def parse_mininet_ip(raw_text: str) -> list:
    pattern_str1: str = r'(Router):\s+(?P<host>\S+)\s+with IP:\s+(?P<ip>\S+)'
    pattern_str2: str = r'(Host)\s+(?P<host>\S+)\s+with IP:\s+(?P<ip>\S+)'
    pattern_str3: str = r'(NAT)\s+(?P<host>\S+) with IP: (?P<ip>\S+)'

    # Find all matches in the decoded output
    matches1: Iterator[re.Match] = find_matches(pattern_str1, raw_text)
    matches2: Iterator[re.Match] = find_matches(pattern_str2, raw_text)
    matches3: Iterator[re.Match] = find_matches(pattern_str3, raw_text)
    # Convert match iterators to lists and concatenate them
    matches: list = list(matches1) + list(matches2) + list(matches3)

    return matches


def build_mininet_host_to_cyborg_ip_map(topology):
    mininet_host_to_cyborg_ip_map = {}
    for entry in topology["topo"]['lans']:
        lan_name = entry['name']
        for host, ip in entry['hosts_info'].items():
            mininet_host_to_cyborg_ip_map[f"{lan_name}{host}"] = ip
        mininet_host_to_cyborg_ip_map[entry['router']] = entry['router_ip']
    return mininet_host_to_cyborg_ip_map


def build_cyborg_ip_to_mininet_host_map(topology):
    cyborg_ip_to_mininet_host_map = {}
    for entry in topology["topo"]['lans']:
        lan_name = entry['name']
        for host, ip in entry['hosts_info'].items():
            cyborg_ip_to_mininet_host_map[ip] = f"{lan_name}{host}"
        cyborg_ip_to_mininet_host_map[entry['router_ip']] = entry['router']
    return cyborg_ip_to_mininet_host_map