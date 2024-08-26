# NetworkVisualizer

Right now it runs after the game ends and uses all the steps taken to create frames.

![Screenshot 2024-08-26 at 5 41 52 PM](https://github.com/user-attachments/assets/5a2b1de8-ec54-4a35-bfb1-da536316ca98)

## Usage

```python
nv = DashNetworkVisualizer(game_castle_gym_agent_state)
nv.run()
```

## To-Do

Real-time update after each step. \
An idea is used a pub/sub pattern where the `DashNetworkVisualizer` subscribes to the updates in `GameStateCollector`
