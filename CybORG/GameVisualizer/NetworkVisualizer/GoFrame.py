import networkx as nx 
import plotly.graph_objects as go
from pprint import pformat
import html
    
def format_dict_for_display(dictObj, indent=0):
    doc_string = ""
    doc_string += '  ' * indent + '\n'
    for k, v in dictObj.items():
        if isinstance(v, dict):
            doc_string += '  ' * indent + str(k) + ':' + '\n'
            doc_string += format_dict_for_display(v, indent+1)
        else:
            doc_string += ' ' * indent + str(k) + ': ' + str(v) + '\n'
    doc_string += '  ' * indent + '\n'
    return doc_string

def convert_reward_format(rewards, ordered=False):
    """
    Convert a dictionary of rewards into an HTML formatted list.

    Args:
    rewards (dict): A dictionary containing reward metrics and values.

    Returns:
    str: An HTML string representing the rewards in list format.
    """
    if not rewards:
        return '<br>No rewards'
    return "".join([f'<br>&nbsp;&nbsp;&nbsp;• {metric}: {round(value,2)}' for metric, value in rewards.items()])

class Frame:
    def __init__(self):
        self.type_to_symbol = {
            'router': 'triangle-up',  # Triangle
            'server': 'square',       # Square
            'host': 'circle',         # Circle
            'op_host': 'diamond',
            'op_server': 'square'
        }
        self.seed = 3113794652

    def add_max_steps(self, steps: int):
        self.num_steps = steps
        return self
    
    def add_red_agent_name(self, red_agent_name: str):
        self.red_agent_name = red_agent_name
        return self
    
    def add_episode(self, episode: int):
        self.episode = episode
        return self
    
    def add_current_step(self, step: int):
        self.step = step
        return self
   
    def add_agent(self, agent: str):
        self.agent = agent
        return self

    def add_state(self, state: dict):
        self.state = state
        return self

    def set_seed(self, seed):
        self.seed = seed
        
    def get_node_type(self, node):
        type = ""
        if 'router' in node:
            type = 'router'
        elif 'Op' in node:
            if 'Host' in node:
                type = 'op_host'
            else:
                type = 'op_server'
        elif 'Server' in node:
            type = 'server' 
        else:
            type = 'host'
        return type


    def build(self) -> go.Frame:
        mode = self.state['mode']
        link_diagram =  self.state['link_diagram']
        compromised_hosts =  self.state['compromised_hosts']
        node_colors =  self.state['node_colors']
        node_borders =  self.state['node_borders']
        action_info =  self.state['action_info']
        host_map =  self.state['host_map']
        obs =  self.state['obs']
        reward =  self.state['reward']
        accumulate_reward =  self.state['accumulate_reward']
        
        # 'link_diagram' is the NetworkX graph
        pos = nx.spring_layout(link_diagram, seed=self.seed)
        
        edge_x = []
        edge_y = []
        for edge in link_diagram.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        # Create edge trace
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')
            
        # Prepare hover text and symbols for each node
        hover_text = []
        node_symbols = []
        node_x = []    
        node_y = []     
        node_names = []

        for i, node in enumerate(link_diagram.nodes()):
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            # Determine the status ...
            compromised = 'Yes' if node in compromised_hosts else 'No'
            node_names.append(node)
            hover_text.append(f"Node: {node}<br>IP Address: {host_map[node]}<br>Compromised: {compromised}")
            # Determine the type of the node and assign the corresponding symbol
            node_type = self.get_node_type(node)  # Replace this with your method to get node type
            node_symbols.append(self.type_to_symbol.get(node_type, 'circle'))  # Default to 'circle'
        
        # Create node trace
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            hovertext=hover_text,
            text=node_names,
            marker=dict(showscale=False, 
                        colorscale='Viridis', 
                        color=node_colors, 
                        line=dict(
                            color=[border['color'] for border in node_borders],  # List of colors for each marker
                            width=[border['width'] for border in node_borders],  # List of widths for each marker
                        ),
                        size=10, 
                        symbol=node_symbols
                       ),
            textposition="top center",  # Position the text above the markers
            textfont=dict(
                family="sans serif",
                size=12,
                color="black")
        )        

        # Create annotations for agent actions, initially invisible
        detailed_info = dict(
          text=f"""
                <br>Mode: <b>{mode}</b>
                <br>Total Number of Steps: {self.num_steps}
                <br>Red Agent Name: {self.red_agent_name}
                <br>Episode: {self.episode+1}
                <br>Display <b>{self.agent}</b> Agent
                <br><b>Step {self.step+1}</b>'
                <br>🎯{self.agent} Action: {action_info['action']}
                <br>👀Observations: {obs}
                <br>✅Success: {action_info['success']}
                <br>💰Reward: {reward}
                <br>💳Accumulated Rewards: {accumulate_reward}
                """,
            showarrow=False,
            visible=False,  
        )

        # Create layout: Main Structure
        layout = go.Layout(
            title=f'<br>Mode: <b>{mode}</b> || Red Agent Name: <b>{self.red_agent_name}</b> <br> Episode: <b>{self.episode+1}</b> || Total Number of Steps: <b>{self.num_steps}</b>',
            title_x=0.5,
            title_y=1.0,
            # titlefont_size=10,
            showlegend=False,
            hovermode='closest',
            # margin=dict(b=15,l=0,r=200,t=80),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            annotations=[detailed_info],  # Include the annotations by default, shown initially
        )

        frame = go.Frame(        
            data=[edge_trace, node_trace],
            layout=layout,
            name=f"{self.red_agent_name} Ep: {self.episode+1} Step: {self.step+1} {self.agent}"
        )
        
        return frame
        