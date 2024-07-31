import pytest
from unittest.mock import Mock, patch

from typing import Dict

from CybORG.Shared import Observation

from CybORG.Mininet.mininet_adapter.utils.parse_red_results_util import parse_nmap_network_scan_v2, \
    parse_nmap_port_scan, parse_nmap_network_scan_v2, parse_exploit_action, parse_escalate_action

@pytest.fixture
def discover_network_scan_output():
    return ''' lan3h1 timeout 60 nmap -oX - -sn 10.0.37.224/28
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE nmaprun>
<?xml-stylesheet href="file:///usr/bin/../share/nmap/nmap.xsl" type="text/xsl"?>
<!-- Nmap 7.80 scan initiated Tue Jul 30 20:33:36 2024 as: nmap -oX - -sn 10.0.37.224/28 -->
<nmaprun scanner="nmap" args="nmap -oX - -sn 10.0.37.224/28" start="1722389616" startstr="Tue Jul 30 20:33:36 2024" version="7.80" xmloutputversion="1.04">
<verbose level="0"/>
<debugging level="0"/>
<host><status state="up" reason="arp-response" reason_ttl="0"/>
<address addr="10.0.37.225" addrtype="ipv4"/>
<address addr="F6:ED:4C:E4:19:D6" addrtype="mac"/>
<hostnames>
</hostnames>
<times srtt="5501" rttvar="5501" to="100000"/>
</host>
<host><status state="up" reason="arp-response" reason_ttl="0"/>
<address addr="10.0.37.226" addrtype="ipv4"/>
<address addr="FE:C6:E0:B2:AB:E1" addrtype="mac"/>
<hostnames>
</hostnames>
<times srtt="4128" rttvar="5000" to="100000"/>
</host>
<host><status state="up" reason="arp-response" reason_ttl="0"/>
<address addr="10.0.37.227" addrtype="ipv4"/>
<address addr="56:AB:71:1F:B7:03" addrtype="mac"/>
<hostnames>
</hostnames>
<times srtt="4114" rttvar="5000" to="100000"/>
</host>
<host><status state="up" reason="arp-response" reason_ttl="0"/>
<address addr="10.0.37.228" addrtype="ipv4"/>
<address addr="42:78:7F:F2:0F:64" addrtype="mac"/>
<hostnames>
</hostnames>
<times srtt="4191" rttvar="5000" to="100000"/>
</host>
<host><status state="up" reason="arp-response" reason_ttl="0"/>
<address addr="10.0.37.229" addrtype="ipv4"/>
<address addr="4E:2B:9F:0D:FD:F9" addrtype="mac"/>
<hostnames>
</hostnames>
<times srtt="5236" rttvar="5236" to="100000"/>
</host>
<host><status state="up" reason="arp-response" reason_ttl="0"/>
<address addr="10.0.37.238" addrtype="ipv4"/>
<address addr="72:19:F6:95:25:3D" addrtype="mac"/>
<hostnames>
</hostnames>
<times srtt="9319" rttvar="9319" to="100000"/>
</host>
<host><status state="up" reason="localhost-response" reason_ttl="0"/>
<address addr="10.0.37.234" addrtype="ipv4"/>
<hostnames>
</hostnames>
</host>
<runstats><finished time="1722389642" timestr="Tue Jul 30 20:34:02 2024" elapsed="26.31" summary="Nmap done at Tue Jul 30 20:34:02 2024; 16 IP addresses (7 hosts up) scanned in 26.31 seconds" exit="success"/><hosts up="7" down="9" total="16"/>
</runstats>
</nmaprun>
'''

class FakeMapper:
    def __init__(self):
        self.cyborg_ip_to_host_map: Dict[str, str] = {}

    def add_ip_host_mapping(self, ip: str, host: str):
        self.cyborg_ip_to_host_map[ip] = host

def fake_mapper():
    mapper = FakeMapper()
    # Add some default mappings
    mapper.add_ip_host_mapping('10.0.37.225', 'host1')
    mapper.add_ip_host_mapping('10.0.37.226', 'host2')
    mapper.add_ip_host_mapping('10.0.37.227', 'router1')
    mapper.add_ip_host_mapping('10.0.37.228', 'host3')
    return mapper

# @pytest
def test_parse_nmap_network_scan_v2(discover_network_scan_output):
    mapper = fake_mapper()
    obs: Observation = parse_nmap_network_scan_v2(discover_network_scan_output, '10.0.37.224/28', mapper)
    print(obs.data)

    assert obs.success.name == "TRUE", "Success should be 'TRUE' if the scan was successful"
        
    assert len(obs.data) == len(mapper.cyborg_ip_to_host_map)+1, "Should have a data entry for each host and one for the suceess status"
    assert 'host1' in obs.data, "Should have data for host1"
    assert 'host2' in obs.data, "Should have data for host2"