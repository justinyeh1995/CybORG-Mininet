import re
import traceback 
from typing import List, Dict, Iterator, Pattern
from ipaddress import IPv4Address, IPv4Network

from CybORG.Shared import Observation
from CybORG.Mininet.mininet_adapter.utils.parse_red_results_util import enum_to_boolean

def parse_remove_action(remove_action_string: str) -> Observation:
    pattern = re.compile(r'TRUE|FALSE')

    # Use re.search to find a match
    match = pattern.search(remove_action_string)
    
    # Extract the 'TRUE' or 'FALSE' part if found
    success_status = enum_to_boolean(match.group()) if match else None
    
    obs = Observation(success_status)
    
    return obs

def parse_decoy_action(decoy_action_output) -> Observation:
    pattern = re.compile(r'TRUE|FALSE')

    # Use re.search to find a match
    match = pattern.search(decoy_action_output)
    
    # Extract the 'TRUE' or 'FALSE' part if found
    success_status = enum_to_boolean(match.group()) if match else None
    
    # print(f"Match is: {match} \n")
    
    return Observation(success_status)