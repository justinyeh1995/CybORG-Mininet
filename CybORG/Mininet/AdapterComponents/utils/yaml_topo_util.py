from typing import List
import ipaddress
from ipaddress import IPv4Network
from CybORG.Mininet.MininetAPI import custom_utils as cu

################
# yaml builder #
################

def get_routers_info(cyborg, cyborg_to_mininet_name_map) -> List:
    """
    Assume the router names are suffixed with '_router'
    """
    return [{'router': cyborg_to_mininet_name_map[name], 
             'ip': str(ip)} for name, ip in cyborg.get_ip_map().items() if name.endswith('_router')]


def get_lans_info(cyborg, cyborg_to_mininet_name_map, cyborg_to_mininet_host_map) -> List:
    import re
    def extract(s):
        match = re.search(r'(h\d+)$', s)
        return match.group(1) if match else "??" # To-Do: better error handling
    
    lans_info = []
    counter = 0
    # Create LANs based on the networks
    for lan_name, network in cyborg.environment_controller.subnet_cidr_map.items():
        hosts = [name for name, ip in cyborg.get_ip_map().items() if ip in network and not name.endswith('_router')]
        
        hosts_info = { extract(cyborg_to_mininet_host_map[name]): str(cyborg.get_ip_map()[name]) for i, name in enumerate(hosts)}
        hosts_name_map = { cyborg_to_mininet_host_map[name]: name for i, name in enumerate(hosts)}
        # Calculate the usable IP range
        usable_ips = list(network.hosts())

        for ip in hosts_info.values():  # create as many hosts as the number we specified      
            host_ip = ipaddress.ip_address(ip)
            if host_ip in usable_ips:
                usable_ips.remove(host_ip)
            else:
                print("Invalid host ip")
        
        if usable_ips:
            router_ip = usable_ips[0]
            usable_ips.remove(router_ip)
        else:
            print("No ip let for router")
            
        lans_info.append({
            'name': cyborg_to_mininet_name_map[lan_name],
            'router': cyborg_to_mininet_name_map[f'{lan_name}_router'],
            'router_ip': str(router_ip),
            'subnet': str(network),
            'hosts': len(hosts),
            'hosts_info': hosts_info,
            'hosts_name_map': hosts_name_map,
            'nat': f'nat{counter}',
            'nat_ip': str(usable_ips[-1]) # Assign the next available IP address to the NAT node
        })

        counter += 1

    return lans_info


def get_router2router_links(cyborg) -> List:
    """
    Filter only for router-to-router links
    """
    try:
        edge_view = cyborg.environment_controller.state.link_diagram.edges
    except AttributeError:
        raise AttributeError("Link diagram not found in the environment controller state, the state is not properly initialized")
    
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


def get_nats_info(cyborg, topology):
    nats_info = []
    for lan in topology["topo"]['lans']:
        if lan.get('nat', None):
            nats_info.append({
                'name': lan['nat'],
                'subnets': [str(network) for lan_name, network in cyborg.environment_controller.subnet_cidr_map.items() if lan_name != lan['name']],
                'router': lan['router'],
            })

    return nats_info


def generate_routing_rules(topology):
    lans: list = topology["topo"]['lans']
    routers: list = topology["topo"]['routers']
    
    routers_cidr: dict = { entry['router']: entry['subnet'] for entry in lans}
    routers_ip: dict = { entry['router']: entry['ip'] for entry in routers}
    routers_2_nat: dict = { entry['router']: entry.get('nat_ip', None) for entry in lans}
        
    number_of_routers: int = len(routers_ip)

    interface_table: dict = {}

    for i in range(1, number_of_routers + 1):
        router = f"r{i}"
        interface_table[router] = {}

        for j in range(1, number_of_routers + 1):
            if i != j:
                interface_table[router][f"r{j}"] = len(interface_table[router]) + 1

    assert interface_table == {
        "r1": {"r2": 1, "r3": 2},
        "r2": {"r1": 1, "r3": 2},
        "r3": {"r1": 1, "r2": 2},
    }

    # route to other routers
    routes: dict = {}
    for i, link in enumerate(topology["topo"]["links"]):
        r1, r2 = link["ep1-router"], link["ep2-router"]
        subnet = link["subnet"]

        ip_prefix, prefix_len, last_octet = cu.IP_components (link['subnet'])

        # Initialize dictionaries if not already present
        routes.setdefault(r1, []).append({"to": routers_cidr[r2], "via": ip_prefix + str (2), "dev":f'{r1}-eth{interface_table[r1][r2]}'})
        routes.setdefault(r2, []).append({"to": routers_cidr[r1], "via": ip_prefix + str (1), "dev":f'{r2}-eth{interface_table[r2][r1]}'})
            
    # Format routing rules among routers
    # defulat should route to the lan that has nat node
    routing_rules = []
    for i, (router, entries) in enumerate(routes.items()):
        router_rules = {"router": router, "entries": []}
        
        # Add default rule for the lan that has nat
        if routers_2_nat[router]: # if r1 belongs to the last subnet
            nat_ip = routers_2_nat[router]
            routes.setdefault(router, []).append({"to": "default", "via": str(nat_ip), "dev":f'{router}-eth0'})

        # Add the ruls defined in routes
        for entry in entries:
            entry_str = f"{entry['to']} via {entry['via']} dev {entry['dev']}"
            router_rules["entries"].append(entry_str)
            
        routing_rules.append(router_rules)

    for nat in topology["topo"]["nats"]:
        router_rules = {"router": nat["name"], "entries": []}
        router_ip = routers_ip[nat["router"]]
        for subnet in nat['subnets']:
            entry_str = f"{subnet} via {router_ip} dev {nat['name']}-eth0"
            router_rules["entries"].append(entry_str)

    return routing_rules
