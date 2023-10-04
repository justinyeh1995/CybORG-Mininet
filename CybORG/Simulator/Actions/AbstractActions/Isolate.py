#@author : harsh Vardhan (Vanderbilt university)

from CybORG.Shared import Observation
from CybORG.Simulator.Actions import Action
from CybORG.Simulator.State import State
from pprint import pprint

class Isolate(Action):
    def __init__(self, session: int, agent: str, hostname: str):
        super().__init__()
        self.agent = agent
        self.session = session
        self.hostname = hostname

    def execute(self, state: State) -> Observation:
        # WIP: working to implement the 'Isolate' functionality to the cyborg
        print('%%%%%%%%%%%%%%')
        parent_session: VelociraptorServer = state.sessions[self.agent][self.session]
        # find relevant session on the chosen host
        sessions = [s for s in state.sessions[self.agent].values() if s.hostname == self.hostname]
        print('Session is:',sessions)
        print('State is:',dir(state))
        pprint(state.__dict__)
        if len(sessions) > 0:
            session = state.np_random.choice(sessions)
            obs = Observation(True)
            # To do: remove the host from the subnet
            if self.hostname in parent_session.sus_pids:
                pass
            return obs
        else:
            return Observation(False)


    def __str__(self):
        return f"{self.__class__.__name__} {self.hostname}"
    
