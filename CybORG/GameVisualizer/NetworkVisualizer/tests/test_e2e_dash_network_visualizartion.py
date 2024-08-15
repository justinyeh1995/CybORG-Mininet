import pytest
import networkx as nx
from CybORG.GameVisualizer.NetworkVisualizer import DashNetworkVisualizer

#Realistic mock data based on the provided step results
mock_agent_game_states = {
    10: {  # num_steps
        "RedAgent": {  # red_agent_name
            0: {  # episode
                0: {  # step
                    "Blue": {
                        "mode": "defend",
                        "link_diagram": nx.node_link_graph({
                            "directed": False,
                            "multigraph": False,
                            "graph": {},
                            "nodes": [{"id": node} for node in [
                                "Defender", "Enterprise0", "Enterprise1", "Enterprise2",
                                "Op_Host0", "Op_Host1", "Op_Host2", "Op_Server0",
                                "User0", "User1", "User2", "User3", "User4",
                                "Enterprise_router", "Operational_router", "User_router"
                            ]],
                            "links": [
                                {"source": "Defender", "target": "Enterprise_router"},
                                {"source": "Enterprise0", "target": "Enterprise_router"},
                                {"source": "Enterprise1", "target": "Enterprise_router"},
                                {"source": "Enterprise2", "target": "Enterprise_router"},
                                {"source": "Op_Host0", "target": "Operational_router"},
                                {"source": "Op_Host1", "target": "Operational_router"},
                                {"source": "Op_Host2", "target": "Operational_router"},
                                {"source": "Op_Server0", "target": "Operational_router"},
                                {"source": "User0", "target": "User_router"},
                                {"source": "User1", "target": "User_router"},
                                {"source": "User2", "target": "User_router"},
                                {"source": "User3", "target": "User_router"},
                                {"source": "User4", "target": "User_router"},
                                {"source": "Enterprise_router", "target": "Operational_router"},
                                {"source": "Enterprise_router", "target": "User_router"},
                                {"source": "Operational_router", "target": "User_router"}
                            ]
                        }),
                        "node_positions": [
                            {"id": "Defender", "x": 0.29207032470114147, "y": 0.6243130116259841, "z": -0.7571677384781477},
                            {"id": "Enterprise0", "x": 0.011012400327767282, "y": -0.22669611021674632, "z": -0.9979540830837798},
                            # ... (include all node positions)
                        ],
                        "node_colors": ["green", "green", "green", "green", "green", "green", "green", "green", "red", "green", "green", "green", "green", "green", "green", "green"],
                        "node_borders": [{"width": 0, "color": "white"} for _ in range(16)],
                        "compromised_hosts": ["User0"],
                        "host_info": [
                            "System info:<br>LINUX UBUNTU (x64)<br><br>Processes info:<br>- init (PID: 1, User: root, )<br>- systemd-journald (PID: 389, User: root, )<br>- systemd-udevd (PID: 407, User: root, )<br>- lvmetad (PID: 409, User: root, )<br>- systemd-timesyncd (PID: 560, User: systemd+, )<br>- accounts-daemon (PID: 790, User: root, )<br>- atd (PID: 802, User: daemon, )<br>- bash (PID: 803, User: velocir+, )<br>- rsyslogd (PID: 807, User: syslog, )<br>- acpid (PID: 824, User: root, )<br>- snapd (PID: 825, User: root, )<br>- dbus-daemon (PID: 827, User: message+, )<br>- velociraptor.bin (PID: 832, User: velocir+, )<br>- cron (PID: 844, User: root, )<br>- systemd-logind (PID: 847, User: root, )<br>- python3 (PID: 852, User: root, )<br>- lxcfs (PID: 853, User: root, )<br>- polkitd (PID: 863, User: root, )<br>- python3 (PID: 867, User: root, )<br>- agetty (PID: 875, User: root, )<br>- agetty (PID: 884, User: root, )<br>- python3 (PID: 1370, User: root, )<br>- systemd-hostnamed (PID: 1432, User: root, )<br>- sshd (PID: 2288, User: root, )<br>- sshd (PID: 879, User: root, Port: 22)<br>- systemd-resolved (PID: 656, User: systemd+, Port: 53, Port: 53)<br>- systemd-networkd (PID: 634, User: systemd+, Port: 68)<br>- VelociraptorServer (PID: 2296, User: ubuntu, )<br>- VelociraptorClient (PID: 2303, User: ubuntu, )<br>",
                            "System info:<br>LINUX UBUNTU (x64)<br><br>Processes info:<br>- sshd (PID: 1091, User: root, Port: 22)<br>- VelociraptorClient (PID: 1093, User: ubuntu, )<br>",
                            "System info:<br>WINDOWS WINDOWS_SVR_2008 (x64)<br><br>Processes info:<br>- sshd.exe (PID: 3368, User: sshd_server, Port: 22)<br>- svchost.exe (PID: 832, User: SYSTEM, Port: 135)<br>- svchost.exe (PID: 4400, User: SYSTEM, Port: 3389)<br>- smss.exe (PID: 4, User: SYSTEM, Port: 445, Port: 139)<br>- tomcat8.exe (PID: 3404, User: NetworkService, Port: 80, Port: 443)<br>- VelociraptorClient (PID: 4408, User: SYSTEM, )<br>",
                            "System info:<br>WINDOWS WINDOWS_SVR_2008 (x64)<br><br>Processes info:<br>- sshd.exe (PID: 3368, User: sshd_server, Port: 22)<br>- svchost.exe (PID: 832, User: SYSTEM, Port: 135)<br>- svchost.exe (PID: 4400, User: SYSTEM, Port: 3389)<br>- smss.exe (PID: 4, User: SYSTEM, Port: 445, Port: 139)<br>- tomcat8.exe (PID: 3404, User: NetworkService, Port: 80, Port: 443)<br>- VelociraptorClient (PID: 4403, User: SYSTEM, )<br>",
                            "System info:<br>LINUX UBUNTU (x64)<br><br>Processes info:<br>- sshd (PID: 1091, User: root, Port: 22)<br>- VelociraptorClient (PID: 1096, User: ubuntu, )<br>- green_session (PID: 1104, User: GreenAgent, )<br>",
                            "System info:<br>LINUX UBUNTU (x64)<br><br>Processes info:<br>- sshd (PID: 1091, User: root, Port: 22)<br>- VelociraptorClient (PID: 1095, User: ubuntu, )<br>- green_session (PID: 1101, User: GreenAgent, )<br>",
                            "System info:<br>LINUX UBUNTU (x64)<br><br>Processes info:<br>- sshd (PID: 1091, User: root, Port: 22)<br>- VelociraptorClient (PID: 1093, User: ubuntu, )<br>- green_session (PID: 1095, User: GreenAgent, )<br>",
                            "System info:<br>LINUX UBUNTU (x64)<br><br>Processes info:<br>- sshd (PID: 1091, User: root, Port: 22)<br>- OTService (PID: 1043, User: root, )<br>- VelociraptorClient (PID: 1094, User: ubuntu, )<br>",
                            "System info:<br>WINDOWS WINDOWS_SVR_2008 (x64)<br><br>Processes info:<br>- sshd.exe (PID: 3368, User: sshd_server, Port: 22)<br>- femitter.exe (PID: 3344, User: SYSTEM, Port: 21)<br>- VelociraptorClient (PID: 3370, User: ubuntu, )<br>- green_session (PID: 3376, User: GreenAgent, )<br>- RedAbstractSession (PID: 3379, User: SYSTEM, )<br>",
                            "System info:<br>WINDOWS WINDOWS_SVR_2008 (x64)<br><br>Processes info:<br>- sshd.exe (PID: 3368, User: sshd_server, Port: 22)<br>- femitter.exe (PID: 3344, User: SYSTEM, Port: 21)<br>- VelociraptorClient (PID: 3376, User: ubuntu, )<br>- green_session (PID: 3385, User: GreenAgent, )<br>",
                            "System info:<br>WINDOWS WINDOWS_SVR_2008 (x64)<br><br>Processes info:<br>- smss.exe (PID: 4, User: SYSTEM, Port: 445, Port: 139)<br>- svchost.exe (PID: 832, User: SYSTEM, Port: 135)<br>- svchost.exe (PID: 4400, User: NetworkService, Port: 3389)<br>- VelociraptorClient (PID: 4405, User: ubuntu, )<br>- green_session (PID: 4410, User: GreenAgent, )<br>",
                            "System info:<br>LINUX UBUNTU (x64)<br><br>Processes info:<br>- mysql (PID: 1101, User: root, Port: 3389)<br>- apache2 (PID: 1100, User: www-data, Port: 80, Port: 443)<br>- smtp (PID: 1102, User: root, Port: 25)<br>- VelociraptorClient (PID: 1108, User: ubuntu, )<br>- green_session (PID: 1114, User: GreenAgent, )<br>",
                            "System info:<br>LINUX UBUNTU (x64)<br><br>Processes info:<br>- sshd (PID: 1091, User: root, Port: 22)<br>- mysql (PID: 1101, User: root, Port: 3390)<br>- apache2 (PID: 1100, User: www-data, Port: 80, Port: 443)<br>- smtp (PID: 1102, User: root, Port: 25)<br>- VelociraptorClient (PID: 1107, User: ubuntu, )<br>- green_session (PID: 1111, User: GreenAgent, )<br>",
                            "",
                            "",
                            ""
                        ],
                        "action_info": {
                            "action": "at Host Defender do Monitor on the whole network",
                            "success": True
                        },
                        "host_map": {
                            "Defender": "10.0.112.39",
                            "Enterprise0": "10.0.112.35",
                            "Enterprise1": "10.0.112.38",
                            "Enterprise2": "10.0.112.45",
                            "Op_Host0": "10.0.29.99",
                            "Op_Host1": "10.0.29.105",
                            "Op_Host2": "10.0.29.101",
                            "Op_Server0": "10.0.29.98",
                            "User0": "10.0.185.235",
                            "User1": "10.0.185.237",
                            "User2": "10.0.185.236",
                            "User3": "10.0.185.225",
                            "User4": "10.0.185.232",
                            "Enterprise_router": "10.0.112.40",
                            "Operational_router": "10.0.29.104",
                            "User_router": "10.0.185.231"
                        },
                        "obs": {},
                        "reward": 0,
                        "accumulate_reward": 0,
                    },
                    "Red": {
                        "mode": "attack",
                        "link_diagram": nx.node_link_graph({
                            "directed": False,
                            "multigraph": False,
                            "graph": {},
                            "nodes": [{"id": node} for node in [
                                "Defender", "Enterprise0", "Enterprise1", "Enterprise2",
                                "Op_Host0", "Op_Host1", "Op_Host2", "Op_Server0",
                                "User0", "User1", "User2", "User3", "User4",
                                "Enterprise_router", "Operational_router", "User_router"
                            ]],
                            "links": [
                                {"source": "Defender", "target": "Enterprise_router"},
                                {"source": "Enterprise0", "target": "Enterprise_router"},
                                {"source": "Enterprise1", "target": "Enterprise_router"},
                                {"source": "Enterprise2", "target": "Enterprise_router"},
                                {"source": "Op_Host0", "target": "Operational_router"},
                                {"source": "Op_Host1", "target": "Operational_router"},
                                {"source": "Op_Host2", "target": "Operational_router"},
                                {"source": "Op_Server0", "target": "Operational_router"},
                                {"source": "User0", "target": "User_router"},
                                {"source": "User1", "target": "User_router"},
                                {"source": "User2", "target": "User_router"},
                                {"source": "User3", "target": "User_router"},
                                {"source": "User4", "target": "User_router"},
                                {"source": "Enterprise_router", "target": "Operational_router"},
                                {"source": "Enterprise_router", "target": "User_router"},
                                {"source": "Operational_router", "target": "User_router"}
                            ]
                        }),
                        "node_positions": [
                            {"id": "Defender", "x": 0.29207032470114147, "y": 0.6243130116259841, "z": -0.7571677384781477},
                            {"id": "Enterprise0", "x": 0.011012400327767282, "y": -0.22669611021674632, "z": -0.9979540830837798},
                            # ... (include all node positions)
                        ],
                        "node_colors": ["green", "green", "green", "green", "green", "green", "green", "green", "red", "green", "green", "green", "green", "green", "green", "rosybrown"],
                        "node_borders": [{"width": 0, "color": "white"} for _ in range(15)] + [{"width": 2, "color": "black"}],
                        "compromised_hosts": ["User0"],
                        "host_info": [
                            "System info:<br>LINUX UBUNTU (x64)<br><br>Processes info:<br>- init (PID: 1, User: root, )<br>- systemd-journald (PID: 389, User: root, )<br>- systemd-udevd (PID: 407, User: root, )<br>- lvmetad (PID: 409, User: root, )<br>- systemd-timesyncd (PID: 560, User: systemd+, )<br>- accounts-daemon (PID: 790, User: root, )<br>- atd (PID: 802, User: daemon, )<br>- bash (PID: 803, User: velocir+, )<br>- rsyslogd (PID: 807, User: syslog, )<br>- acpid (PID: 824, User: root, )<br>- snapd (PID: 825, User: root, )<br>- dbus-daemon (PID: 827, User: message+, )<br>- velociraptor.bin (PID: 832, User: velocir+, )<br>- cron (PID: 844, User: root, )<br>- systemd-logind (PID: 847, User: root, )<br>- python3 (PID: 852, User: root, )<br>- lxcfs (PID: 853, User: root, )<br>- polkitd (PID: 863, User: root, )<br>- python3 (PID: 867, User: root, )<br>- agetty (PID: 875, User: root, )<br>- agetty (PID: 884, User: root, )<br>- python3 (PID: 1370, User: root, )<br>- systemd-hostnamed (PID: 1432, User: root, )<br>- sshd (PID: 2288, User: root, )<br>- sshd (PID: 879, User: root, Port: 22)<br>- systemd-resolved (PID: 656, User: systemd+, Port: 53, Port: 53)<br>- systemd-networkd (PID: 634, User: systemd+, Port: 68)<br>- VelociraptorServer (PID: 2296, User: ubuntu, )<br>- VelociraptorClient (PID: 2303, User: ubuntu, )<br>",
                            "System info:<br>LINUX UBUNTU (x64)<br><br>Processes info:<br>- sshd (PID: 1091, User: root, Port: 22)<br>- VelociraptorClient (PID: 1093, User: ubuntu, )<br>",
                            "System info:<br>WINDOWS WINDOWS_SVR_2008 (x64)<br><br>Processes info:<br>- sshd.exe (PID: 3368, User: sshd_server, Port: 22)<br>- svchost.exe (PID: 832, User: SYSTEM, Port: 135)<br>- svchost.exe (PID: 4400, User: SYSTEM, Port: 3389)<br>- smss.exe (PID: 4, User: SYSTEM, Port: 445, Port: 139)<br>- tomcat8.exe (PID: 3404, User: NetworkService, Port: 80, Port: 443)<br>- VelociraptorClient (PID: 4408, User: SYSTEM, )<br>",
                            "System info:<br>WINDOWS WINDOWS_SVR_2008 (x64)<br><br>Processes info:<br>- sshd.exe (PID: 3368, User: sshd_server, Port: 22)<br>- svchost.exe (PID: 832, User: SYSTEM, Port: 135)<br>- svchost.exe (PID: 4400, User: SYSTEM, Port: 3389)<br>- smss.exe (PID: 4, User: SYSTEM, Port: 445, Port: 139)<br>- tomcat8.exe (PID: 3404, User: NetworkService, Port: 80, Port: 443)<br>- VelociraptorClient (PID: 4403, User: SYSTEM, )<br>",
                            "System info:<br>LINUX UBUNTU (x64)<br><br>Processes info:<br>- sshd (PID: 1091, User: root, Port: 22)<br>- VelociraptorClient (PID: 1096, User: ubuntu, )<br>- green_session (PID: 1104, User: GreenAgent, )<br>",
                            "System info:<br>LINUX UBUNTU (x64)<br><br>Processes info:<br>- sshd (PID: 1091, User: root, Port: 22)<br>- VelociraptorClient (PID: 1095, User: ubuntu, )<br>- green_session (PID: 1101, User: GreenAgent, )<br>",
                            "System info:<br>LINUX UBUNTU (x64)<br><br>Processes info:<br>- sshd (PID: 1091, User: root, Port: 22)<br>- VelociraptorClient (PID: 1093, User: ubuntu, )<br>- green_session (PID: 1095, User: GreenAgent, )<br>",
                            "System info:<br>LINUX UBUNTU (x64)<br><br>Processes info:<br>- sshd (PID: 1091, User: root, Port: 22)<br>- OTService (PID: 1043, User: root, )<br>- VelociraptorClient (PID: 1094, User: ubuntu, )<br>",
                            "System info:<br>WINDOWS WINDOWS_SVR_2008 (x64)<br><br>Processes info:<br>- sshd.exe (PID: 3368, User: sshd_server, Port: 22)<br>- femitter.exe (PID: 3344, User: SYSTEM, Port: 21)<br>- VelociraptorClient (PID: 3370, User: ubuntu, )<br>- green_session (PID: 3376, User: GreenAgent, )<br>- RedAbstractSession (PID: 3379, User: SYSTEM, )<br>",
                            "System info:<br>WINDOWS WINDOWS_SVR_2008 (x64)<br><br>Processes info:<br>- sshd.exe (PID: 3368, User: sshd_server, Port: 22)<br>- femitter.exe (PID: 3344, User: SYSTEM, Port: 21)<br>- VelociraptorClient (PID: 3376, User: ubuntu, )<br>- green_session (PID: 3385, User: GreenAgent, )<br>",
                            "System info:<br>WINDOWS WINDOWS_SVR_2008 (x64)<br><br>Processes info:<br>- smss.exe (PID: 4, User: SYSTEM, Port: 445, Port: 139)<br>- svchost.exe (PID: 832, User: SYSTEM, Port: 135)<br>- svchost.exe (PID: 4400, User: NetworkService, Port: 3389)<br>- VelociraptorClient (PID: 4405, User: ubuntu, )<br>- green_session (PID: 4410, User: GreenAgent, )<br>",
                            "System info:<br>LINUX UBUNTU (x64)<br><br>Processes info:<br>- mysql (PID: 1101, User: root, Port: 3389)<br>- apache2 (PID: 1100, User: www-data, Port: 80, Port: 443)<br>- smtp (PID: 1102, User: root, Port: 25)<br>- VelociraptorClient (PID: 1108, User: ubuntu, )<br>- green_session (PID: 1114, User: GreenAgent, )<br>",
                            "System info:<br>LINUX UBUNTU (x64)<br><br>Processes info:<br>- sshd (PID: 1091, User: root, Port: 22)<br>- mysql (PID: 1101, User: root, Port: 3390)<br>- apache2 (PID: 1100, User: www-data, Port: 80, Port: 443)<br>- smtp (PID: 1102, User: root, Port: 25)<br>- VelociraptorClient (PID: 1107, User: ubuntu, )<br>- green_session (PID: 1111, User: GreenAgent, )<br>",
                            "",
                            "",
                            ""
                        ],
                        "action_info": {
                            "action": "at Host User0 do DiscoverRemoteSystems on User_router",
                            "success": True
                        },
                        "host_map": {
                            "Defender": "10.0.112.39",
                            "Enterprise0": "10.0.112.35",
                            "Enterprise1": "10.0.112.38",
                            "Enterprise2": "10.0.112.45",
                            "Op_Host0": "10.0.29.99",
                            "Op_Host1": "10.0.29.105",
                            "Op_Host2": "10.0.29.101",
                            "Op_Server0": "10.0.29.98",
                            "User0": "10.0.185.235",
                            "User1": "10.0.185.237",
                            "User2": "10.0.185.236",
                            "User3": "10.0.185.225",
                            "User4": "10.0.185.232",
                            "Enterprise_router": "10.0.112.40",
                            "Operational_router": "10.0.29.104",
                            "User_router": "10.0.185.231"
                        },
                        "obs": {},
                        "reward": 0,
                        "accumulate_reward": 0,
                    }
                }
            }
        }
    }
}

@pytest.fixture
def network_visualizer():
    return DashNetworkVisualizer(mock_agent_game_states)

def test_network_visualizer_initialization(network_visualizer):
    assert network_visualizer.agent_game_states == mock_agent_game_states

if __name__ == "__main__":
    network_visualizer = DashNetworkVisualizer(mock_agent_game_states)
    network_visualizer.run()