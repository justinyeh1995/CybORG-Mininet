from copy import deepcopy
from prettytable import PrettyTable
import numpy as np
import os
import json
from CybORG.Shared.Results import Results
from CybORG.Agents.Wrappers.BaseWrapper import BaseWrapper
from CybORG.Agents.Wrappers.TrueTableWrapper import TrueTableWrapper


class BlueTableWrapper(BaseWrapper):
    def __init__(self, env=None, agent=None, output_mode='table'):
        super().__init__(env, agent)
        self.env = TrueTableWrapper(env=env, agent=agent)
        self.agent = agent

        self.baseline = None
        self.output_mode = output_mode
        self.blue_info = {}

    def reset(self, agent='Blue'):
        result = self.env.reset(agent)
        obs = result.observation
        if agent == 'Blue':
            self._process_initial_obs(obs)
            #print('In BlueTablewrapper, reset obs is:',obs)
            obs = self.observation_change(obs, baseline=True)
        print('In BlueTablewrapper, changed obs is:',obs)
        result.observation = obs
        return result

    def step(self, agent=None, action=None) -> Results:
        
        print('\n action from blue table wrapper, is:',action)
        result = self.env.step(agent, action)
        obs = result.observation
        #print('\n observation from blue table wraper, is:',obs)
        if agent == 'Blue':
            obs = self.observation_change(obs)
        #print('\n changed obs from blue_table wrapper, is:',obs)
        result.observation = obs
        result.action_space = self.action_space_change(result.action_space)
        return result

    def get_table(self, output_mode='blue_table'):
        if output_mode == 'blue_table':
            return self._create_blue_table(success=None)
        elif output_mode == 'true_table':
            return self.env.get_table()

    def observation_change(self, observation, baseline=False):
        #print('\n observation from observation change, is:',observation)
        obs = observation if type(observation) == dict else observation.data
        obs = deepcopy(observation)
        success = obs['success']
        self._process_last_action()
        #print('baseline is:',baseline, "success is:",success, 'Output mode is:',self.output_mode)
        anomaly_obs = self._detect_anomalies(obs) if not baseline else obs
        del obs['success']
        # TODO check what info is for baseline
        #print('\n from observation change, anomaly obs is:',anomaly_obs)
        
        info = self._process_anomalies(anomaly_obs)
        
        #print('\n from observation change, Info is :',info)
        if baseline:
            for host in info:
                info[host][-2] = 'None'
                info[host][-1] = 'No'
                self.blue_info[host][-1] = 'No'

        self.info = info
        #print('\n Info is :',self.info)
        if self.output_mode == 'table':
            return self._create_blue_table(success)
        elif self.output_mode == 'anomaly':
            anomaly_obs['success'] = success
            return anomaly_obs
        elif self.output_mode == 'raw':
            return observation
        elif self.output_mode == 'vector':
            return self._create_vector(success)
        else:
            raise NotImplementedError('Invalid output_mode for BlueTableWrapper')

    def _process_initial_obs(self, obs):
        obs = obs.copy()
        #print('\n _process_initial_obs, obs is:',obs)
        self.baseline = obs
        del self.baseline['success']
        for hostid in obs:
            if hostid == 'success':
                continue
            host = obs[hostid]
            interface = host['Interface'][0]
            subnet = interface['Subnet']
            ip = str(interface['IP Address'])
            hostname = host['System info']['Hostname']
            self.blue_info[hostname] = [str(subnet), str(ip), hostname, 'None', 'No']
        #print('\n _process_initial_obs, blue_info is:',self.blue_info)
        if not os.path.exists('./assets'):
             os.makedirs('./assets')
        file_path= './assets/blue_initial_obs.json'
        with open(file_path, 'w') as file:
            json.dump(self.blue_info, file)
        
        return self.blue_info

    def _process_last_action(self):
        action = self.get_last_action(agent='Blue')
        if action is not None:
            name = action.__class__.__name__
            hostname = action.get_params()['hostname'] if name in ('Restore', 'Remove') else None

            if name == 'Restore':
                self.blue_info[hostname][-1] = 'No'
            elif name == 'Remove':
                compromised = self.blue_info[hostname][-1]
                if compromised != 'No':
                    self.blue_info[hostname][-1] = 'Unknown'

    def _detect_anomalies(self, obs):
        print('\n from detect anomalies, obs is:',obs)
        if self.baseline is None:
            raise TypeError(
                'BlueTableWrapper was unable to establish baseline. This usually means the environment was not reset before calling the step method.')

        anomaly_dict = {}
        print('\n \n self.baseline:',self.baseline)
        for hostid, host in obs.items():
            if hostid == 'success':
                continue
            print('host id is:',hostid)
            host_baseline = self.baseline[hostid]
            print('\n Host baseline is:',host_baseline)
            if host == host_baseline:
                continue

            host_anomalies = {}
            if 'Files' in host:
                baseline_files = host_baseline.get('Files', [])
                #print('\n Baseline files:',baseline_files)
                anomalous_files = []
                for f in host['Files']:
                    if f not in baseline_files:
                        anomalous_files.append(f)
                #print('\n anomalous files:',anomalous_files)
                if anomalous_files:
                    host_anomalies['Files'] = anomalous_files

            if 'Processes' in host:
                baseline_processes = host_baseline.get('Processes', [])
                print('\n Baseline processes:',baseline_processes)
                anomalous_processes = []
                for p in host['Processes']:
                    if p not in baseline_processes:
                        anomalous_processes.append(p)
                if anomalous_processes:
                    host_anomalies['Processes'] = anomalous_processes
                #print('\n anomalous processes:',anomalous_processes)
            if host_anomalies:
                anomaly_dict[hostid] = host_anomalies
        print('\n anomaly dict is:',anomaly_dict,'\n')
        return anomaly_dict

    def _process_anomalies(self, anomaly_dict):
        info = deepcopy(self.blue_info)
        for hostid, host_anomalies in anomaly_dict.items():
            assert len(host_anomalies) > 0
            if 'Processes' in host_anomalies:
                # added fix
                if "Connections" in host_anomalies['Processes'][-1]:
                    connection_type = self._interpret_connections(host_anomalies['Processes'])
                    info[hostid][-2] = connection_type
                    if connection_type == 'Exploit':
                        info[hostid][-1] = 'User'
                        self.blue_info[hostid][-1] = 'User'
            if 'Files' in host_anomalies:
                malware = [f['Density'] >= 0.9 for f in host_anomalies['Files']]
                if any(malware):
                    info[hostid][-1] = 'Privileged'
                    self.blue_info[hostid][-1] = 'Privileged'

        return info

    def _interpret_connections(self, activity: list):
        #print("_interpret connections:, activity is:",activity)
        num_connections = len(activity)
        ports = set([item['Connections'][0]['local_port'] \
                     for item in activity if 'Connections' in item])
        #print('** ports are:',ports,'num of connections:',num_connections)
        port_focus = len(ports)

        remote_ports = set([item['Connections'][0].get('remote_port') \
                            for item in activity if 'Connections' in item])
        if None in remote_ports:
            remote_ports.remove(None)

        if num_connections >= 3 and port_focus >= 3:
            anomaly = 'Scan'
        elif 4444 in remote_ports:
            anomaly = 'Exploit'
        elif num_connections >= 3 and port_focus == 1:
            anomaly = 'Exploit'
        else:
            anomaly = 'Scan'

        return anomaly

    # def _malware_analysis(self,obs,hostname):
    # anomaly_dict = {hostname: {'Files': []}}
    # if hostname in obs:
    # if 'Files' in obs[hostname]:
    # files = obs[hostname]['Files']
    # else:
    # return anomaly_dict
    # else:
    # return anomaly_dict

    # for f in files:
    # if f['Density'] >= 0.9:
    # anomaly_dict[hostname]['Files'].append(f)

    # return anomaly_dict

    def _create_blue_table(self, success):
        table = PrettyTable([
            'Subnet',
            'IP Address',
            'Hostname',
            'Activity',
            'Compromised'
        ])
        for hostid in self.info:
            table.add_row(self.info[hostid])

        table.sortby = 'Hostname'
        table.success = success
        return table

    def _create_vector(self, success):
        table = self._create_blue_table(success)._rows
        #print('From blue table wrapper, table is:',table)
        proto_vector = []
        for row in table:
            # Activity
            activity = row[3]
            if activity == 'None':
                value = [0, 0]
            elif activity == 'Scan':
                value = [1, 0]
            elif activity == 'Exploit':
                value = [1, 1]
            else:
                raise ValueError('Table had invalid Access Level')
            proto_vector.extend(value)

            # Compromised
            compromised = row[4]
            if compromised == 'No':
                value = [0, 0]
            elif compromised == 'Unknown':
                value = [1, 0]
            elif compromised == 'User':
                value = [0, 1]
            elif compromised == 'Privileged':
                value = [1, 1]
            else:
                raise ValueError('Table had invalid Access Level')
            proto_vector.extend(value)

        return np.array(proto_vector)

    def get_attr(self, attribute: str):
        return self.env.get_attr(attribute)

    def get_observation(self, agent: str):
        if agent == 'Blue' and self.output_mode == 'table':
            output = self.get_table()
        else:
            output = self.get_attr('get_observation')(agent)

        return output

    def get_agent_state(self, agent: str):
        return self.get_attr('get_agent_state')(agent)

    def get_action_space(self, agent):
        return self.env.get_action_space(agent)

    def get_last_action(self, agent):
        return self.get_attr('get_last_action')(agent)

    def get_ip_map(self):
        return self.get_attr('get_ip_map')()

    def get_rewards(self):
        return self.get_attr('get_rewards')()
