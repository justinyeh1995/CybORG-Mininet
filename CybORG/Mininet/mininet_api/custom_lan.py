#
# CS/ECE 4383/5383: Computer Networks
# Author: Aniruddha Gokhale
# Created: Fall 2023
#
#  The CustomLAN class
#
# This class will be used by our CustomTopology class and is
# used to create a specified LAN topology including who its router is,
# its subnet, etc. It is assumed that the router has already been created.

# Many of the packages that need to be imported. See
# https://mininet.org/api/index.html
from mininet.topo import Topo
from mininet.node import Node
from mininet.nodelib import NAT # For NAT capabilities

# The following specialized ones, if needed
from mininet.node import CPULimitedHost
from mininet.node import OVSSwitch
from mininet.link import TCLink
from mininet.link import TCIntf

# other utility classes
from mininet.log import setLogLevel, info
from mininet.util import irange, natural, naturalSeq

# our utility methods
import custom_utils as cu

# from ipaddress import IPv4Address, IPv4Network
import ipaddress

##########################################
# The LAN class that keeps details of our LAN
##########################################
class CustomLAN ():
  def __init__ (self, lan_spec, router_intf_num):
    # the lan_spec parameter is a dictionary containing several details
    # about this LAN. Below, we obtain all the details from this dictionary
    self.topo = None  # our parent topo
    self.name = lan_spec['name']   # used as prefix when creating a switch and hosts
    self.router = lan_spec['router']  # router connected to this LAN
    self.router_ip = lan_spec['router_ip']
    self.router_intf_num = router_intf_num  # router interface number used to connect to LAN
    self.subnet = lan_spec['subnet']  # subnet of this LAN
    self.num_hosts = lan_spec['hosts']   # number of hosts in this LAN
    self.hosts_info = lan_spec['hosts_info']
    self.switch = None  # this will hold the created switch
    self.hosts = []  # this will be a list of all created hosts
    if 'nat' in lan_spec.keys ():  # check if "nat" is a dictionary key in this LAN or not
      self.nat_node = lan_spec['nat']
      self.nat_ip = lan_spec['nat_ip']
    else:
      self.nat_node = None

  #######################################
  # Construct the lan with the switch and hosts
  #######################################
  def build_lan (self, topo):
    '''Method that actually builds the LAN'''
    
    self.topo = topo  # save a handle to our parent topo
    
    # retrieve the diff parts of the CIDR-erized IP address
    ip_prefix, prefix_len, last_octet =cu.IP_components (self.subnet)
    
    # now construct a switch
    info ("LAN::build_lan - add switch for lan: " + self.name + "\n")
    s = self.topo.addSwitch (self.name + "s")
    self.switch = s

    # add a link to the switch from the router and use the first available IP
    info ("LAN::build_lan - add link from router to switch for lan: " + self.name + "\n")
    self.topo.addLink (self.router,
                       s,
                       intfName1=self.router + "-eth" + str (self.router_intf_num),
                       params1={"ip": self.router_ip + prefix_len})
      
    info ("LAN::build_lan - add all the hosts and connect to switch for lan: " + self.name + "\n")
    for i in range (self.num_hosts):  # create as many hosts as the number we specified      
      host_ip = ipaddress.ip_address(self.hosts_info["h" + str(i+1)])
      host_name = self.name + "h" + str(i+1)

      info ("Host " + host_name + " with IP: " + str(host_ip) + " and default route = " + "via " + self.router_ip + prefix_len + "\n")
      h = self.topo.addHost (name=host_name,
                             ip=str(host_ip) + prefix_len,
                             defaultRoute = " via " + self.router_ip) 
        
      # save this host (in case we need it)
      self.hosts.append (h)

      # add link from this host to switch
      info ("Connect this host to its switch\n")
      self.topo.addLink (h, s)

    # Assign IP address to the NAT node, if applicable
    if self.nat_node:
        info ("NAT " + self.nat_node + " with IP: " + str(self.nat_ip) + " and default route = " + "via " + self.router_ip + "\n")
        nat_host = self.topo.addHost(self.nat_node,
                                    cls=NAT,
                                    subnet=self.subnet,
                                    ip=str(self.nat_ip) + prefix_len,
                                    inNamespace=False)
        self.hosts.append(nat_host)
        self.topo.addLink(nat_host, s)