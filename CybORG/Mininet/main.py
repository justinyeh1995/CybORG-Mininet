import subprocess
import inspect
import sys
import time
from statistics import mean, stdev
import random
import argparse 
from pprint import pprint

import logging
import traceback
from rich.logging import RichHandler

from typing import List, Dict, Union

from CybORG import CybORG, CYBORG_VERSION

from CybORG.Shared import Observation

from CybORG.Agents import B_lineAgent, BlueReactRemoveAgent, \
    RedMeanderAgent, SleepAgent, KeyboardAgent
from CybORG.Agents import BaseAgent

from CybORG.Agents.Wrappers.ChallengeWrapper import ChallengeWrapper
from CybORG.Agents.Wrappers.LinkDiagramWrapper import LinkDiagramWrapper
from CybORG.Mininet.CustomFactory import CybORGFactory, AgentFactory
from CybORG.Mininet.CustomEnvironment import SimulatedEnvironment, EmulatedEnvironment
from CybORG.GameVisualizer.NetworkVisualizer import NetworkVisualizer, DashNetworkVisualizer

# from CybORG.GameVisualizer.DBManager import DBManager

random.seed(0)

def wrap(env):
    return ChallengeWrapper(env=env, agent_name='Blue')

def get_git_revision_hash() -> str:
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()

def main_v2(agent_type: str, cyborg_type: str, environment: str = "emu", max_step: int = 10, max_episode: int = 2, scenario: str = "Scenario2") -> None:
    cyborg_version = CYBORG_VERSION
    scenario = 'Scenario2'
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
    
    try:
        for num_steps in [max_step]:
            for red_agent in [B_lineAgent]: # [RedMeanderAgent, SleepAgent, KeyboardAgent]:

                cyborg_dicts = cyborg_factory.create(type=cyborg_type, red_agent=red_agent, file_name=scenario)
                wrapped_cyborg, cyborg, red_agent = cyborg_dicts["wrapped"], cyborg_dicts["unwrapped"], cyborg_dicts['Red']  

                if environment == "emu":
                    env = EmulatedEnvironment(wrapped_cyborg, red_agent, agent, num_steps, max_episode, environment)
                elif environment == "sim":
                    env = SimulatedEnvironment(wrapped_cyborg, red_agent, agent, num_steps, max_episode, environment)

                else:
                    raise ValueError(f"Invalid environment: {environment}")

                total_reward, actions_list = env.run()
                
                write_to_file(env, file_name, num_steps, total_reward, actions_list)
        
        return env.game_state_manager.get_game_state()
    
    except KeyboardInterrupt:
        print("Operation was interrupted by the user")
    except Exception as e:
        traceback.print_exc()
        print(f"An error occurred: {e}")


def write_to_file(env: Union[SimulatedEnvironment, EmulatedEnvironment], file_name: str, num_steps: int, total_reward: List[Union[float,int]], actions_list: List[str]) -> None:
    mean_val = mean(total_reward)
    stdev_val = 0 if len(total_reward) == 1 else stdev(total_reward)
    logging.info(f'Average reward for red agent {env.red_agent_name} and steps {num_steps} is: {mean_val}, standard deviation {stdev_val}')
    try:
        with open(file_name, 'a+') as data:
            data.write(f'steps: {num_steps}, adversary: {env.red_agent_name}, mean: {mean_val}, standard deviation {stdev_val}\n\n')
            for act, sum_rew in zip(actions_list, total_reward):
                data.write(f'actions: {act}, total reward: {sum_rew}\n')
    except IOError:
        logging.error(f"An error occurred while writing to file {file_name}")


def parseCmdLineArgs ():
    # parse the command line
    parser = argparse.ArgumentParser ()

    # add optional arguments
    parser.add_argument ("-env", "--env", default="emu", help="sim/emu")
    parser.add_argument ("-max_step", "--max_step", type=int, default=15, help="max rounds in onr epoisode")
    parser.add_argument ("-max_episode", "--max_episode", type=int, default=1, help="max episode in onr epoisode")
    parser.add_argument ("-agent_type", "--agent_type", default="DARTMOUTH", help="CASTLEgym/CardiffUni/DARTMOUTH")
    parser.add_argument ("-cyborg_type", "--cyborg_type", default="wrap/others")
    parser.add_argument ("-scenario", "--scenario", default="Scenario2")
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

        env = parsed_args.env
        max_step = parsed_args.max_step
        max_episode = parsed_args.max_episode
        scenario = parsed_args.scenario

        start = time.time()
        game_castle_gym_agent_state = main_v2(agent_type = "CASTLEgym", 
                                              cyborg_type = "wrap", 
                                              environment = env, 
                                              max_step = max_step, 
                                              max_episode = max_episode,
                                              scenario = scenario)
        
        logger = getLogger ()
        logger.info(f"Time for {max_episode} Episodes and {max_step} Steps: %d sec", time.time()-start)
        
        if not game_castle_gym_agent_state:
            logger.warning ("Game state is empty, Nothing to visualize. exiting...")
            sys.exit(0)
        
        try:
            nv = DashNetworkVisualizer(game_castle_gym_agent_state)
            nv.run()
        except Exception as e:
            logger.error ("Dash Visualization went wrong...")
            raise e
        
        # try:
        #     nv = NetworkVisualizer(game_castle_gym_agent_state)
        #     nv.plot(save=False)
        # except Exception as e:
        #     logger.error ("Visualization went wrong...")
        #     raise e
        
        # try:
        #     logger.info ("Store the game state into DB")
        #     db = DBStorage ()
        #     status = db.store_game_state (game_castle_gym_agent_state)
        #     if status:
        #         logger.info ("DB storage successful")
        #     else:
        #         logger.error ("DB storage failed")
        # except Exception as e:
        #     logger.error ("DB storage went wrong...")
        #     raise e
        
    except KeyboardInterrupt:
        logger.error ("Keyboard Interrupt")
        pass