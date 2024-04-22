import subprocess
import inspect
import time
import os
from statistics import mean, stdev
import random
import collections
import traceback 
from pprint import pprint

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict

from CybORG import CybORG, CYBORG_VERSION

from CybORG.Shared import Observation

from CybORG.Agents import B_lineAgent, BlueReactRestoreAgent, BlueReactRemoveAgent, \
    RandomAgent, RedMeanderAgent, SleepAgent
from CybORG.Agents import BaseAgent
from CybORG.Agents.MainAgent import MainAgent
from CybORG.Agents.MainAgent_cyborg_mm import MainAgent as MainAgent_cyborg_mm

from CybORG.Agents.Wrappers.ChallengeWrapper import ChallengeWrapper
from CybORG.Agents.Wrappers import EnumActionWrapper
from CybORG.Agents.Wrappers.FixedFlatWrapper import FixedFlatWrapper
from CybORG.Agents.Wrappers.IntListToAction import IntListToActionWrapper
from CybORG.Agents.Wrappers.OpenAIGymWrapper import OpenAIGymWrapper
from CybORG.Simulator.Scenarios.FileReaderScenarioGenerator import FileReaderScenarioGenerator

from CybORG.GameVisualizer.NetworkVisualizer import NetworkVisualizer
from CybORG.GameVisualizer.GameStateCollector import GameStateCollector
from CybORG.Mininet.MininetAdapter import MininetAdapter

MAX_EPS = 1
agent_name = 'Blue'
random.seed(0)
cyborg_version = CYBORG_VERSION
# scenario = 'Scenario2'
scenario = 'Scenario2_cyborg--'

@dataclass
class AgentFactory:
    """Class for keeping building agents."""
    
    def create(self, type: str) -> BaseAgent:
        if type == "CardiffUni":
            return MainAgent()
        elif type == "CASTLEgym":
            return MainAgent_cyborg_mm()
        else:
            return BlueReactRemoveAgent()  

@dataclass
class CybORGFactory:
    """Class for keeping building agents."""
    type: str = "wrap"
    file_name: str = "Scenario2_cyborg--"
    
    def wrap(self, env):
        return ChallengeWrapper(env=env, agent_name='Blue')
    
    def create(self, type: str, red_agent) -> Dict:
        red_agent = red_agent()
        path = str(inspect.getfile(CybORG))
        path = path[:-7] + f'/Simulator/Scenarios/scenario_files/{self.file_name}.yaml'
        sg = FileReaderScenarioGenerator(path)
        cyborg = CybORG(sg, 'sim', agents={'Red': red_agent})
        
        if type == "wrap":
            return {"wrapped": self.wrap(cyborg), "unwrapped": cyborg, 'Red':red_agent}
            
        return {"wrapped": None, "unwrapped": cyborg, 'Red':red_agent} 

def wrap(env):
    return ChallengeWrapper(env=env, agent_name='Blue')

def main(agent_type: str, cyborg_type: str, environment="emu") -> None:
    environment = environment
    cyborg_version = CYBORG_VERSION
    scenario = 'Scenario2_cyborg--'
    # commit_hash = get_git_revision_hash()
    commit_hash = "Not using git"
    # ask for a name
    name = "John Hannay"
    # ask for a team
    team = "CardiffUni"
    # ask for a name for the agent
    name_of_agent = "PPO + Greedy decoys"

    lines = inspect.getsource(wrap)
    wrap_line = lines.split('\n')[1].split('return ')[1]

    # Change this line to load your agent
    agent_factory = AgentFactory()
    # Change this line to load your agent
    agent = agent_factory.create(type=agent_type)
    
    print(f'Using agent {agent.__class__.__name__}, if this is incorrect please update the code to load in your agent')

    cyborg_factory = CybORGFactory()

    print(f'using CybORG v{cyborg_version}, {scenario}\n')
    
    # game manager initialization
    game_state_manager = GameStateCollector(environment=environment)
    # mininet adapter initialization
    mininet_adapter = MininetAdapter()

    
    for num_steps in [10]:
        for red_agent in [B_lineAgent]:

            cyborg_dicts = cyborg_factory.create(type=cyborg_type, red_agent=red_agent)
            wrapped_cyborg, cyborg, red_agent = cyborg_dicts["wrapped"], cyborg_dicts["unwrapped"], cyborg_dicts['Red']

            blue_observation = wrapped_cyborg.reset() if wrapped_cyborg else cyborg.reset()
            blue_action_space = wrapped_cyborg.get_action_space('Blue') if wrapped_cyborg else cyborg.reset()

            # Getting intial red_observation
            red_observation=cyborg.get_observation('Red')
            red_action_space= cyborg.get_action_space('Red')

            red_agent_name: str = red_agent.__class__.__name__
            blue_agent_name: str = agent.__class__.__name__
            
            # Set up game_state_manager
            game_state_manager.set_environment(cyborg=cyborg,
                                               red_agent_name=red_agent_name,
                                               blue_agent_name=blue_agent_name,
                                               num_steps=num_steps)
            # Reset state
            game_state_manager.reset()


            if environment == "emu":
                # Reset mininet adapter 
                mininet_adapter.set_environment(cyborg=cyborg)
                mininet_adapter.reset()
    
                mininet_blue_observation = blue_observation
                mininet_red_observation = red_observation
            
            total_reward = []
            actions_list = []
            for i in range(MAX_EPS):
                r = []
                a = []
                
                # cyborg.env.env.tracker.render()
                for j in range(num_steps):
                    if environment == "emu":
                        ########
                        # Blue #
                        ######## 
                        blue_observation = mininet_blue_observation
                        blue_observation = wrapped_cyborg.env.env.observation_change('Blue', blue_observation.data) if isinstance(blue_observation, Observation) else blue_observation
                        blue_observation = np.array(blue_observation, dtype=np.float32)
                        
                        blue_action = agent.get_action(blue_observation, blue_action_space)
                        blue_possible_actions = wrapped_cyborg.env.possible_actions[blue_action]
                        print("--> In main loop: Blue action using mininet_observation")
                        print(blue_possible_actions)
                        #######
                        # Red #
                        ####### 
                        red_observation = mininet_red_observation.data if isinstance(mininet_red_observation, Observation) else mininet_red_observation
                        red_action=red_agent.get_action(red_observation, red_action_space)
                        print("--> In main loop: Red action using mininet_observation")
                        print(red_action)
                        
                        # Mininet takes step
                        mininet_red_observation, red_reward = mininet_adapter.step(str(red_action), agent_type='Red')
                        mininet_blue_observation, blue_reward = mininet_adapter.step(str(blue_possible_actions), agent_type='Blue')
    
                        # Serialize actions & observations
                        actions = {"Red": str(red_action), "Blue": str(blue_possible_actions)}
                        observations = {"Red": mininet_red_observation.data, "Blue": mininet_blue_observation.data}
                    
                    elif environment == "sim":
                        blue_action = agent.get_action(blue_observation, blue_action_space)
                        blue_observation, rew, done, info = wrapped_cyborg.step(blue_action)

                        actions = {"Red":str(cyborg.get_last_action('Red')), "Blue": str(cyborg.get_last_action('Blue'))}
                        observations = {"Red": cyborg.get_observation('Red'), "Blue": cyborg.get_observation('Blue')}
                        pprint(actions)
                        pprint(observations)
                    # Create state for this step
                    state_snapshot = game_state_manager.create_state_snapshot(actions, observations)
                    
                    game_state_manager.store_state(state_snapshot, i, j)
                    print(f"===Step {j} is over===")
                    
                # game manager reset
                agent.end_episode()
                total_reward.append(sum(r))
                actions_list.append(a)
                # observation = cyborg.reset().observation
                observation = cyborg.reset()
                # game state manager reset
                game_state_manager.reset()
                # mininet adapter reset
                if environment == "emu":
                    mininet_adapter.reset()
        
        mininet_adapter.clean()

    return game_state_manager.get_game_state()


if __name__ == "__main__":
    # game_simple_agent_state = main(agent_type="default", cyborg_type="simple")
    game_castle_gym_agent_state = main(agent_type="CASTLEgym", cyborg_type="wrap", environment="sim")

