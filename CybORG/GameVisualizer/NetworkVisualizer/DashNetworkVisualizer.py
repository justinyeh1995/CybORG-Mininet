import os
import dash
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from tqdm import tqdm
import signal
import threading
import webbrowser

from .GoFrame import Frame
from .NetworkVisualizer import NetworkVisualizer

class DashNetworkVisualizer(NetworkVisualizer):
    def __init__(self, agent_game_states):
        super().__init__(agent_game_states)
        self.app = dash.Dash(__name__)
        self.app._favicon = ("cyborg-favicon.ico")
        self.frames = []
        self.create_frames()
        self.setup_layout()
        self.setup_callbacks()
        self.shutdown_event = threading.Event()

    def create_frames(self):
        total_frames = sum(
            len(self.agent_game_states[num_steps][red_agent_name][episode])
            for num_steps in self.agent_game_states
            for red_agent_name in self.agent_game_states[num_steps]
            for episode in self.agent_game_states[num_steps][red_agent_name]
        )

        with tqdm(total=total_frames, desc="Generating Frames") as pbar:
            for num_steps in self.agent_game_states:
                for red_agent_name in self.agent_game_states[num_steps]:
                    for episode in self.agent_game_states[num_steps][red_agent_name]:
                        for step, state in self.agent_game_states[num_steps][red_agent_name][episode].items():
                            for agent in state:
                                frame = Frame() \
                                    .add_max_steps(num_steps) \
                                    .add_red_agent_name(red_agent_name) \
                                    .add_episode(episode) \
                                    .add_current_step(step) \
                                    .add_agent(agent) \
                                    .add_state(state[agent]) \
                                    .build()
                                self.frames.append(frame)
                                pbar.update(1)
                                
    def setup_layout(self):
        self.app.layout = html.Div([
            html.H1("CybORG Visualizer", style={'textAlign': 'center'}),
            
            html.Div([
                dcc.Graph(id='network-graph', style={'height': '80vh', 'width': '60%'}),
                html.Div([
                    html.H3("Details"),
                    html.Div(id="observations-panel", style={'display': 'block', 'padding': '10px'}),
                    html.Button("Show Detailed Information", id="toggle-observations"),
                ], style={'width': '40%', 'float':'right', 'margin-left': 'auto', 'margin-right': 'auto', 'padding': '10px'})
            ], style={'display': 'flex'}),
            
            html.Div([
                html.Div(id='frame-info'),
                html.Button('Previous', id='prev-button', n_clicks=0),
                html.Button('Play', id='play-button', n_clicks=0),
                html.Button('Pause', id='pause-button', n_clicks=0),
                html.Button('Next', id='next-button', n_clicks=0),
            ], style={
                'display': 'flex',
                'justifyContent': 'center',
                'alignItems': 'center',
                'gap': '10px',
                'marginTop': '20px'
            }),
            
            html.Div([
                dcc.Slider(
                    id='frame-slider',
                    min=0,
                    max=len(self.frames) - 1,
                    value=0,
                    marks={i: str(i) for i in range(0, len(self.frames), max(1, len(self.frames) // 10))},
                    step=1
                ),
                
            ], style={'margin-top': '20px', 'margin-left': 'auto', 'margin-right': 'auto', 'margin-bottom': '20px'}),
        
            dcc.Interval(id='interval-component', interval=500, n_intervals=0, disabled=True),
        ])

    def setup_callbacks(self):
        @self.app.callback(
            Output('network-graph', 'figure'),
            Output('frame-info', 'children'),
            Output('frame-slider', 'value'),
            Output('interval-component', 'disabled'),
            Output('observations-panel', 'children'),
            Input('frame-slider', 'value'),
            Input('interval-component', 'n_intervals'),
            Input('prev-button', 'n_clicks'),
            Input('next-button', 'n_clicks'),
            Input('play-button', 'n_clicks'),
            Input('pause-button', 'n_clicks'),
            State('interval-component', 'disabled')
        )
        def update_graph(selected_frame, n_intervals, prev_clicks, next_clicks, play_clicks, pause_clicks, is_paused):
            ctx = dash.callback_context
            if not ctx.triggered:
                frame_index = 0
            else:
                input_id = ctx.triggered[0]['prop_id'].split('.')[0]
                if input_id == 'interval-component':
                    frame_index = (selected_frame + 1) % len(self.frames)
                    if frame_index == 0:  # Stop at the last frame
                        is_paused = True
                elif input_id == 'prev-button':
                    frame_index = max(0, selected_frame - 1)
                elif input_id == 'next-button':
                    frame_index = min(len(self.frames) - 1, selected_frame + 1)
                elif input_id == 'play-button':
                    is_paused = False
                    frame_index = selected_frame
                elif input_id == 'pause-button':
                    is_paused = True
                    frame_index = selected_frame
                else:
                    frame_index = selected_frame

            frame = self.frames[frame_index]
            fig = go.Figure(data=frame.data, layout=frame.layout)
            
            # Remove the observations from the figure
            fig.update_layout(annotations=[])
            
            # Extract frame info
            frame_info = f"Frame - {frame.name}"
            
            # Prepare observations panel content
            observations_panel = html.Div([
                html.P(f"Step: {frame.layout.annotations[0]['text'].split('<b>Step')[1].split('</b>')[0]}"),
                html.P(f"Agent: {frame.layout.annotations[0]['text'].split('Display <b>')[1].split('</b>')[0]}"),
                html.P(f"Action: {frame.layout.annotations[0]['text'].split('Action:')[1].split('<br>')[0]}"),
                html.P(f"Success: {frame.layout.annotations[0]['text'].split('Success:')[1].split('<br>')[0]}"),
                html.P(f"Observations:\n"),
                html.P(frame.layout.annotations[0]['text'].split('Observations:')[1].split('<br>')[0]),
                html.P(f"Reward: {frame.layout.annotations[0]['text'].split('Reward:')[1].split('<br>')[0]}"),
                html.P(f"Accumulated Rewards: {frame.layout.annotations[0]['text'].split('Accumulated Rewards:')[1]}")
            ])
            
            return fig, frame_info, frame_index, is_paused, observations_panel

        @self.app.callback(
            Output('toggle-observations', 'children'),
            Output('observations-panel', 'style'),
            Input('toggle-observations', 'n_clicks'),
            State('observations-panel', 'style')
        )
        def toggle_observations(n_clicks, current_style):
            if n_clicks is None:
                # Initial state
                return "Hide Detailed Information", {'display': 'block'}
            
            if current_style['display'] == 'none':
                # If it's currently hidden, show it and change button text to "Hide"
                return "Hide Detailed Information", {'display': 'block'}
            else:
                # If it's currently shown, hide it and change button text to "Show"
                return "Show Detailed Information", {'display': 'none'}

    
    def run_server(self):
        self.app.run_server(debug=False, port=8050, use_reloader=False)
    
    def open_browser(self):
        webbrowser.open_new('http://localhost:8050/')

    def signal_handler(self, signum, frame):
        print("\nShutting down the server...")
        self.shutdown_event.set()

    def run(self):
        signal.signal(signal.SIGINT, self.signal_handler)

        server_thread = threading.Thread(target=self.run_server)
        server_thread.daemon = True
        server_thread.start()

        browser_thread = threading.Thread(target=self.open_browser)
        browser_thread.daemon = True
        browser_thread.start()

        print("Press Ctrl+C to shut down the server.")

        try:
            while not self.shutdown_event.is_set():
                self.shutdown_event.wait(1)
        except KeyboardInterrupt:
            pass

        print("Shutting down...")
    