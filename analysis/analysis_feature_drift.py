# Script for plotting the drift over all blocks

import numpy as np
import matplotlib.pyplot as plt
import mne
import gc
import scipy.stats
from statsmodels.stats.diagnostic import lilliefors
import utils.utils as utils
from mne_bids import BIDSPath, read_raw_bids, print_dir_tree, make_report
from alive_progress import alive_bar
import time
from statannot import add_stat_annotation
import seaborn as sb
from scipy import stats
import matplotlib
matplotlib.use('TkAgg')
import warnings
warnings.filterwarnings("ignore")

# Set analysis parameters
feature_name = "peak_speed" # out of ["peak_acc", "mean_speed", "move_dur", "peak_speed", "stim_time", "peak_speed_time", "move_onset_time", "move_offset_time"]
plot_individual = True
normalize = False
dataset_off = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20, 26, 27]
dataset_on = [3, 4, 5, 7, 9, 10, 12, 18, 21, 22, 23, 24, 25]
dataset = dataset_off

# Load feature matrix
feature_matrix = np.load(f"../../Data/{feature_name}.npy")

# Load array specifying which condition was first
slow_first = np.load(f"../../Data/slow_first.npy")

# Select datasets of interest
feature_matrix = feature_matrix[dataset, :, :, :]
slow_first = slow_first[dataset]
n_dataset, _, _, n_trials = feature_matrix.shape

# Rearrange such that the first block comes first
slow_fast = feature_matrix[np.where(slow_first == 1)[0], :, :, :]
fast_slow = feature_matrix[np.where(slow_first == 0)[0], :, :, :]
fast_slow = fast_slow[:, [1, 0], :, :]
feature_matrix = np.vstack((slow_fast, fast_slow))

# Detect and fill outliers (e.g. when subject did not touch the screen)
np.apply_along_axis(lambda m: utils.fill_outliers_mean(m, threshold=3), axis=3, arr=feature_matrix)

# Reshape matrix such that all movements are concatenated
feature_matrix_long = np.reshape(feature_matrix, (n_dataset, n_trials*4))

"""
plt.plot(feature_matrix_long[5, -50:])
plt.plot(feature_matrix[5, 1, 0, -50: ])
plt.show()"""

# Delete the first 5 movements
feature_matrix_long = feature_matrix_long[:, 5:]

# Normalize to average of first 5 movements
if normalize:
    feature_matrix_long = utils.norm_perc(feature_matrix_long)

# Smooth over 5 consecutive movements for plotting
feature_matrix_long = utils.smooth_moving_average(feature_matrix_long, window_size=5, axis=1)

# Plot individual if needed
if plot_individual:
    for i in range(n_dataset):
        # Plot feature over time
        plt.figure(figsize=(10, 3))
        plt.plot(feature_matrix_long[i,:].flatten())
        if normalize:
            plt.axhline(0, color="black", linewidth=1)
        plt.xlabel("Movement number", fontsize=14)
        feature_name_space = feature_name.replace("_", " ")
        plt.ylabel(f"Change in {feature_name_space} [%]", fontsize=14)
        plt.title(f"dataset_{i}_{feature_name}")
        # Save figure on individual basis
        plt.savefig(f"../../Plots/drift_dataset_{i}_{feature_name}.png", format="png", bbox_inches="tight")
        #plt.close()

# Average over all datasets
feature_matrix_mean = np.nanmedian(feature_matrix_long, axis=0)
feature_matrix_std = np.nanstd(feature_matrix_long, axis=0)

# Plot feature over time
fig = plt.figure()
x = np.arange(feature_matrix_long.shape[1])
plt.plot(feature_matrix_mean, linewidth=3)
plt.fill_between(x, feature_matrix_mean - feature_matrix_std, feature_matrix_mean + feature_matrix_std, alpha=0.2)
plt.xlabel("Movement number", fontsize=14)
feature_name_space = feature_name.replace("_", " ")
plt.ylabel(f"Change in {feature_name_space} [%]", fontsize=14)
if normalize:
    plt.axhline(0, color="black", linewidth=1)

# Save figure on group basis
plt.savefig(f"../../Plots/drift_{feature_name}.svg", format="svg", bbox_inches="tight")

plt.show()