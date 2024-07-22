#!/usr/bin/python
#
# CS/ECE 4383/5383: Computer Networks
# Author: Aniruddha Gokhale
# Created: Fall 2023
#
#  Custom Topology creator based on YAML file 
#
# Run this program under "sudo" mode
#

# Many of the packages that need to be imported. See
# https://mininet.org/api/index.html
import collections
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node

# The following specialized ones, if needed
from mininet.node import CPULimitedHost
from mininet.node import OVSSwitch
from mininet.link import TCLink
from mininet.link import TCIntf

# other utility classes
from mininet.log import setLogLevel, info
from mininet.util import irange, natural, naturalSeq

# this one is for random number support
import random

# our CustomLan
from custom_lan import CustomLAN

# our utilities
import custom_utils as cu

# Linux Router
from linux_router import LinuxRouter

# Support for Yaml
import yaml
import json

from pathlib import Path
import logging

#################################################
# I don't think there is any simple way to create individual topologies in their own
# classes and then somehow combine them by picking, say, a switch from the
# child topology and connect to an artifact in the parent. So there is now only a
# single customized topology class but we have multiple methods so that the code
# is still somewhat modularized
#################################################
class CustomTopology (Topo):

  def __init__ (self, args, **_opts):
    self.topo_dict = None
    self.yaml = args.yaml  # The file containing YAML
    self.router_dict = {}   # maintains the next interface num for that router
    self.routers = []
    self.lans = []
    
    super ().__init__ (**_opts) # invoke parent class constructor

  ##############################################
  # Parses our topology description from YAML file
  ##############################################
  def parse_yaml (self):
    info ("CustomTopology::parse_yaml\n")
    with open (self.yaml, "r") as file:
      self.topo_dict = yaml.safe_load (file)['topo']
    
  ##########################################
  # build all the routers
  ##########################################
  def build_routers (self):
    '''Build the Routers one by one'''

    info ("CustomTopology::build_routers - creating all the routers\n")
    for router in self.topo_dict ['routers']:
      # add a host of Linux Router type
      info ("Router: " + router['router'] + " with IP: " + router['ip'] + "\n")
      r = self.addHost (router['router'],  # name of this router
                        cls=LinuxRouter,
                        ip=router['ip'])

      # save this router
      self.routers.append (r)

  ##########################################
  # build all the specified lans from the topo dict
  ##########################################
  def build_lans (self):
    '''Build the LANs one by one'''

    info ("CustomTopology::build_lans - creating all the LANS\n")
    for lan in self.topo_dict['lans']:
      # check if the router we are dealing with exists in our dictionary.
      # If not, create an entry and start our interface numbering from Zero
      if lan['router'] not in self.router_dict:
        self.router_dict[lan['router']] = 0

      # instantial CustomLAN object and let it build the underlying LAN
      lan_topo = CustomLAN (lan, self.router_dict[lan['router']])

      # build the lan
      lan_topo.build_lan (self)  # pass ourselves as the parent topo

      # save this LAN
      self.lans.append (lan_topo)

      # increment the interface num for this router for its next connection
      # somewhere else.
      self.router_dict[lan['router']] += 1
      
  ##########################################
  # connect the routers
  ##########################################
  def connect_routers (self):
    '''Build the LANs one by one'''

    info ("CustomTopology::connect_routers - connecting the routers\n")
    for link in self.topo_dict['links']:
      # check if the routers we are dealing with exists in our dictionary.
      # There could be a case where we have an intermediate router with
      # no LAN attached
      if link['ep1-router'] not in self.router_dict:
        self.router_dict[link['ep1-router']] = 0
      if link['ep2-router'] not in self.router_dict:
        self.router_dict[link['ep2-router']] = 0

      # retrieve the diff parts of the subnet address
      ip_prefix, prefix_len, last_octet = cu.IP_components (link['subnet'])

      # Add link
      info ("Add link between router " + link['ep1-router'] + " and router " + link['ep2-router'] + "\n")
      self.addLink (link['ep1-router'],
                    link['ep2-router'],
                    intfName1=link['ep1-router'] + "-eth" + str (self.router_dict[link['ep1-router']]),
                    params1={"ip": ip_prefix + "1" + prefix_len},
                    intfName2=link['ep2-router'] + "-eth" + str (self.router_dict[link['ep2-router']]),
                    params2={"ip": ip_prefix + "2" + prefix_len})
      
      # increment the interface num for these routers
      self.router_dict[link['ep1-router']] += 1
      self.router_dict[link['ep2-router']] += 1
      
  ##########################################
  # Fix routing rules at the individual hosts
  #
  # For reasons that I have not yet figured out, Mininet seems to force
  # upon each LAN host a default route to the default IP Base of 10.0.0.0/8
  # despite providing a defaultRoute going thru the specified router.
  #
  # This has happened sometimes.
  #
  # Thus, we use this brute force approach to fix the routes.
  ##########################################
  def fix_default_route (self, net):
    '''Fix default routing entries for each LAN '''

    info ("CustomTopology::fix_default_routes on each LAN host in our topology\n")
    info ("Currenly a NO-OP\n")

  ##########################################
  # Add user-supplied routing table entries
  ##########################################
  def add_routes (self, net):
    '''Add routing entries'''

    info ("CustomTopology::add_routes - update routing entries\n")

    for route in self.topo_dict['routes']:
      info ("Routing table update for Router: " + route['router'] + "\n")
      for entry in route['entries']:
        info ("Adding entry: " + entry + "\n")
        net[route['router']].cmd ("ip route add " + entry)

    # Although the LinuxRouter class's config method sets the IPv4 forwarding=1
    # I think that this is not getting enabled. So we do it again here for each of
    # the routers in our topology
    info ("CustomTopology::add_routes - enable forwarding in our routers\n")
    for router in self.routers:
      info ("Enabling IPv4 forwarding for router: " + router + "\n")
      net[router].cmd ("sysctl net.ipv4.ip_forward=1")
    
  ##########################################
  # Add NAT rules to all the subnets that need NAT access
  ##########################################
  def add_nat_rules (self, net):
    '''Add NAT rules'''

    info ("CustomTopology::add_nat_rules - add NAT rules for specified subnets\n")

    for nat in self.topo_dict['nats']:
      info ("Adding NAT rules for nat node: " + nat['name'] + "\n")
      nat_node = nat['name']
      nat_intf = nat_node + "-eth0"
      for subnet in nat['subnets']:
        info ("Adding rules for subnet: " + subnet + "\n")
        net[nat_node].cmd( 'iptables -I FORWARD',
                           '-i', nat_intf, '-d', subnet, '-j DROP' )
        net[nat_node].cmd( 'iptables -A FORWARD',
                           '-i', nat_intf, '-s', subnet, '-j ACCEPT' )
        net[nat_node].cmd( 'iptables -A FORWARD',
                           '-o', nat_intf, '-d', subnet, '-j ACCEPT' )
        net[nat_node].cmd( 'iptables -t nat -A POSTROUTING',
                           '-s', subnet, "'!'", '-d', subnet, '-j MASQUERADE' )

  ##########################################
  # Cleanup additional NAT rules that we had added. The default one
  # will (should) get cleaned up as part of mininet NAT node's terminate
  # method
  ##########################################
  def cleanup_nat_rules (self, net):
    '''Cleanup the additional NAT rules'''

    info ("CustomTopology::cleanup_nat_rules - cleanup NAT rules for specified subnets\n")

    for nat in self.topo_dict['nats']:
      info ("Cleaning up NAT rules for nat node: " + nat['name'] + "\n")
      nat_node = nat['name']
      nat_intf = nat_node + "-eth0"
      for subnet in nat['subnets']:
        info ("Cleaning up rules for subnet: " + subnet + "\n")
        net[nat_node].cmd( 'iptables -D FORWARD',
                           '-i', nat_intf, '-d', subnet, '-j DROP' )
        net[nat_node].cmd( 'iptables -D FORWARD',
                           '-i', nat_intf, '-s', subnet, '-j ACCEPT' )
        net[nat_node].cmd( 'iptables -D FORWARD',
                           '-o', nat_intf, '-d', subnet, '-j ACCEPT' )
        net[nat_node].cmd( 'iptables -t nat -D POSTROUTING',
                           '-s', subnet, "'!'", '-d', subnet, '-j MASQUERADE' )


  def cleanupServices(self, net):
    """Clean up services and temp files and sockets and daemon processes"""
    host = 'lan3h1' # User0
    net[host].cmd("pkill -f 'sudo -u velociraptor'")
    net[host].cmd(f"ps aux | grep sshd | grep -v grep | grep '/tmp/sshd_config_mininet' | awk '{{print $2}}' | xargs -r sudo kill")
    net[host].cmd(f"ps aux | grep '[S]SHConnectionServer.py' | awk '{{print $2}}' | xargs sudo kill -9") # clean the socket
    net[host].cmd(f"rm /tmp/terminal_connection_*")
    net[host].cmd(f"rm /usr/local/run/*")

  
  def setPassword(self, net):
    for lan in self.topo_dict['lans']:
      for host_name, host_info in lan['hosts_info'].items():
        host = lan['name'] + host_name    
        username = net[host].cmd('whoami').strip()
        info (f"Set password for {username} on {host}\n")
        password_change_command = f'echo "{username}:1234" | sudo chpasswd'
        net[host].cmd(password_change_command)


  def startSSHServer(self, net):
    for lan in self.topo_dict['lans']:
      for host_name, host_info in lan['hosts_info'].items():
        host = lan['name'] + host_name
        temp_config_file = f'/tmp/sshd_config_mininet_{host}'
        info(f"Create and configure a minimal sshd_config on {host}\n")
        # Start with a basic configuration enabling only password authentication
        basic_config = (
            "UsePAM yes\n"
            "PermitRootLogin yes\n"
            "PasswordAuthentication yes\n"
            "ChallengeResponseAuthentication no\n"
            "UseDNS no\n"  
            "Subsystem sftp /usr/lib/openssh/sftp-server\n"  
        )
        # Write this configuration to the temporary file
        net[host].cmd(f'echo "{basic_config}" > {temp_config_file}')
        info(f"Start ssh server on {host} with custom config\n")
        net[host].cmd(f'/usr/sbin/sshd -D -f {temp_config_file} > /tmp/sshd_{host}.log 2>&1 &')


  def setupSSHKnownHosts(self, net):
    '''Rules for SSH known_hosts file on different hosts'''
    """~/.ssh/known_hosts_ent10 for User3 & User4 should store the info of Enterprise 0
      ~/.ssh/known_hosts_ent11 for User1 & User2 & Defender should store the info of Enterprise 1
      ~/.ssh/known_hosts_ops10 for Enterprise 2 should store the info of Operational Server 0"""
    # A very Ad-hoc way to setup the known_hosts file, trying to map what castle-vm is doing
    ssh_known_hosts_map = {}
    for lan in self.topo_dict['lans']:
      for host_name, cyborg_name in lan['hosts_name_map'].items():
        host = lan['name'] + host_name
        ip = net[host].IP()
        if cyborg_name == 'User3' or cyborg_name == 'User4':
          ssh_known_hosts_map[ip] = '/tmp/.ssh/known_hosts_ent10'
        elif cyborg_name == 'User1' or cyborg_name == 'User2' or cyborg_name == 'Defender':
          ssh_known_hosts_map[ip] = '/tmp/.ssh/known_hosts_ent11'
        elif cyborg_name == 'Enterprise2':
          ssh_known_hosts_map[ip] = '/tmp/.ssh/known_hosts_ops10'
    
    ssh_known_hosts_map_json_file = Path('/', 'tmp', '.ssh', 'known_hosts.json')
    ssh_known_hosts_map_json_file.parent.mkdir(parents=True, exist_ok=True)
    
    # if not ssh_known_hosts_map_json_file.exists():
    #   raise FileNotFoundError(f"File {ssh_known_hosts_map_json_file} does not exist")
      
    with open('/tmp/.ssh/known_hosts.json', 'w') as f:
      json.dump(ssh_known_hosts_map, f)
    
    for lan in self.topo_dict['lans']:
      for host_name, cyborg_name in lan['hosts_name_map'].items():
        if cyborg_name == 'Enterprise0':
          host = lan['name'] + host_name
          ip = net[host].IP()
          info(f"Setup SSH known_hosts file for User3, User5\n")
          net[host].cmd(f'echo "{ip}" > /tmp/.ssh/known_hosts_ent10')
        elif cyborg_name == 'Enterprise1':
          host = lan['name'] + host_name
          ip = net[host].IP()
          info(f"Setup SSH known_hosts file for User1, User2, Defender\n")
          net[host].cmd(f'echo "{ip}" > /tmp/.ssh/known_hosts_ent11')
        elif cyborg_name == 'Op_Server0':
          host = lan['name'] + host_name
          ip = net[host].IP()
          info(f"Setup SSH known_hosts file for Enterprise2\n")
          net[host].cmd(f'echo "{ip}" > /tmp/.ssh/known_hosts_ops10')


  def updateClientConfigFile(self, net):
    '''rewrite server_urls'''
    lan3h1_ip = net['lan3h1'].IP()
    info(f"IP address of velociraptor server is {lan3h1_ip}\n")
    # Path to the client config file
    client_config_path = f"/etc/velociraptor/client.config.yaml"
    
    # Read, modify, and write the YAML configuration
    with open(client_config_path, 'r') as file:
        config = yaml.load(file)
    
    config['Client']['server_urls'] = [f"https://{lan3h1_ip}:8000/"]

    with open(client_config_path, 'w') as file:
        yaml.dump(config, file, default_flow_style=False)


  def startVelociraptorServer(self, net):
    '''Start the Velociraptor server on the attacker host and the defender host'''
    pids = collections.defaultdict(list)
    attacker_host = 'lan3h1' # User0
    defender_host = 'lan1h4' # Defender
    info(f"Start velociraptor server on {attacker_host} & {defender_host}\n")
    for node in [attacker_host, defender_host]:
      net[node].cmd('sudo -u velociraptor velociraptor --config /etc/velociraptor/server.config.yaml frontend &')
      pid = net[node].cmd('echo $!')
      pids[node].append(pid)
    return pids
  

  def startVelociraptorClients(self, net):
    pids = collections.defaultdict(list)
    for lan in self.topo_dict['lans']:
      for host_name, _ in lan['hosts_info'].items():
        host = lan['name'] + host_name
        # if host == 'lan3h1':
        #   continue
        info(f"Start velociraptor client on {host}\n")
        # net[host].cmd('velociraptor --config /home/ubuntu/justinyeh1995/CASTLEGym/CybORG/CybORG/Mininet/actions/client.config.yaml client -v > /dev/null 2>&1 &')
        net[host].cmd('velociraptor --config /etc/velociraptor/client.config.yaml client -v > /dev/null 2>&1 &')

        # net[host].cmd('systemctl start velociraptor_server &')
        pid = net[host].cmd('echo $!')
        pids[host].append(pid)
    return pids


  def configureHostsDNS(self, net, dns='8.8.8.8'):
    """
    Configure the DNS server for all hosts in the network.
    """
    for host in net.hosts:
      info(f"Append nameserver {dns} to /etc/resolv.conf \n")
      host.cmd('echo "nameserver %s" >> /etc/resolv.conf' % dns)
      dns_config = host.cmd('cat /etc/resolv.conf')
      info(f"DNS settings:\n{dns_config}\n")
      break


  def removeSpecificDNS(self, net, dns='8.8.8.8'):
    """
    Remove a specific DNS entry (nameserver 8.8.8.8) from /etc/resolv.conf for all hosts.
    """
    for host in net.hosts:
      # This command uses sed to search for the line containing 'nameserver 8.8.8.8' and delete it
      host.cmd(f"sed -i '/nameserver {dns}/d' /etc/resolv.conf")


  def stopSSHServer(self, net):
    for lan in self.topo_dict['lans']:
      for host_name, _ in lan['hosts_info'].items():
        host = lan['name'] + host_name
        info(f"Stopping ssh server on {host}\n")
        # Retrieve the PID of the SSH daemonKill the SSH daemon process
        net[host].cmd(f"ps aux | grep sshd | grep -v grep | grep '/tmp/sshd_config_mininet_{host}' | awk '{{print $2}}' | xargs -r sudo kill")
        # net[host].cmd(f"rm /tmp/sshd_config_mininet_{host}")


  def stopVelociraptorServer(self, net, pids):
    attacker_host = 'lan3h1' # User0
    defender_host = 'lan1h4' # Defender
    for host in [attacker_host, defender_host]:
        info(f"Stopping velociraptor server on {host}\n")
        # net[host].cmd('systemctl stop velociraptor_server &')
        for pid in pids[host]:
          output = net[host].cmd(f"sudo kill -9 {pid}")
          # Wait for the command to complete and retrieve the output
          output = net[host].waitOutput()
          info(f"Output of kill command on {host}: {output}\n")


  def stopVelociraptorClients(self, net, pids):
    for lan in self.topo_dict['lans']:
      for host_name, _ in lan['hosts_info'].items():
        host = lan['name'] + host_name
        info(f"Stopping velociraptor client on {host}\n")
        # net[host].cmd('systemctl stop velociraptor_server &')

        for pid in pids[host]:
          output = net[host].cmd(f"sudo kill -9 {pid}")
          # Wait for the command to complete and retrieve the output
          output = net[host].waitOutput()
          info(f"Output of kill command on {host}: {output}\n")


  def add_usr_local_dir(self, net):
    """
    Add /usr/local/run/ directory, if it has not existed yet
    """
    path = Path("/", "usr", "local", "run")
    if path.exists():
      print (f"{path} exists\n")
      return 
    for lan in self.topo_dict['lans']:
      for host_name, _ in lan['hosts_info'].items():
        host = lan['name'] + host_name
        net[host].cmd (f"sudo mkdir /usr/local/run/")
        net[host].cmd (f"sudo mkdir /usr/local/scripts/python/")
        return 

  ##########################################
  # The overridden build method
  ##########################################
  def build (self, **_opts):
    # Let us create single switch topology and specify a subnet they will use

    info ("CustomTopology::build - start building\n")

    # parse the yaml
    self.parse_yaml ()

    # first, build the routers
    self.build_routers ()

    # next, build the LANs
    self.build_lans ()
    
    # next, make connections between routers
    self.connect_routers ()

    # other operations will be performed after the net is formed
