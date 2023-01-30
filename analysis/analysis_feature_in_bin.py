# Script for plotting of features averaged in bins
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
med = "off"  # "on", "off", "all"
if med == "all":
    datasets = np.arange(26)
elif med == "off":
    datasets = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20]
else:
    datasets = [3, 4, 5, 7, 9, 10, 12, 18, 21, 22, 23, 24, 25]

# Load feature matrix
feature_matrix = np.load(f"../../Data/{feature_name}.npy")

# Select datasets of interest
feature_matrix = feature_matrix[datasets, :, :, :]
n_datasets, _,_, n_trials = feature_matrix.shape

# Detect and fill outliers (e.g. when subject did not touch the screen)
np.apply_along_axis(lambda m: utils.fill_outliers_nan(m), axis=3, arr=feature_matrix)

# Reshape matrix such that blocks from one condition are concatenated
feature_matrix = np.reshape(feature_matrix, (n_datasets, 2, n_trials*2))

# Delete the first 3 movements
feature_matrix = feature_matrix[:, :, 3:]

# Group into bins: Compute average feature in bin
n_bins = 21
if property == "median":
    feature_bin_median = np.array([np.nanmedian(arr, axis=2) for arr in np.array_split(feature_matrix, n_bins, axis=2)])
    feature_bin_std = np.array([np.nanstd(arr, axis=2) for arr in np.array_split(feature_matrix, n_bins, axis=2)])
elif property == "std":
    feature_bin_median = np.array([np.nanstd(arr, axis=2) for arr in np.array_split(feature_matrix, n_bins, axis=2)])

# Normalize to first bin and transform into percentage
feature_bin_median = ((feature_bin_median - feature_bin_median[0, :, :]) / feature_bin_median[0, :, :]) * 100

# Plot individual if needed
if plot_individual:
    for i in range(n_datasets):
        # Plot feature over time
        plt.figure(figsize=(18, 5))
        utils.plot_bins(feature_bin_median[:,i,:])
        plt.xlabel("# Bin", fontsize=14)
        plt.ylabel(f"% change in {property} {feature_name}", fontsize=14)
        # Save figure on individual basis
        plt.savefig(f"../../Plots/dataset{i}_{feature_name}_{med}.png", format="png", bbox_inches="tight")
        plt.close()

# Average over all datasets
feature_bin_median_dataset = np.median(feature_bin_median, axis=1)
feature_bin_std_dataset = np.std(feature_bin_median, axis=1)

# Plot feature over time
plt.figure(figsize=(10, 5))
utils.plot_bins(feature_bin_median_dataset, feature_bin_std_dataset)
plt.xlabel("# Bin", fontsize=14)
plt.xticks([])
plt.ylabel(f"% change in {property} {feature_name}", fontsize=14)
plt.axvline(np.floor(feature_bin_median.shape[0]/2), color="black", linewidth=2)

# Add statistics
p_vals = []
for i, bin in enumerate(feature_bin_median[1:]):
    z, p = scipy.stats.wilcoxon(x=bin[:, 0], y=bin[:, 1])
    #z, p = scipy.stats.ttest_rel(bin[:, 0], bin[:, 1])
    p_vals.append(p)
    # Add p value to plot
    if p < 0.01:
        plt.text(i+1, 10, "**", fontsize=15)
    elif p < 0.05:
        plt.text(i + 1, 10, "*", fontsize=15)
print(p_vals)

# Save figure on group basis
plt.savefig(f"../../Plots/{feature_name}_{med}_{property}.png", format="png", bbox_inches="tight")

plt.show()