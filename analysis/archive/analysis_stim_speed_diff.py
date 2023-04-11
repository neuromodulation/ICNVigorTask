# Plot difference of feature of stimulated movements to mean of all movements in bins

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
import scipy
matplotlib.use('TkAgg')
import warnings
warnings.filterwarnings("ignore")

# Set analysis parameters
feature_name = "peak_speed"
plot_individual = False
med = "off"  # "on", "off", "all"
if med == "all":
    datasets = np.range(26)
elif med == "off":
    datasets = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20]
else:
    datasets = [3, 4, 5, 7, 9, 10, 12, 18, 21, 22, 23, 24, 25]

# Load feature matrix
feature_matrix = np.load(f"../../Data/{feature_name}.npy")
feature_matrix = feature_matrix[datasets, :, :, :]
n_datasets, _,_, n_trials = feature_matrix.shape

# Detect and fill outliers (e.g. when subject did not touch the screen)
np.apply_along_axis(lambda m: utils.fill_outliers_nan(m), axis=3, arr=feature_matrix)

# Normalize to the start of each stimulation block (mean peak speed of movement 5-10)
feature_matrix = utils.norm_perc(feature_matrix)

# Load stim time matrix
stim_time = np.load(f"../../Data/stim_time.npy")
stim_time = stim_time[datasets, :, :, :]

# Reshape matrix such that blocks from one condition are concatenated
feature_matrix = np.reshape(feature_matrix, (n_datasets, 2, n_trials*2))
stim_time = np.reshape(stim_time, (n_datasets, 2, n_trials*2))

# Delete the first 3 movements
feature_matrix = feature_matrix[:, :, 5:]
stim_time = stim_time[:, :, 5:]

# Get index of stimulated movements
idx_nan = np.where(np.isnan(stim_time))

# Set peak speeds of non stimulated movements to nan
feature_matrix_stim = feature_matrix.copy()
feature_matrix_stim[idx_nan] = None

# Group into bins: Compute average feature in bin
n_bins = 21
feature_bin_median = np.array([np.nanmean(arr, axis=2) for arr in np.array_split(feature_matrix, n_bins, axis=2)])
feature_stim_bin_median = np.array([np.nanmean(arr, axis=2) for arr in np.array_split(feature_matrix_stim, n_bins, axis=2)])

# Compute difference between stim and non stim feature
feature_bin_diff = feature_stim_bin_median - feature_bin_median

# Average over datasets
feature_bin_diff_mean = np.nanmedian(feature_bin_diff, axis=1)
feature_bin_diff_std = np.nanstd(feature_bin_diff, axis=1)

# Plot it
cond_names = ["Slow", "Fast"]
colors = ["blue", "red"]
plt.figure(figsize=(5, 5))
for cond in range(2):
    # Plot difference in average speed
    x = np.arange(10)
    plt.plot(feature_bin_diff_mean[:10, cond], color=colors[cond], label=cond_names[cond], linewidth=3)
    plt.fill_between(x, feature_bin_diff_mean[:10, cond] - feature_bin_diff_std[:10, cond],
    feature_bin_diff_mean[:10, cond] + feature_bin_diff_std[:10, cond], color=colors[cond], alpha=0.5)

plt.legend()
plt.xlabel("# Bin", fontsize=14)
plt.xticks([])
plt.ylabel(f"difference in change in {feature_name}", fontsize=14)

# Significant difference between start and end
start = np.nanmean(feature_bin_diff[:3, :, 1], axis=0)
end = np.nanmean(feature_bin_diff[7:10, :, 1], axis=0)
z, p = scipy.stats.wilcoxon(x=start, y=end)

plt.savefig(f"../../Plots/{feature_name}_stim_diff_{med}.png", format="png", bbox_inches="tight")

plt.show()