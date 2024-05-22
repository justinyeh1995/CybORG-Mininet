import subprocess
import inspect
import time
from statistics import mean, stdev
import random
import argparse 
from pprint import pprint

import numpy as np
import pandas as pd
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List, Dict

from CybORG import CybORG, CYBORG_VERSION

from CybORG.Shared import Observation

from CybORG.Agents import B_lineAgent, BlueReactRestoreAgent, BlueReactRemoveAgent, \
    RandomAgent, RedMeanderAgent, SleepAgent
from CybORG.Agents import BaseAgent
from CybORG.Agents.MainAgent import MainAgent
from CybORG.Agents.MainAgent_cyborg_mm import MainAgent as MainAgent_cyborg_mm

from CybORG.Agents.Wrappers.ChallengeWrapper import ChallengeWrapper
from CybORG.Simulator.Scenarios.FileReaderScenarioGenerator import FileReaderScenarioGenerator

from CybORG.GameVisualizer.NetworkVisualizer import NetworkVisualizer
from CybORG.GameVisualizer.GameStateCollector import GameStateCollector
from CybORG.Mininet.MininetAdapter import MininetAdapter

MAX_EPS = 50
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
    red_agent: BaseAgent = None
    
    def wrap(self, env):
        return ChallengeWrapper(env=env, agent_name='Blue')
    
    def create(self, type: str, red_agent) -> Dict:
        self.red_agent = red_agent()
        path = str(inspect.getfile(CybORG))
        path = path[:-7] + f'/Simulator/Scenarios/scenario_files/{self.file_name}.yaml'
        sg = FileReaderScenarioGenerator(path)
        cyborg = CybORG(sg, 'sim', agents={'Red': self.red_agent})
        
        if type == "wrap":
            return {"wrapped": self.wrap(cyborg), "unwrapped": cyborg, 'Red': self.red_agent}
            
        return {"wrapped": None, "unwrapped": cyborg, 'Red': self.red_agent} 

class CybORGEnvironment(ABC):
    def __init__(self, cyborg, red_agent, blue_agent, num_steps, max_episode):
        self.cyborg = cyborg
        self.red_agent = red_agent
        self.blue_agent = blue_agent
        self.num_steps = num_steps
        self.max_episode = max_episode
        self.red_agent_name: str = red_agent.__class__.__name__
        self.blue_agent_name: str = blue_agent.__class__.__name__
    @abstractmethod
    def run(self):
        pass

class SimulatedEnvironment(CybORGEnvironment):
    def __init__(self, cyborg, red_agent, blue_agent, num_steps, max_episode, game_state_manager):
        super().__init__(cyborg, red_agent, blue_agent, num_steps, max_episode)
        self.game_state_manager = game_state_manager

        self.openai_gym_cyborg = cyborg.env
        self.blue_table_cyborg = cyborg.env.env
        self.true_table_cyborg = cyborg.env.env.env
        self.unwrapped_cyborg = cyborg.env.env.env.env
        # Set up game_state_manager
        self.game_state_manager.set_environment(cyborg=self.unwrapped_cyborg,
                                            red_agent_name=self.red_agent_name,
                                            blue_agent_name=self.blue_agent_name,
                                            num_steps=num_steps)

    def run(self):
        blue_observation = self.cyborg.reset()
        blue_action_space = self.cyborg.get_action_space('Blue')

        actions_list = []
        total_reward = []

        for i in range(self.max_episode):
            r = []
            a = []

            blue_observation = self.cyborg.reset()
            blue_action_space = self.cyborg.get_action_space('Blue')

            self.game_state_manager.reset()

            for j in range(self.num_steps):
                blue_action = self.blue_agent.get_action(blue_observation, blue_action_space)
                blue_observation, rew, done, info = self.cyborg.step(blue_action)

                actions = {"Red": str(self.unwrapped_cyborg.get_last_action('Red')),
                           "Blue": str(self.unwrapped_cyborg.get_last_action('Blue'))}
                observations = {"Red": self.unwrapped_cyborg.get_observation('Red'),
                                "Blue": self.unwrapped_cyborg.get_observation('Blue')}
                rewards = {"Red": list(self.unwrapped_cyborg.get_rewards()['Red'].values())[0],
                           "Blue": list(self.unwrapped_cyborg.get_rewards()['Blue'].values())[0]}

                state_snapshot = self.game_state_manager.create_state_snapshot(actions, observations, rewards)
                self.game_state_manager.store_state(state_snapshot, i, j)
                r.append(rewards['Blue'])
                a.append((actions['Blue'], actions['Red']))

                print(f"===Episode {i+1}, Round {j + 1} is over===")

            self.blue_agent.end_episode()
            total_reward.append(sum(r))
            actions_list.append(a)

            blue_observation = self.cyborg.reset()
            blue_action_space = self.cyborg.get_action_space('Blue')

        return total_reward, actions_list

class EmulatedEnvironment(CybORGEnvironment):
    def __init__(self, cyborg, red_agent, blue_agent, num_steps, max_episode, game_state_manager, mininet_adapter):
        super().__init__(cyborg, red_agent, blue_agent, num_steps, max_episode)
        self.game_state_manager = game_state_manager
        
        self.openai_gym_cyborg = cyborg.env
        self.blue_table_cyborg = cyborg.env.env
        self.true_table_cyborg = cyborg.env.env.env
        self.unwrapped_cyborg = cyborg.env.env.env.env

        # Set up game_state_manager
        self.game_state_manager.set_environment(cyborg=self.unwrapped_cyborg,
                                            red_agent_name=self.red_agent_name,
                                            blue_agent_name=self.blue_agent_name,
                                            num_steps=num_steps)
        # Set up mininet_adapter
        self.mininet_adapter = mininet_adapter
        self.mininet_adapter.set_environment(cyborg=self.unwrapped_cyborg)


    def run(self):
        actions_list = []
        total_reward = []

        for i in range(max_episode):
            r = []
            a = []
            self.game_state_manager.reset()
            self.mininet_adapter.reset()

            blue_observation = self.cyborg.reset()
            blue_action_space = self.cyborg.get_action_space('Blue')
            red_observation = self.true_table_cyborg.get_observation('Red')
            red_action_space = self.true_table_cyborg.get_action_space('Red')

            mininet_blue_observation = blue_observation
            mininet_red_observation = red_observation

            for j in range(self.num_steps):
                red_observation = mininet_red_observation.data if isinstance(mininet_red_observation, Observation) else mininet_red_observation
                red_action = self.red_agent.get_action(red_observation, red_action_space)
                print("--> In main loop: Red action using mininet_observation")
                print(red_action)
                
                mininet_red_observation, red_reward = self.mininet_adapter.step(str(red_action), agent_type='Red')

                blue_observation = mininet_blue_observation
                blue_observation = self.blue_table_cyborg.observation_change('Blue', blue_observation.data) if isinstance(blue_observation, Observation) else blue_observation
                blue_observation = np.array(blue_observation, dtype=np.float32)

                blue_action = self.blue_agent.get_action(blue_observation, blue_action_space)
                blue_possible_actions = self.openai_gym_cyborg.possible_actions[blue_action]
                print("--> In main loop: Blue action using mininet_observation")
                print(blue_possible_actions)

                mininet_blue_observation, blue_reward = self.mininet_adapter.step(str(blue_possible_actions), agent_type='Blue')

                actions = {"Red": str(red_action), "Blue": str(blue_possible_actions)}
                observations = {"Red": mininet_red_observation.data, "Blue": mininet_blue_observation.data}
                rewards = {"Red": red_reward[-1] + blue_reward[-1], "Blue": red_reward[0] + blue_reward[0]}

                state_snapshot = self.game_state_manager.create_state_snapshot(actions, observations, rewards)
                self.game_state_manager.store_state(state_snapshot, i, j)
                r.append(rewards['Blue'])
                a.append((actions['Blue'], actions['Red']))

                print(f"===Episode {i+1}, Round {j + 1} is over===")

            self.blue_agent.end_episode()
            total_reward.append(sum(r))
            actions_list.append(a)

        self.mininet_adapter.clean()

        return total_reward, actions_list

def wrap(env):
    return ChallengeWrapper(env=env, agent_name='Blue')

def get_git_revision_hash() -> str:
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()

def main_v2(agent_type: str, cyborg_type: str, environment: str = "emu", max_step: int = 10, max_episode: int = 2) -> None:
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

    file_name = str(inspect.getfile(CybORG))[:-7] + '/Evaluation/' + time.strftime("%Y%m%d_%H%M%S") + f'_{agent.__class__.__name__}_{environment}' + '.txt'
    print(f'Saving evaluation results to {file_name}')
    with open(file_name, 'a+') as data:
        data.write(f'CybORG v{cyborg_version}, {scenario}, Commit Hash: {commit_hash}\n')
        data.write(f'author: {name}, team: {team}, technique: {name_of_agent}\n')
        data.write(f"wrappers: {wrap_line}\n")
        data.write(f"mode: {environment}\n")

    cyborg_factory = CybORGFactory()

    print(f'using CybORG v{cyborg_version}, {scenario}\n')
    
    # Single  
    # game manager initialization
    game_state_manager = GameStateCollector(environment=environment)
    
    # mininet adapter initialization
    mininet_adapter = MininetAdapter()
    
    for num_steps in [max_step]:
        for red_agent in [B_lineAgent]:

            cyborg_dicts = cyborg_factory.create(type=cyborg_type, red_agent=red_agent)
            wrapped_cyborg, cyborg, red_agent = cyborg_dicts["wrapped"], cyborg_dicts["unwrapped"], cyborg_dicts['Red']  

            if environment == "emu":
                env = EmulatedEnvironment(wrapped_cyborg, red_agent, agent, num_steps, max_episode, game_state_manager, mininet_adapter)
            elif environment == "sim":
                env = SimulatedEnvironment(wrapped_cyborg, red_agent, agent, num_steps, max_episode, game_state_manager)
            else:
                raise ValueError(f"Invalid environment: {environment}")

            total_reward, actions_list = env.run()
            
            mean_val = mean(total_reward)
            stdev_val = 0 if len(total_reward) == 1 else stdev(total_reward)
            print(f'Average reward for red agent {env.red_agent_name} and steps {num_steps} is: {mean_val}, standard deviation {stdev_val}')
            with open(file_name, 'a+') as data:
                data.write(f'steps: {num_steps}, adversary: {env.red_agent_name}, mean: {mean_val}, standard deviation {stdev_val}\n\n')
                for act, sum_rew in zip(actions_list, total_reward):
                    data.write(f'actions: {act}, total reward: {sum_rew}\n')
    
    return env.game_state_manager.get_game_state()


def parseCmdLineArgs ():
    # parse the command line
    parser = argparse.ArgumentParser ()

    # add optional arguments
    parser.add_argument ("-env", "--env", default="emu", help="sim/emu")
    parser.add_argument ("-max_step", "--max_step", type=int, default=30, help="max rounds in onr epoisode")
    parser.add_argument ("-max_episode", "--max_episode", type=int, default=2, help="max episode in onr epoisode")
    parser.add_argument ("-agent_type", "--agent_type", default="CASTLEgym", help="CASTLEgym/CardiffUni/Others")
    parser.add_argument ("-cyborg_type", "--cyborg_type", default="wrap/others")

    # parse the args
    args = parser.parse_args ()

    return args

if __name__ == "__main__":
    parsed_args = parseCmdLineArgs ()
    
    # ip = parsed_args.ip
    env = parsed_args.env
    max_step = parsed_args.max_step
    max_episode = parsed_args.max_episode
    game_castle_gym_agent_state = main_v2(agent_type="CASTLEgym", cyborg_type="wrap", environment=env, max_step=max_step, max_episode=max_episode)
    # nv = NetworkVisualizer(game_castle_gym_agent_state)
    # nv.plot(save=False)
