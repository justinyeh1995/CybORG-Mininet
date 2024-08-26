# NetworkVisualizer

Right now it runs after the game ends and uses all the steps taken to create frames.

![Screenshot 2024-08-26 at 5 41 52 PM](https://github.com/user-attachments/assets/5a2b1de8-ec54-4a35-bfb1-da536316ca98)

## Usage

```python
nv = DashNetworkVisualizer(game_castle_gym_agent_state)
nv.run()
```

This will open an flask app that runs on port `8050`.

## (Updating) To-Do

Real-time update after each step. \
An idea is used a pub/sub pattern where the `DashNetworkVisualizer` subscribes to the updates in `GameStateCollector`. multithreading could help here as well.
 
Uses websocket to support running a step at a time. Look into what keyboard agent wrapper does
