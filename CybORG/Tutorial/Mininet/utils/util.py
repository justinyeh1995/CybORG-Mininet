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
    

def parse_action(cyborg, action_str, agent, ip_to_host_map):
    action_type = action_str.split(" ")[0]
    target_host = ""
    isSuccess = cyborg.get_observation(agent)['success'].__str__()
    if isSuccess == 'TRUE':
        action_str_split = action_str.split(" ")
        n = len(action_str_split)
        target_host = action_str_split[-1] if n > 1 else target_host
        print(target_host)
        # Update target host if it's an IP address to get the hostname
        target_host = ip_to_host_map.get(target_host, target_host) #if target_host in ip_to_host_map else target_host
        if action_type == "DiscoverRemoteSystems":
            print("Hey DiscoverRemoteSystems")
    return target_host, action_type, isSuccess