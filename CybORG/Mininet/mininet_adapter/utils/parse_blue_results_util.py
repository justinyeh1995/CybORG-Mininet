import re
import traceback 
import random
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

def parse_decoy_action(decoy_action_output: str) -> Observation:
    pattern = re.compile(r'TRUE|FALSE')

    # Use re.search to find a match
    match = pattern.search(decoy_action_output)
    
    # Extract the 'TRUE' or 'FALSE' part if found
    success_status = enum_to_boolean(match.group()) if match else None
    
    obs = Observation(success_status)
    
    pattern_decoyname = r"Decoied Service:\s+(\w+)"
    match_decoyname = re.search(pattern_decoyname, decoy_action_output)
    decoyname = match_decoyname.group(1) if match_decoyname else None
    
    pattern_host = r"Decoy Deployed Hostname:\s+(\w+)"
    match_host = re.search(pattern_host, decoy_action_output)
    host = match_host.group(1) if match_host else None
    
    # print(f"Match is: {match} \n")
    data = {'host': host,
        'username': 'root',
        'decoyname': decoyname,
        }
    formatted_data = transform_decoy(data)
    obs.data.update(formatted_data)
    
    return obs


def transform_decoy(data):
    # TO do : Remove PID and PPID as fixed to fetch from process and update 
    #       : If possible remove the propertiesa and set it during the decoy set up to lure/honeytrap. 
    #       : Remove the faked decoys that is not part of linux type decoys. 
    #print('Data is:',data)
    formatted_data= {}
    host=data['host']
    username=data['username']
    decoyname=data['decoyname']

    decoyname= decoyname.lower()
    formatted_data[host] = {
            'Processes': [
                {
                    'PID': random.randint(1000,5000),  # Static PID since it's not provided in the input
                    'PPID': 1,                # Static PPID since it's not provided in the input
                    'Service Name': decoyname,  # Assuming a static service name; replace if variable
                    'Username': username
                }
            ]
        }

    #Decoy specific modification
    if decoyname=='tomcat':
        formatted_data[host]['Processes'][0]['Properties']=['rfi']
    elif decoyname=='femitter':
        formatted_data[host]['Processes'][0]['Username']='SYSTEM'
    elif decoyname=='harakasmpt': 
        formatted_data[host]['Processes'][0]['Service Name']='haraka'
    return formatted_data
