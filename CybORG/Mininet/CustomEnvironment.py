import traceback
import numpy as np
from abc import ABC, abstractmethod
from typing import List, Dict

from CybORG import CybORG, CYBORG_VERSION

from CybORG.Shared import Observation

class CybORGEnvironment(ABC):
    def __init__(self, cyborg, red_agent, blue_agent, num_steps, max_episode):
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

    @abstractmethod
    def run(self):
        pass

class SimulatedEnvironment(CybORGEnvironment):
    def __init__(self, cyborg, red_agent, blue_agent, num_steps, max_episode, game_state_manager):
        super().__init__(cyborg, red_agent, blue_agent, num_steps, max_episode)
        self.game_state_manager = game_state_manager

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

        for i in range(self.max_episode):
            r = []
            a = []

            blue_observation = self.linked_diagram_cyborg.reset()
            blue_action_space = self.challenge_wrapper.get_action_space('Blue')
            red_observation = self.true_table_cyborg.get_observation('Red')
            red_action_space = self.true_table_cyborg.get_action_space('Red')

            mininet_blue_observation = blue_observation
            mininet_red_observation = red_observation


            # @To-Do bad design, the reset() among different objects has ordering dependecies
            try:
                self.game_state_manager.reset()
            except Exception as e:
                traceback.print_exc()
                raise e
            
            try:
                self.mininet_adapter.reset()
            except Exception as e:
                traceback.print_exc()
                raise e
            
            for j in range(self.num_steps):
                red_observation = mininet_red_observation.data if isinstance(mininet_red_observation, Observation) else mininet_red_observation
                red_action = self.red_agent.get_action(red_observation, red_action_space)
                print("--> In main loop: Red action using mininet_observation")
                print(red_action)
                
                try:
                    mininet_red_observation, red_reward = self.mininet_adapter.step(str(red_action), agent_type='Red')

                except Exception as e:
                    traceback.print_exc()
                    raise e

                blue_observation = mininet_blue_observation
                # blue_observation = self.blue_table_cyborg.observation_change('Blue', blue_observation.data) if isinstance(blue_observation, Observation) else blue_observation
                blue_observation = self.blue_table_cyborg.observation_change(blue_observation.data) if isinstance(blue_observation, Observation) else blue_observation
                blue_observation = np.array(blue_observation, dtype=np.float32)

                blue_action = self.blue_agent.get_action(blue_observation, blue_action_space)
                # blue_possible_actions = self.openai_gym_cyborg.possible_actions[blue_action]
                blue_possible_actions = self.openai_gym_cyborg.get_attr('possible_actions')[blue_action]
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
            self.red_agent.end_episode()
            total_reward.append(sum(r))
            actions_list.append(a)

        self.mininet_adapter.clean()

        return total_reward, actions_list