import yaml
import inspect
from CybORG import CybORG, CYBORG_VERSION
from CybORG.Mininet.mininet_adapter import CybORGMininetMapper
from CybORG.Mininet.mininet_adapter.entity import Entity

WIN_REWARD = 0
LOSE_REWARD = 0
SESSION_REWARD = 0
ROOT_SESSION_REWARD = 0
LOSE_SESSION_REWARD = 0
LOSE_ROOT_SESSION_REWARD = 0

REWARD_MAX_DECIMAL_PLACES = 1

class RewardCalculator(Entity):
    # this reward calculator provides a reward to both red and blue due to changes in the number of privileged sessions
    def __init__(self, scenario):
        self.old_total = 0

        self.mapping = {'None': 0.0,
                        'Low': 0.1,
                        'Medium': 1.0,
                        'High': 10.0}
        self.compromised_hosts = {}
        with open(scenario, 'r') as file:
            # Load the YAML content
            self.scenario = yaml.safe_load(file)
        # print('Scenario data is:',self.scenario)
    def reset(self):
        self.old_total = 0

    def get_host(self, host_ip:str, mapper: CybORGMininetMapper):
        return mapper.cyborg_ip_to_host_map.get(host_ip, host_ip) 

    def privilegedrewardcalculator(self,current_state:dict, mapper):
        root_sessions=0; system_sessions=0
        for host, info in current_state.items():

            if host == 'success':
                continue

            if 'Sessions' in info:
                for session in info['Sessions']:
                        #if session['Agent'] == self.agent_name:
                        # count the number of root sessions
                        if session['Username'] == 'root':
                            confidentiality_value = self.mapping[self.scenario.get('Hosts', {}).get(host, {}).get('ConfidentialityValue', 'Low')]
                            root_sessions += confidentiality_value
                            self.compromised_hosts[host] = confidentiality_value
                            break
                        # count the number of SYSTEM sessions
                        if session['Username'] == 'SYSTEM':
                            confidentiality_value = self.mapping[self.scenario.get('Hosts', {}).get(host, {}).get('ConfidentialityValue', 'Low')]
                            system_sessions += confidentiality_value
                            self.compromised_hosts[host] = confidentiality_value
                            break

            # find the difference from the old privileged sessions
        total = root_sessions + system_sessions
        reward = total  # - self.old_total
        self.old_total = total
        return round(reward, REWARD_MAX_DECIMAL_PLACES)

    def reward(self,observation, mapper):
        reward= self.privilegedrewardcalculator(observation, mapper)
        return [-1*reward,reward]   #[Blue reward, red rewards]


if __name__=='__main__':
    path = str(inspect.getfile(CybORG))
    reward_cal=RewardCalculator(path[:-7] +'/Simulator/Scenarios/scenario_files/Scenario2_cyborg--.yaml')
    # obs= {"success":"True/False/Unknown", 'Op_Server0':{'Sessions':[{'Username':'root', 'ID': 0,'Timeout':0,'PID':2323}],'System info': {'OSType':'LINUX'}}, 'User1':{'Sessions':[{'Username':'root', 'ID': 0,'Timeout':0,'PID':2323}],'System info': {'OSType':'LINUX'}},'Enterprise1': {'Interface': [{'IP Address': '10.0.120.158'}]}}
    obs = {'10.0.67.119': {'Interface': [{'IP Address': '10.0.67.119'}],
                 'Processes': [{'Connections': [{'local_address': '10.0.67.119',
                                                 'local_port': '22',
                                                 'remote_address': '10.0.67.126',
                                                 'remote_port': 4444}],
                                'Process Type': 'ProcessType.REVERSE_SESSION'},
                               {'Connections': [{'Status': 'ProcessState.OPEN',
                                                 'local_address': '10.0.67.119',
                                                 'local_port': '52056'}],
                                'Process Type': 'ProcessType.XXX'}],
                 'Sessions': [{'Agent': 'Red',
                               'ID': 1,
                               'PID': '652249',
                               'Type': 'SessionType.RED_REVERSE_SHELL',
                               'Username': 'root'}],
                 'System info': {'Hostname': 'User1',
                                 'OSType': 'LINUX'}},
 '10.0.67.126': {'Processes': [{'Connections': [{'local_address': '10.0.67.126',
                                                 'local_port': 4444,
                                                 'remote_address': '10.0.67.119',
                                                 'remote_port': '22'}],
                                'Process Type': 'ProcessType.REVERSE_SESSION'}]},
 'success': "True"}
    reward=reward_cal.reward(obs)
    print(reward)
    print('Done')