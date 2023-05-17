import numpy as np
import matplotlib.pyplot as plt

import utils.utils


def run_simulation(dis, eta, D1_mean, D2_mean, stim, n_trials, n_runs):

    X_all = np.zeros((n_trials, n_runs))
    mean_all = np.zeros((n_trials, n_runs))
    for run in range(n_runs):
        dis = [1000, 50]
        for trial in range(n_trials):

            # Draw sample for gaussian
            X = np.random.normal(dis[0], dis[1], 1)

            # Basal ganglia activation
            D1 = X * np.random.normal(D1_mean, 0.01, 1)
            D2 = X * np.random.normal(D2_mean, 0.01, 1)
            if stim == "random" and np.random.randint(0, 3) == 1 or \
               stim == "all" or \
               stim == "slow" and trial > 2 and np.all(X < X_all[trial-3:trial-1, run]) or \
               stim == "fast" and trial > 2 and np.all(X > X_all[trial-3:trial-1, run]):
                D2 = X * (np.random.normal(D2_mean, 0.01, 1) + 0.02)
            BG = (D1 + D2) / 2

            # Update mean of distribution
            shift = (BG - X) * (X - dis[0])
            dis[0] = dis[0] + eta * shift

            # Save
            X_all[trial, run] = X
            mean_all[trial, run] = dis[0]

    return  X_all, mean_all

# create a model that can simulate the results
n_trials = 100
n_runs = 100

# Define initial distribution and parameters
dis = [1000, 20]
eta = 0.01
D1_mean = 1.1
D2_mean = 0.7
stims = ["all", "random", "fast", "slow", "No stim"]

plt.figure(figsize=(10, 4))
for stim in stims:
    # Simulate
    X_all, mean_all = run_simulation(dis, eta, D1_mean, D2_mean, stim, n_trials, n_runs)
    # Plot
    plt.plot(np.mean(mean_all, axis=1), linewidth=3, label=stim)
plt.legend()
utils.utils.despine()
plt.show()