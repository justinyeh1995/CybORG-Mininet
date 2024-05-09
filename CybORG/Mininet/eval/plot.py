import re
import inspect
from CybORG import CybORG
import matplotlib.pyplot as plt

def parse_rewards(file_path):
    rewards = []
    with open(file_path, 'r') as file:
        content = file.read()
        rewards = re.findall(r"total reward: (-?\d+\.\d+)", content)
        rewards = [round(float(reward), 5) for reward in rewards]
    return rewards

# Data points for each series
episodes = list(range(1, 51))

path = str(inspect.getfile(CybORG))[:-7] + "/Evaluation/"

sim_file = path + "20240506_211240_MainAgent_sim.txt"
emu_file = path + "20240506_222451_MainAgent_emu.txt"

bline_reduced_sim = parse_rewards(sim_file)
bline_reduced_emu = parse_rewards(emu_file)
# Create a figure and axis
fig, ax = plt.subplots(figsize=(10, 6))

# Plot the data series
ax.plot(episodes, bline_reduced_sim, label='Simulation mode')
ax.plot(episodes, bline_reduced_emu, label='Emulation mode')

# Set labels and title with white color
ax.set_xlabel('Number of Episodes', color='white')
ax.set_ylabel('Rewards', color='white')
ax.set_title('Comparison of Rewards', color='white')

# Set the tick and tick label colors
plt.xticks(color='white')
plt.yticks(color='white')

# Change the edge color of the plot window
ax.spines['bottom'].set_color('white')
ax.spines['top'].set_color('white')
ax.spines['right'].set_color('white')
ax.spines['left'].set_color('white')

# Add legend with white text
ax.legend(facecolor='darkgrey')

# Optional: Change the background color of the plot area if desired
ax.set_facecolor('black')
fig.patch.set_facecolor('black')

# Save the figure before showing
plt.savefig('evaluation.png', transparent=True)

# Display the plot
plt.show()