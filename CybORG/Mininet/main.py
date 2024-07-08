import subprocess
import inspect
import time
from statistics import mean, stdev
import random
import argparse 
from pprint import pprint

import logging
from rich.logging import RichHandler

from typing import List, Dict

from CybORG import CybORG, CYBORG_VERSION

from CybORG.Shared import Observation

from CybORG.Agents import B_lineAgent, BlueReactRemoveAgent, \
    RedMeanderAgent, SleepAgent
from CybORG.Agents import BaseAgent
from CybORG.Agents.MainAgent import MainAgent
from CybORG.Agents.MainAgent_cyborg_mm import MainAgent as MainAgent_cyborg_mm

from CybORG.Agents.Wrappers.ChallengeWrapper import ChallengeWrapper
from CybORG.Agents.Wrappers.LinkDiagramWrapper import LinkDiagramWrapper
from CybORG.Mininet.CustomFactory import CybORGFactory, AgentFactory
from CybORG.Mininet.CustomEnvironment import SimulatedEnvironment, EmulatedEnvironment
from CybORG.GameVisualizer.NetworkVisualizer import NetworkVisualizer
from CybORG.GameVisualizer.GameStateCollector import GameStateCollector
from CybORG.Mininet.MininetAdapter import MininetAdapter

MAX_EPS = 50
agent_name = 'Blue'
random.seed(0)
cyborg_version = CYBORG_VERSION
# scenario = 'Scenario2'
scenario = 'Scenario2_cyborg--'

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

    file_name = str(inspect.getfile(CybORG))[:-10] + '/Evaluation/' + time.strftime("%Y%m%d_%H%M%S") + f'_{agent.__class__.__name__}_{environment}' + '.txt'
    print(f'Saving evaluation results to {file_name}')
    with open(file_name, 'a+') as data:
        data.write(f'CybORG v{cyborg_version}, {scenario}, Commit Hash: {commit_hash}\n')
        data.write(f'author: {name}, team: {team}, technique: {name_of_agent}\n')
        data.write(f"wrappers: {wrap_line}\n")
        data.write(f"mode: {environment}\n")

    cyborg_factory = CybORGFactory()

    print(f'using CybORG v{cyborg_version}, {scenario}\n')
    
    # generate a enhanced network object for cyborg v2 
    # wrapped cyborg

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
    parser.add_argument ("-max_step", "--max_step", type=int, default=1, help="max rounds in onr epoisode")
    parser.add_argument ("-max_episode", "--max_episode", type=int, default=1, help="max episode in onr epoisode")
    parser.add_argument ("-agent_type", "--agent_type", default="CASTLEgym", help="CASTLEgym/CardiffUni/Others")
    parser.add_argument ("-cyborg_type", "--cyborg_type", default="wrap/others")

    # parse the args
    args = parser.parse_args ()

    return args

def getLogger ():
    logging.basicConfig(handlers=[RichHandler()])
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    return logger

if __name__ == "__main__":
    try:
        parsed_args = parseCmdLineArgs ()
        logger = getLogger ()
        # ip = parsed_args.ip
        env = parsed_args.env
        max_step = parsed_args.max_step
        max_episode = parsed_args.max_episode
        start = time.time()
        game_castle_gym_agent_state = main_v2(agent_type="CASTLEgym", cyborg_type="wrap", environment=env, max_step=max_step, max_episode=max_episode)
        
        logger.info(f"Time for {max_episode} Episodes and {max_step} Steps: %d sec", time.time()-start)
        
        nv = NetworkVisualizer(game_castle_gym_agent_state)
        nv.plot(save=False)
    except KeyboardInterrupt:
        pass