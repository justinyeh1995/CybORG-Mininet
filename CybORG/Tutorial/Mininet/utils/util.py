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
    

def parse_action(cyborg, action_str, agent, host_map, ip_map):
    action_type = action_str.split(" ")[0]
    target_host = ""
    if cyborg.get_observation(agent)['success'].__str__() == 'TRUE':
        action_str_split = action_str.split(" ")
        n = len(action_str_split)
        target_host = action_str_split[-1] if n > 1 else target_host
        # Update target host if it's an IP address to get the hostname
        target_host = ip_map.get(target_host, target_host) if target_host in ip_map else target_host
    return target_host, action_type