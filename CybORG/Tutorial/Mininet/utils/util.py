import re
import collections
from typing import Iterator, Pattern, Tuple, Dict, List
from ipaddress import IPv4Address, IPv4Network

def set_name_map(cyborg) -> Dict:
    cyborg_to_mininet_name_map = collections.defaultdict(str)
    
    for cnt, (lan_name, network) in enumerate(cyborg.get_cidr_map().items()):
            cyborg_to_mininet_name_map[lan_name] = f'lan{cnt+1}'
            cyborg_to_mininet_name_map[f'{lan_name}_router'] = f'r{cnt+1}'
        
    return cyborg_to_mininet_name_map


def get_routers_info(cyborg, cyborg_to_mininet_name_map) -> List:
    """
    Assume the router names are suffixed with '_router'
    """
    return [{'router': cyborg_to_mininet_name_map[name], 
             'ip': str(ip)} for name, ip in cyborg.get_ip_map().items() if name.endswith('_router')]


def get_lans_info(cyborg, cyborg_to_mininet_name_map) -> List:
    lans_info = []
    # Create LANs based on the networks
    for lan_name, network in cyborg.get_cidr_map().items():
        hosts = [name for name, ip in cyborg.get_ip_map().items() if ip in network and not name.endswith('_router')]
        hosts_info = { f'h{i+1}': str(cyborg.get_ip_map()[name]) for i, name in enumerate(hosts)}
        lans_info.append({
            'name': cyborg_to_mininet_name_map[lan_name],
            'router': cyborg_to_mininet_name_map[f'{lan_name}_router'],
            'subnet': str(network),
            'hosts': len(hosts),
            'hosts_info': hosts_info
        })
    return lans_info


def get_router2router_links(cyborg) -> List:
    """
    Filter only for router-to-router links
    """
    edge_view = cyborg.environment_controller.state.link_diagram.edges
    routers = {node for edge in edge_view for node in edge if node.endswith('_router')}

    return [edge for edge in cyborg.environment_controller.state.link_diagram.edges if all(node in routers for node in edge)]


def get_links_info(cyborg, cyborg_to_mininet_name_map) -> List:
    router_links = get_router2router_links(cyborg)
    links_info = []
    for i, link in enumerate(router_links):
        ep1, ep2 = link
        # Assuming you have a function or a way to get the subnet for a given link
        subnet = str(IPv4Network(f'10.{50*(i+1)}.1.0/28'))  # Placeholder, replace with your subnet logic # needs fix
        links_info.append({
            'ep1-router': cyborg_to_mininet_name_map[ep1],
            'ep2-router': cyborg_to_mininet_name_map[ep2],
            'subnet': subnet
        })
    return links_info


def parse_action(cyborg, action_str, agent, ip_to_host_map):
    action_type = action_str.split(" ")[0]
    target_host = ""
    isSuccess = cyborg.get_observation(agent)['success'].__str__()
    if isSuccess == 'TRUE':
        action_str_split = action_str.split(" ")
        n = len(action_str_split)
        target_host = action_str_split[-1] if n > 1 else target_host
        # Update target host if it's an IP address to get the hostname
        target_host = ip_to_host_map.get(target_host, target_host) #if target_host in ip_to_host_map else target_host
        # target_host = 
    return target_host, action_type, isSuccess


def find_matches(pattern_str: str, raw_text: str) -> Iterator[re.Match]:
    # Define a regex pattern to extract hostnames and IP addresses
    pattern: Pattern = re.compile(pattern_str)
    
    # Find all matches in the decoded output
    match: Iterator[re.Match] = pattern.finditer(raw_text)
    
    return match


def parse_mininet_ip(raw_text: str) -> list:
    pattern_str1: str = r'(Router):\s+(?P<host>\S+)\s+with IP:\s+(?P<ip>\S+)'
    pattern_str2: str = r'(Host)\s+(?P<host>\S+)\s+with IP:\s+(?P<ip>\S+)'
    
    # Find all matches in the decoded output
    matches1: Iterator[re.Match] = find_matches(pattern_str1, raw_text)
    matches2: Iterator[re.Match] = find_matches(pattern_str2, raw_text)

    # Convert match iterators to lists and concatenate them
    matches: list = list(matches1) + list(matches2)

    return matches



def translate_discover_remote_systems(subnet):
    pass

def translate_discover_network_services(subnet):
    pass

def translate_exploit_network_services(ip_address, port):
    pass

def translate_restore(ip_address):
    pass

def translate_remove(ip_address, port):
    pass
    