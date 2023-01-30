# Script for plotting of features averaged in bins for med on and off

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
feature_name = "peak_acc"  # out of ["peak_acc", "mean_speed", "move_dur", "peak_speed", "stim_time", "peak_speed_time", "move_onset_time", "move_offset_time"]
property = "median"  # ["median", "std"]
plot_individual = False

# Define medication On/Off datastes
datasets_off = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20]
datasets_on = [3, 4, 5, 7, 9, 10, 12, 18, 21, 22, 23, 24, 25]

# Load feature matrix
feature_matrix = np.load(f"../../Data/{feature_name}.npy")
n_datasets, _,_, n_trials = feature_matrix.shape

# Detect and fill outliers (e.g. when subject did not touch the screen)
np.apply_along_axis(lambda m: utils.fill_outliers_nan(m), axis=3, arr=feature_matrix)

# Reshape matrix such that blocks from one condition are concatenated
feature_matrix = np.reshape(feature_matrix, (n_datasets, 2, n_trials*2))

# Delete the first 3 movements
feature_matrix = feature_matrix[:, :, 3:]

# Group into bins: Compute average feature in bin
n_bins = 21
feature_bin_median = np.array([np.nanmedian(arr, axis=2) for arr in np.array_split(feature_matrix, n_bins, axis=2)])

# Normalize to first bin and transform into percentage
feature_bin_median = ((feature_bin_median - feature_bin_median[0, :, :]) / feature_bin_median[0, :, :]) * 100

# Plot one subplot for each condition with 2 lines, one for each medication
cond_names = ["Slow", "Fast"]
colors = ["blue", "red"]
plt.figure(figsize=(12, 5))
for cond in range(2):
    plt.subplot(2, 1, cond+1)
    # Plot med off
    plt.plot(np.median(feature_bin_median[:, datasets_off, cond], axis=1),
                    linestyle='solid', color=colors[cond], label="Off", linewidth=2)
    # Plot med on
    plt.plot(np.median(feature_bin_median[:, datasets_on, cond], axis=1),
                    linestyle="dashed", color=colors[cond], label="On", linewidth=2)
    if cond == 1: plt.xlabel("# Bin", fontsize=14)
    plt.xticks([])
    plt.ylabel(f"% change in {feature_name}", fontsize=11)
    plt.axvline(np.floor(feature_bin_median.shape[0]/2), color="black", linewidth=2)
    plt.title(cond_names[cond], fontsize=16)
    plt.legend(loc="upper right")

plt.subplots_adjust(hspace=0.3)

# Save figure on group basis
plt.savefig(f"../../Plots/{feature_name}_med.png", format="png", bbox_inches="tight")

plt.show()