import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# --- Plot 1 ---
# Define constants and ranges
Tv = 1.0
Ts_Tv_ratio = np.linspace(0.01, 0.99, 50)
P_values = np.linspace(0.1, 0.9, 50)
N_range = np.arange(1, 11)  # N from 1 to 10

def speed_relative(Ts_Tv_ratio, P, N, Tv):
    spec_speed = (1 - P**(N+1)) / ((Ts_Tv_ratio * Tv * N + Tv) * (1 - P))
    orig_speed = 1/Tv
    return spec_speed/orig_speed

# Create meshgrid for ratio and P
ratio_mesh, p_mesh = np.meshgrid(Ts_Tv_ratio, P_values)
speedup_mesh = np.zeros_like(ratio_mesh)
optimal_N_mesh = np.zeros_like(ratio_mesh)

# Find optimal N and corresponding speedup for each point
for i in range(len(P_values)):
    for j in range(len(Ts_Tv_ratio)):
        speeds = [speed_relative(ratio_mesh[i,j], p_mesh[i,j], n, Tv) for n in N_range]
        best_idx = np.argmax(speeds)
        speedup_mesh[i,j] = speeds[best_idx]
        optimal_N_mesh[i,j] = N_range[best_idx]

# Create the plot
fig = plt.figure(figsize=(15, 10))
ax = fig.add_subplot(111, projection='3d')

# Plot main surface with color indicating optimal N
surf = ax.plot_surface(ratio_mesh, p_mesh, speedup_mesh,
                      facecolors=plt.cm.viridis(optimal_N_mesh/10),
                      alpha=0.8)

# Add transparent z=1 surface
z_ones = np.ones_like(ratio_mesh)
ax.plot_surface(ratio_mesh, p_mesh, z_ones,
               color='gray', alpha=0.3)

# Find intersection points (where speedup is close to 1)
intersection_points = []
for i in range(len(P_values)):
    for j in range(len(Ts_Tv_ratio)-1):
        if (speedup_mesh[i,j] - 1) * (speedup_mesh[i,j+1] - 1) <= 0:
            # Linear interpolation to find more precise intersection
            ratio_interp = ratio_mesh[i,j] + (ratio_mesh[i,j+1] - ratio_mesh[i,j]) * \
                          (1 - speedup_mesh[i,j]) / (speedup_mesh[i,j+1] - speedup_mesh[i,j])
            intersection_points.append([ratio_interp, p_mesh[i,j], 1])

intersection_points = np.array(intersection_points)
if len(intersection_points) > 0:
    # Plot intersection line
    ax.plot(intersection_points[:,0], intersection_points[:,1], intersection_points[:,2],
            color='red', linewidth=3, label='Break-even line')

# Set labels and title
ax.set_xlabel('Ts/Tv Ratio')
ax.set_ylabel('Acceptance Probability (P)')
ax.set_zlabel('Speedup (Times of original)')
ax.set_title('Speculative Decoding Speedup with Optimal N (1-10)')

# Add colorbar for N values
sm = plt.cm.ScalarMappable(cmap=plt.cm.viridis,
                          norm=plt.Normalize(vmin=1, vmax=10))
sm.set_array([])
cbar = plt.colorbar(sm)
cbar.set_label('Optimal N')

ax.legend()
plt.show()

# Print some example points
print("\nExample configurations:")
for ratio in [0.1, 0.3, 0.5, 0.7]:
    for p in [0.3, 0.5, 0.7]:
        idx_r = np.abs(Ts_Tv_ratio - ratio).argmin()
        idx_p = np.abs(P_values - p).argmin()
        print(f"Ratio={ratio:.1f}, P={p:.1f}: " +
              f"Optimal N={optimal_N_mesh[idx_p,idx_r]:.0f}, " +
              f"Speedup={speedup_mesh[idx_p,idx_r]:.2f}x")

# --- Plot 2 ---
# Define constants
Tv = 1.0  # Verification time (normalized)
P = 0.6  # Fixed probability of token acceptance

# Define the range for Ts/Tv ratio and N
Ts_Tv_ratio = np.linspace(0.01, 0.99, 50)
N_values = np.arange(1, 20)  # Number of tokens speculated each round

# Calculate the time per token
def time_per_token(Ts_Tv_ratio, P, N, Tv):
    return ((Ts_Tv_ratio * Tv * N) + Tv) * (1 - P) / (1 - P**(N+1))

# Calculate speed (tokens per time unit)
def speed(Ts_Tv_ratio, N, P, Tv):
    return 1.0 / time_per_token(Ts_Tv_ratio, P, N, Tv)

# Create a meshgrid for Ts/Tv ratio and N
Ts_Tv_mesh, N_mesh = np.meshgrid(Ts_Tv_ratio, N_values)
speed_mesh = speed(Ts_Tv_mesh, N_mesh, P, Tv)

# Find the best N for each Ts/Tv ratio
optimal_N = []
optimal_speeds = []
for i, ratio in enumerate(Ts_Tv_ratio):
    speeds_for_ratio = speed(ratio, N_values, P, Tv)
    best_index = np.argmax(speeds_for_ratio)
    optimal_N.append(N_values[best_index])
    optimal_speeds.append(speeds_for_ratio[best_index])

# Plot the speed in 3D surface
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_surface(Ts_Tv_mesh, N_mesh, speed_mesh, cmap='viridis', alpha=0.7)

# Mark the optimal points in red
optimal_points = list(zip(Ts_Tv_ratio, optimal_N, optimal_speeds))
optimal_points = np.array(optimal_points)
ax.scatter(optimal_points[:, 0], optimal_points[:, 1], optimal_points[:, 2],
           color='red', s=50, label='Optimal N')

# Set labels and title
ax.set_xlabel('Ts/Tv Ratio')
ax.set_ylabel('Number of Speculated Tokens (N)')
ax.set_zlabel('Speed (Tokens/time unit)')
ax.set_title('Speculative Decoding Speed with P=0.6')
ax.legend()

# Add a colorbar
fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)

plt.show()

# Print the optimal N values for each ratio
print("Optimal N for each Ts/Tv ratio:")
for ratio, n, spd in zip(Ts_Tv_ratio, optimal_N, optimal_speeds):
    print(f"Ts/Tv Ratio: {ratio:.2f}, Optimal N: {n}, Speed: {spd:.2f} Tokens/time unit")


