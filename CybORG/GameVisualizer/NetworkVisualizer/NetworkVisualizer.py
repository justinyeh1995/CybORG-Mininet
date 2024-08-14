import os
import plotly.graph_objects as go

from tqdm import tqdm
from .GoFrame import Frame

class NetworkVisualizer:
    def __init__(self, agent_game_states):
        self.agent_game_states = agent_game_states
        self.save = None
        
    def set_game_state(self, agent_game_states):
        self.agent_game_states = agent_game_states

    def plot(self, save=True):
        # assert data is sufficient
        # try
        # raise bad data

        frames = []
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
                                frames.append(frame)
                                pbar.update(1)

        fig = go.Figure(data=frames[0].data, layout=frames[0].layout)
        fig.frames = frames

        # Add animation controls (play, pause, etc.)
        self._add_animation_controls(fig)

        # if save:
        #     for frame in frames:
        #         print("Saved")
        fig.show()

    def _add_animation_controls(self, fig: go.Figure):
        # Define the custom buttons for play/pause
        play_buttons = [
            dict(label='▶️', method='animate', 
                 args=[None, {
                     'frame': {'duration': 500, 'redraw': True},
                     'fromcurrent': True,
                     'transition': {'duration': 0},
                     'mode': 'immediate',
                     'layout': {'uirevision': 'static'}  # This helps preserve the layout
                 }]),
            dict(label='⏹️', method='animate', 
                 args=[[None], {
                     'frame': {'duration': 0, 'redraw': True},
                     'mode': 'immediate',
                     'transition': {'duration': 0},
                     'layout': {'uirevision': 'static'}  # This helps preserve the layout
                 }]),
        ]

        # Add the play/pause buttons to the layout
        play_menu = dict(
            type='buttons',
            showactive=False,
            x=0.5,
            y=-0.01,
            # pad=dict(t=0, r=10),
            buttons=play_buttons,
            direction='right',
            font=dict(size=20),
        )

        # Add a slider
        steps = []
        for i, frame in enumerate(fig.frames):
            step = dict(
                method="animate",
                args=[
                    [frame.name],
                    {"frame": {"duration": 300, "redraw": True},
                     "mode": "immediate",
                     "transition": {"duration": 300}}
                ],
                label=str(i)
            )
            steps.append(step)

        sliders = [dict(
            active=0,
            currentvalue={"prefix": "Frame: "},
            pad={"t": 50},
            steps=steps
        )]

        # Update the layout, preserving existing updatemenus
        if 'updatemenus' in fig.layout:
            new_menus = fig.layout.updatemenus + (play_menu,)
            fig.layout.updatemenus = new_menus
        else:
            fig.layout.updatemenus = (play_menu,)

        fig.layout.sliders = sliders

        # Adjust the layout to accommodate the new controls
        # fig.update_layout(
        #     height=900,  # Increase the height to accommodate all controls
        # )
        
    def _save_figure(self, fig, red_agent, step):
        image_folder = f"images/{red_agent}"
        if not os.path.exists(image_folder):
            os.makedirs(image_folder, exist_ok=True)
        fig.write_image(f"{image_folder}/step{step+1}.png")
        