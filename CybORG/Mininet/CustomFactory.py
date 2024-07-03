import inspect
import random

from dataclasses import dataclass
from typing import List, Dict

from CybORG import CybORG, CYBORG_VERSION

from CybORG.Agents import B_lineAgent, BlueReactRemoveAgent
from CybORG.Agents import BaseAgent
from CybORG.Agents.MainAgent import MainAgent
from CybORG.Agents.MainAgent_cyborg_mm import MainAgent as MainAgent_cyborg_mm

from CybORG.Agents.Wrappers.ChallengeWrapper import ChallengeWrapper
from CybORG.Agents.Wrappers.LinkDiagramWrapper import LinkDiagramWrapper

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
        env = ChallengeWrapper(env=env, agent_name='Blue')
        return LinkDiagramWrapper(env=env)
    
    def create(self, type: str, red_agent: BaseAgent) -> Dict:
        self.red_agent = red_agent()
        path = str(inspect.getfile(CybORG))
        path = path[:-10] + f'/Shared/Scenarios/{self.file_name}.yaml'
        #sg = FileReaderScenarioGenerator(path)
        cyborg = CybORG(path, 'sim', agents={'Red': red_agent})
        
        if type == "wrap":
            return {"wrapped": self.wrap(cyborg), "unwrapped": cyborg, 'Red': self.red_agent}
            
        return {"wrapped": None, "unwrapped": cyborg, 'Red': self.red_agent} 