import pytest
import inspect

from unittest.mock import Mock, patch
from CybORG.Mininet.AdapterComponents.results_bundler import parse_exploit_action

@pytest.fixture
def complex_exploit_output():
    return ''' lan3h1 timeout 60 /home/ubuntu/justinyeh1995/CASTLEGym/castle.2.venv/bin/python3 /home/ubuntu/justinyeh1995/CASTLEGym/CybORG/CybORG/Mininet/actions/exploit_action.py --hostname cpswtjustin --remote_hostname 10.0.230.177\r\ntcp   ESTAB  0      0       10.0.230.177:22    10.0.214.188\x1b[01;31m\x1b[K:4444\x1b[m\x1b[K users:(("sshd",pid=120688,fd=4))           \r\r\n and its type is: <class \'str\'>\r\nSuccess is: TRUE\r\nConnection Key is: ZY6TI3OJCR\r\nMalicious file written?: File written.\r\r\n\r\nExploit is: FTPDirTraversal\r\nconnection info string is: tcp   ESTAB  0      0       10.0.230.177:22    10.0.214.188\x1b[01;31m\x1b[K:4444\x1b[m\x1b[K users:(("sshd",pid=120688,fd=4))           \r\r\n\r\nPlease clean the mess after test!!\r\n'''

@pytest.fixture
def mock_mapper():
    mapper = Mock()
    # Configure the mock mapper with any necessary behavior
    mapper.get_ip.return_value = '10.0.230.177'
    return mapper

@pytest.main
def test_parse_exploit_action(test_exploit_string):
    """test parse_exploit_action function"""
    # obs = parse_exploit_action(test_exploit_string)

import re

def parse_complex_exploit_output(output: str) -> dict:
    # Remove ANSI escape codes
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    output = ansi_escape.sub('', output)

    # Split the output into lines
    lines = output.split('\n')

    # Initialize the result dictionary
    result = {}

    # Parse the connection info
    connection_info = next((line for line in lines if line.startswith('tcp')), '')
    if connection_info:
        match = re.search(r'(\d+\.\d+\.\d+\.\d+):(\d+)\s+(\d+\.\d+\.\d+\.\d+):(\d+).*pid=(\d+)', connection_info)
        if match:
            result['ip1'], result['port1'], result['ip2'], result['port2'], result['pid'] = match.groups()

    # Extract other information
    for line in lines:
        if 'Success is:' in line:
            result['success'] = line.split(':')[-1].strip()
        elif 'Connection Key is:' in line:
            result['connection_key'] = line.split(':')[-1].strip()
        elif 'Malicious file written?:' in line:
            result['malicious_file_written'] = line.split(':')[-1].strip()
        elif 'Exploit is:' in line:
            result['exploit'] = line.split(':')[-1].strip()

    return result

# Test the function
result = parse_complex_exploit_output(test_exploit_string)
print(result)

