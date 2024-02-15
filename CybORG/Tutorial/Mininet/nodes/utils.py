import argparse # for argument parsing
import configparser # for configuration parsing
import logging # for logging. Use it in place of print statements.import json 
import traceback
import collections

action_table = {
    "DiscoverRemoteSystems": "nc"
}


def parseCmdLineArgs ():
    # instantiate a ArgumentParser object
    parser = argparse.ArgumentParser (description="Publisher Application")
  
    parser.add_argument ("-act", "--action", default="pub", help="Some action assigned to us. Keep it unique per publisher")

    parser.add_argument ("-a", "--addr", default="localhost", help="IP addr of this publisher to advertise (default: localhost)")

    parser.add_argument ("-p", "--port", default="5577", help="Port number on which our underlying applications ZMQ service runs, default=5577")
    parser.add_argument ("-l", "--loglevel", type=int, default=logging.DEBUG, choices=[logging.DEBUG,logging.INFO,logging.WARNING,logging.ERROR,logging.CRITICAL], help="logging level, choices 10,20,30,40,50: default 10=logging.DEBUG")
    
    return parser.parse_args()


def lookup_action (action):
    return action_table[action]

def build_commad (action, host):
    return action + f"{host}:5577"
    
    
    