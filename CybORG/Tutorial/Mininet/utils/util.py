import re
from typing import Iterator, Pattern, Tuple

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


def get_matches(pattern_str: str, raw_text: str) -> Iterator[re.Match]:
    # Define a regex pattern to extract hostnames and IP addresses
    pattern: Pattern = re.compile(pattern_str)
    
    # Find all matches in the decoded output
    match: Iterator[re.Match] = pattern.finditer(raw_text)
    
    return match


def get_all_matches(raw_text: str) -> list:
    pattern_str1: str = r'(Router):\s+(?P<host>\S+)\s+with IP:\s+(?P<ip>\S+)'
    pattern_str2: str = r'(Host)\s+(?P<host>\S+)\s+with IP:\s+(?P<ip>\S+)'
    
    # Find all matches in the decoded output
    matches1: Iterator[re.Match] = get_matches(pattern_str1, raw_text)
    matches2: Iterator[re.Match] = get_matches(pattern_str2, raw_text)

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
    