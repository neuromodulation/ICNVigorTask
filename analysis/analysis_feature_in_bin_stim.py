# Plot feature of stimulated movements over time

import numpy as np
import matplotlib.pyplot as plt
import mne
import gc
import utils.utils as utils
from mne_bids import BIDSPath, read_raw_bids, print_dir_tree, make_report
from alive_progress import alive_bar
import time
from statannot import add_stat_annotation
import seaborn as sb
from scipy import stats
import matplotlib
from scipy.stats import pearsonr, spearmanr
matplotlib.use('TkAgg')
import warnings
warnings.filterwarnings("ignore")

# Set analysis parameters
plot_individual = False
feature_name = "peak_speed"
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

# Normalize to average of 5-10
feature_matrix = utils.norm_perc(feature_matrix)

# Load stim time matrix
stim_time = np.load(f"../../Data/stim_time.npy")
stim_time = stim_time[datasets, :, :, :]

# Reshape matrix such that blocks from one condition are concatenated
feature_matrix = np.reshape(feature_matrix, (n_datasets, 2, n_trials*2))
stim_time = np.reshape(stim_time, (n_datasets, 2, n_trials*2))

# Delete the first 3 movements
feature_matrix = feature_matrix[:, :, 3:]
stim_time = stim_time[:, :, 3:]

# Get index of not stimulated movements
idx_not_stim = np.where(np.isnan(stim_time))

# Set feature of non stimulated movements to nan
feature_matrix_stim = feature_matrix.copy()
feature_matrix_stim[idx_not_stim] = None

# Group into bins: Compute average feature in bin
n_bins = 21
feature_stim_bin = np.array([np.nanmean(arr, axis=2) for arr in np.array_split(feature_matrix_stim, n_bins, axis=2)])
feature_bin = np.array([np.nanmean(arr, axis=2) for arr in np.array_split(feature_matrix, n_bins, axis=2)])

# Normalize to first bin of all movements and transform into percentage
#feature_stim_bin = ((feature_stim_bin - feature_bin[0, :, :]) / feature_bin[0, :, :]) * 100
#feature_bin = ((feature_bin - feature_bin[0, :, :]) / feature_bin[0, :, :]) * 100

# Compute and plot average over datasets
cond_names = ["Slow", "Fast"]
colors = ["#00863b", "#3b0086"]
x = np.arange(len(feature_bin[:10, :, :]))
fig = plt.figure()
for cond in range(2):

    # Plot all moves
    feature_bin_all_median = np.nanmedian(feature_bin[:10, :, cond], axis=1)
    feature_bin_all_std = np.nanstd(feature_bin[:10, :, cond], axis=1)
    plt.plot(feature_bin_all_median, label=cond_names[cond]+" all moves", color=colors[cond], linewidth=3)
    # Plot std
    #plt.fill_between(x, feature_bin_all_median - feature_bin_all_std, feature_bin_all_median + feature_bin_all_std, alpha=0.2, color=colors[cond])

    # Plot only stimulated movements
    feature_bin_stim_median = np.nanmedian(feature_stim_bin[:10, :, cond], axis=1)
    feature_bin_stim_std = np.nanstd(feature_stim_bin[:10, :, cond], axis=1)
    plt.plot(feature_bin_stim_median, label=cond_names[cond] + " stim", color=colors[cond], linestyle="dashed", linewidth=3)
    # Plot std
    plt.fill_between(x, feature_bin_stim_median - feature_bin_stim_std, feature_bin_stim_median + feature_bin_stim_std,
                     alpha=0.2, color=colors[cond])

plt.legend()
plt.xlabel("Number of bin", fontsize=14)
feature_name_space = feature_name.replace("_", " ")
plt.ylabel(f"Change in {feature_name_space} [%]", fontsize=14)
plt.xlim([0, 9])
utils.adjust_plot(fig)
plt.subplots_adjust(bottom=0.2, left=0.15)

plt.savefig(f"../../Plots/{feature_name}_all_stim_{med}.png", format="png", bbox_inches="tight")

plt.show()