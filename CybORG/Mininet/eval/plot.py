import matplotlib.pyplot as plt

# Data points for each series
episodes = list(range(1, 11))

bline_reduced_sim = [-4.103483995, -14.54598851, -20.31694695, -13.94742726, -27.82761236,
                 -42.55584202, -64.64813699, -69.06542352, -94.3887349, -120.6668253]
bline_reduced_emu = [-1.291118747, -20.17600479, -42.15899246, 20.21501291, -24.51857925,
                   -30.25989215, -52.76169124, -80.55656073, -114.6410629, -122.9751975]

# Create a figure and axis
fig, ax = plt.subplots(figsize=(10, 6))

# Plot the data series
ax.plot(episodes, bline_reduced_sim, label='Bline (reduced AS) Sim mode')
ax.plot(episodes, bline_reduced_emu, label='Bline (reduced AS) Emu mode')

# Set labels and title
ax.set_xlabel('Number of Episodes')
ax.set_ylabel('Average rewards')
ax.set_title('Comparison of Average Rewards')

# Add legend
ax.legend()

# Display the plot
plt.show()