import logging
import traceback
import numpy as np
from abc import ABC, abstractmethod
from typing import List, Dict

from CybORG import CybORG, CYBORG_VERSION

from CybORG.Shared import Observation

from CybORG.GameVisualizer.GameStateCollector import GameStateCollector
from CybORG.Mininet.MininetAdapter import MininetAdapter

class CybORGEnvironment:
    def __init__(self, cyborg, red_agent, blue_agent, num_steps, max_episode, environment):
        self.cyborg = cyborg
        self.red_agent = red_agent
        self.blue_agent = blue_agent
        self.num_steps = num_steps
        self.max_episode = max_episode
        self.red_agent_name: str = red_agent.__class__.__name__
        self.blue_agent_name: str = blue_agent.__class__.__name__

        # @To-Do: highly coupled dependency: bad
        self.linked_diagram_cyborg = cyborg
        self.challenge_wrapper = cyborg.env
        self.openai_gym_cyborg = cyborg.env.env
        self.enum_action_cyborg = cyborg.env.env.env
        self.blue_table_cyborg = cyborg.env.env.env.env
        self.true_table_cyborg = cyborg.env.env.env.env.env
        self.unwrapped_cyborg = cyborg.env.env.env.env.env.env
        
        self.game_state_manager = GameStateCollector(environment=environment)
        # Set up game_state_manager
        self.game_state_manager.set_environment(cyborg=self.unwrapped_cyborg,
                                            red_agent_name=self.red_agent_name,
                                            blue_agent_name=self.blue_agent_name,
                                            num_steps=num_steps)

    @abstractmethod
    def run(self):
        pass

class SimulatedEnvironment(CybORGEnvironment):
    def __init__(self, cyborg, red_agent, blue_agent, num_steps, max_episode, environment):
        super().__init__(cyborg, red_agent, blue_agent, num_steps, max_episode, environment)

    def run(self):
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
                blue_observation, rew, done, info = self.challenge_wrapper.step(blue_action)

                actions = {"Red": str(self.unwrapped_cyborg.get_last_action('Red')),
                           "Blue": str(self.unwrapped_cyborg.get_last_action('Blue'))}
                observations = {"Red": self.unwrapped_cyborg.get_observation('Red'),
                                "Blue": self.unwrapped_cyborg.get_observation('Blue')}
                rewards = {"Red": self.unwrapped_cyborg.get_rewards()['Red'],
                           "Blue": self.unwrapped_cyborg.get_rewards()['Blue']}

                state_snapshot = self.game_state_manager.create_state_snapshot(actions, observations, rewards)
                self.game_state_manager.store_state(state_snapshot, i, j)
                r.append(rewards['Blue'])
                a.append((actions['Blue'], actions['Red']))

                print(f"===Episode {i+1}, Round {j + 1} is over===")

            self.blue_agent.end_episode()
            total_reward.append(sum(r))
            actions_list.append(a)

        return total_reward, actions_list

class EmulatedEnvironment(CybORGEnvironment):
    """_summary_
        This is where CybORG interacts with the MininetAdapter to run the environment
    Args:
        CybORGEnvironment (_type_): The parent class
    """
    def __init__(self, cyborg, red_agent, blue_agent, num_steps, max_episode, environment):
        super().__init__(cyborg, red_agent, blue_agent, num_steps, max_episode, environment)

    def run(self):
        actions_list = []
        total_reward = []
        
        with MininetAdapter() as mininet_adapter:
            # Set up mininet_adapter
            self.mininet_adapter = mininet_adapter
            self.mininet_adapter.set_environment(cyborg=self.unwrapped_cyborg) # @Note: since we are passing an object refence, the effect of self.cyborg.reset() will reflect in mininet_adapter

            for i in range(self.max_episode):
                r = []
                a = []

                blue_observation = self.cyborg.reset() # @To-Do; Follow wrapper branch and use the obs from assets/blue_init_observation.json 
                blue_action_space = self.cyborg.get_action_space('Blue')
                red_observation = self.true_table_cyborg.get_observation('Red')
                red_action_space = self.true_table_cyborg.get_action_space('Red')

                mininet_blue_observation = blue_observation
                mininet_red_observation = red_observation


                # @To-Do bad design, the reset() among different objects has ordering dependecies
                try:
                    self.game_state_manager.reset()
                except Exception as e:
                    raise e
                
                try:
                    self.mininet_adapter.reset()
                except Exception as e:
                    raise e
                
                for j in range(self.num_steps):
                    red_observation = mininet_red_observation.data if isinstance(mininet_red_observation, Observation) else mininet_red_observation
                    red_action_space = self.true_table_cyborg.get_action_space('Red')
                    red_action = self.red_agent.get_action(red_observation, red_action_space)
                    print("--> In main loop: Red action using mininet_observation")
                    print(red_action)
                    
                    try:
                        mininet_red_observation, red_reward = self.mininet_adapter.step(str(red_action), agent_type='Red')

                    except Exception as e:
                        raise e

                    blue_observation = mininet_blue_observation
                    # blue_observation = self.blue_table_cyborg.observation_change('Blue', blue_observation.data) if isinstance(blue_observation, Observation) else blue_observation
                    blue_observation = self.blue_table_cyborg.observation_change(blue_observation.data) if isinstance(blue_observation, Observation) else blue_observation
                    blue_observation = np.array(blue_observation, dtype=np.float32)

                    blue_action = self.blue_agent.get_action(blue_observation, blue_action_space)
                    # blue_possible_actions = self.openai_gym_cyborg.possible_actions[blue_action]
                    blue_possible_actions = self.openai_gym_cyborg.get_attr('possible_actions')[blue_action]
                    
                    logging.info("--> In main loop: Blue action using mininet_observation")
                    logging.info(blue_possible_actions)

                    mininet_blue_observation, blue_reward = self.mininet_adapter.step(str(blue_possible_actions), agent_type='Blue')

                    actions = {"Red": str(red_action), "Blue": str(blue_possible_actions)}
                    observations = {"Red": mininet_red_observation.data, "Blue": mininet_blue_observation.data}
                    rewards = {"Red": red_reward[-1] + blue_reward[-1], "Blue": red_reward[0] + blue_reward[0]}

                    state_snapshot = self.game_state_manager.create_state_snapshot(actions, observations, rewards)
                    self.game_state_manager.store_state(state_snapshot, i, j)
                    
                    r.append(rewards['Blue'])
                    a.append((actions['Blue'], actions['Red']))

                    logging.info(f"===Episode {i+1}, Round {j + 1} is over===")

                self.blue_agent.end_episode()
                self.red_agent.end_episode()
                total_reward.append(sum(r))
                actions_list.append(a)

        return total_reward, actions_list