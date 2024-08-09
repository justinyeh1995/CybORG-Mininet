import re
import traceback 
import random
from typing import List, Dict, Iterator, Pattern
from ipaddress import IPv4Address, IPv4Network

from CybORG.Shared import Observation
from CybORG.Emulator.Observations.Velociraptor.AnalyseObservation import AnalyseObservation

from CybORG.Mininet.AdapterComponents.utils.parse_red_results_util import enum_to_boolean

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


def parse_reset_action(reset_action_output: str) -> Observation:
    '''
    md5 chksum are: {'/tmp/lan1h1/ubuntu/file6.txt': '2ed1da9e5db09fa95f42eacf0f203c88', '/tmp/lan1h1/ubuntu/file0.txt': '55bb703ba889096db15b539a1141c109', '/tmp/lan1h1/ubuntu/file5.txt': '36a9d8ed8066b9094ff73ac221d585fb', '/tmp/lan1h1/ubuntu/file1.txt': 'f4bdbfe06a7dbf5aaaa71ddd625f9881', '/tmp/lan1h1/ubuntu/file4.txt': '60f46204641696f89c34ca6c3a665131', '/tmp/lan1h1/ubuntu/file2.txt': '0ede6689285a69a30ec1e5131b3f721a', '/tmp/lan1h1/ubuntu/file3.txt': '0556da718ead47d7e4e178d80f0ff1cf'}
    turn this string into a dictionary
    '''
    test = "md5 chksum are: {'/tmp/lan1h1/ubuntu/file6.txt': '2ed1da9e5db09fa95f42eacf0f203c88', '/tmp/lan1h1/ubuntu/file0.txt': '55bb703ba889096db15b539a1141c109', '/tmp/lan1h1/ubuntu/file5.txt': '36a9d8ed8066b9094ff73ac221d585fb', '/tmp/lan1h1/ubuntu/file1.txt': 'f4bdbfe06a7dbf5aaaa71ddd625f9881', '/tmp/lan1h1/ubuntu/file4.txt': '60f46204641696f89c34ca6c3a665131', '/tmp/lan1h1/ubuntu/file2.txt': '0ede6689285a69a30ec1e5131b3f721a', '/tmp/lan1h1/ubuntu/file3.txt': '0556da718ead47d7e4e178d80f0ff1cf'}"
    pattern = r"md5 chksum are: ({.*})"
    match = re.search(pattern, reset_action_output)
    if match:
        md5_dict: Dict = eval(match.group(1))
        obs = Observation(True)
        obs.data.update({"MD5": md5_dict})
        return obs
    else:
        return Observation(False)

def parse_reset_action_v2(reset_action_output: str) -> Observation:
    example_text = "{'/tmp/lan1h2/ubuntu/file4.txt': '05b28d68132082ee549f5a415eb6c8de','/tmp/lan1h2/ubuntu/file1.txt': 'b3a07c8b2fcc98559993b7575168e4ea','/tmp/lan1h2/ubuntu/file5.txt': 'c944cf3f2d850bbc93ba28e63245e0dd','/tmp/lan1h2/ubuntu/file0.txt': '2ab0c5d77ee9d3f45ab9876c539e20dc','/tmp/lan1h2/ubuntu/file2.txt': '296f42303bbfe60fa6b1b77c0daa5370','/tmp/lan1h2/ubuntu/file3.txt': '6096517e3f230cc9850a748c4cbcc4d9'}"
    
    pattern = r"({.*})"
    match = re.search(pattern, reset_action_output)
    if match:
        md5_dict: Dict = eval(match.group(1))
        obs = Observation(True)
        obs.data.update({"MD5": md5_dict})
        return obs
    else:
        return Observation(False)
    
    
def parse_analyse_action(analyse_action_output: str) -> Observation:
    
    # Use re.search to find a match
    # match_dict_string = re.search(r"Previous MD5SUM: (\{[^}]+\})\s+Current MD5SUM: (\{[^}]+\})\s+Densityscout: (\{[^}]+\})", analyse_action_output)
    match_previous_md5sum = re.search(r"Previous MD5SUM: (\{[^}]+\})", analyse_action_output)
    match_current_md5sum = re.search(r"Current MD5SUM: (\{[^}]+\})", analyse_action_output)
    match_densityscout = re.search(r"Densityscout: (\{[^}]+\})", analyse_action_output)
    
    # import pdb; pdb.set_trace()
    # Extract the dictionary string if found
    if match_previous_md5sum and match_current_md5sum and match_densityscout:
        previous_verification_dict = eval(match_previous_md5sum.group(1)) 
        current_verification_dict = eval(match_current_md5sum.group(1)) 
        density_scout_dict = {file_name: float(density_str) for file_name, density_str in eval(match_densityscout.group(1)).items()}
        
    
        obs = AnalyseObservation(current_verification_dict, previous_verification_dict, density_scout_dict)
    else:
        obs = Observation(False)
        
    return obs

def parse_remove_action(remove_action_string: str) -> Observation:
    pattern = re.compile(r'TRUE|FALSE')

    # Use re.search to find a match
    match = pattern.search(remove_action_string)
    
    # Extract the 'TRUE' or 'FALSE' part if found
    success_status = enum_to_boolean(match.group()) if match else None
    
    obs = Observation(success_status)
    
    return obs
