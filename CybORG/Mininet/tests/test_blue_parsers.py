import logging
import pytest
from unittest.mock import Mock, patch


from typing import Dict

from CybORG.Shared import Observation

from CybORG.Mininet.mininet_adapter.utils.parse_blue_results_util import parse_decoy_action, \
    parse_remove_action, parse_reset_action, parse_reset_action_v2, parse_analyse_action
    
@pytest.fixture
def reset_action_output():
    # return "{\n'/tmp/lan1h2/ubuntu/file4.txt': '05b28d68132082ee549f5a415eb6c8de',\n'/tmp/lan1h2/ubuntu/file1.txt': 'b3a07c8b2fcc98559993b7575168e4ea',\n'/tmp/lan1h2/ubuntu/file5.txt': 'c944cf3f2d850bbc93ba28e63245e0dd',\n'/tmp/lan1h2/ubuntu/file0.txt': '2ab0c5d77ee9d3f45ab9876c539e20dc',\n'/tmp/lan1h2/ubuntu/file2.txt': '296f42303bbfe60fa6b1b77c0daa5370',\n'/tmp/lan1h2/ubuntu/file3.txt': '6096517e3f230cc9850a748c4cbcc4d9'\n}"
    return "{'/tmp/lan1h2/ubuntu/file4.txt': '05b28d68132082ee549f5a415eb6c8de','/tmp/lan1h2/ubuntu/file1.txt': 'b3a07c8b2fcc98559993b7575168e4ea','/tmp/lan1h2/ubuntu/file5.txt': 'c944cf3f2d850bbc93ba28e63245e0dd','/tmp/lan1h2/ubuntu/file0.txt': '2ab0c5d77ee9d3f45ab9876c539e20dc','/tmp/lan1h2/ubuntu/file2.txt': '296f42303bbfe60fa6b1b77c0daa5370','/tmp/lan1h2/ubuntu/file3.txt': '6096517e3f230cc9850a748c4cbcc4d9'}"

def test_parse_reset_action_v2(reset_action_output):
    obs = parse_reset_action_v2(reset_action_output)
    assert obs.data.get('MD5', {}) == {        
        '/tmp/lan1h2/ubuntu/file4.txt': '05b28d68132082ee549f5a415eb6c8de',
        '/tmp/lan1h2/ubuntu/file1.txt': 'b3a07c8b2fcc98559993b7575168e4ea',
        '/tmp/lan1h2/ubuntu/file5.txt': 'c944cf3f2d850bbc93ba28e63245e0dd',
        '/tmp/lan1h2/ubuntu/file0.txt': '2ab0c5d77ee9d3f45ab9876c539e20dc',
        '/tmp/lan1h2/ubuntu/file2.txt': '296f42303bbfe60fa6b1b77c0daa5370',
        '/tmp/lan1h2/ubuntu/file3.txt': '6096517e3f230cc9850a748c4cbcc4d9'
        }
    assert obs.success.name == "TRUE"