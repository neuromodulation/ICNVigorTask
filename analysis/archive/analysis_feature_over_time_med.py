# Script for plotting of features over time (med on/off)

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
feature_name = "peak_speed"  # out of ["peak_acc", "mean_speed", "move_dur", "peak_speed", "stim_time", "peak_speed_time", "move_onset_time", "move_offset_time"]
plot_individual = False
# Define medication On/Off datastes
datasets_off = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20]
datasets_on = [3, 4, 5, 7, 9, 10, 12, 18, 21, 22, 23, 24, 25]

# Load feature matrix
feature_matrix = np.load(f"../../Data/{feature_name}.npy")

# Select datasets of interest
n_datasets, _,_, n_trials = feature_matrix.shape

# Detect and fill outliers (e.g. when subject did not touch the screen)
np.apply_along_axis(lambda m: utils.fill_outliers_nan(m, threshold=3), axis=3, arr=feature_matrix)

# Reshape matrix such that blocks from one condition are concatenated
feature_matrix = np.reshape(feature_matrix, (n_datasets, 2, n_trials*2))

# Delete the first 5 movements
feature_matrix = feature_matrix[:, :, 5:]

# Normalize to average of first 5 movements
feature_matrix = utils.norm_perc(feature_matrix)

# Smooth over 5 consecutive movements for plotting
feature_matrix = utils.smooth_moving_average(feature_matrix, window_size=5, axis=2)

# Plot one subplot for each condition with 2 lines, one for each medication
cond_names = ["Slow", "Fast"]
colors = ["#00863b",  "#3b0086"]
plt.figure(figsize=(5, 5))
for cond in range(2):
    plt.subplot(2, 1, cond+1)

    # Plot med off
    x = np.arange(feature_matrix.shape[-1])
    off = feature_matrix[datasets_off, cond, :]
    plt.plot(np.nanmean(off, axis=0), linestyle='dashed', color=colors[cond], label=f"{cond_names[cond]} Med Off", linewidth=2)
    # Add std as shaded area
    plt.fill_between(x, np.nanmean(off, axis=0) - np.nanstd(off, axis=0), np.nanmean(off, axis=0) + np.nanstd(off, axis=0), color=colors[cond], alpha=0.2)

    # Plot med on
    x = np.arange(feature_matrix.shape[-1])
    on = feature_matrix[datasets_on, cond, :]
    plt.plot(np.nanmean(on, axis=0), linestyle='solid', color=colors[cond], label=f"{cond_names[cond]} Med On", linewidth=2)
    # Add std as shaded area
    plt.fill_between(x, np.nanmean(on, axis=0) - np.nanstd(on, axis=0), np.nanmean(on, axis=0) + np.nanstd(on, axis=0), color=colors[cond], alpha=0.2)

    # Adjust the plot
    n_trials = feature_matrix.shape[-1]
    plt.xlim([0, n_trials-1])
    plt.axvline(n_trials / 2, color="black", linewidth=1)
    axes = plt.gca()
    ymin, ymax = axes.get_ylim()
    axes.spines[['right', 'top']].set_visible(False)
    if cond == 0:
        plt.text(25, ymax + 2, "Stimulation", rotation=0, fontsize=11)
        plt.text(118, ymax + 2, "Recovery", rotation=0, fontsize=11)
    else:
        plt.xlabel("Movement number", fontsize=12)
    feature_name_space = feature_name.replace("_", " ")
    plt.ylabel(f"Change in \n {feature_name_space} [%]", fontsize=12)
    plt.legend()

plt.subplots_adjust(hspace=0.15, bottom=0.1, left=0.2)


# Save figure on group basis
plt.savefig(f"../../Plots/{feature_name}_med.png", format="png", bbox_inches="tight")

plt.show()