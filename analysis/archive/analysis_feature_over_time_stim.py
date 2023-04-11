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

# Load stim time matrix
stim_time = np.load(f"../../Data/stim_time.npy")
stim_time = stim_time[datasets, :, :, :]

# Reshape matrix such that blocks from one condition are concatenated
feature_matrix = np.reshape(feature_matrix, (n_datasets, 2, n_trials*2))
stim_time = np.reshape(stim_time, (n_datasets, 2, n_trials*2))

# Delete the first 3 movements
feature_matrix = feature_matrix[:, :, 5:]
stim_time = stim_time[:, :, 5:]

# Normalize to average of 5-10
feature_matrix = utils.norm_perc(feature_matrix)

# Get index of not stimulated movements
idx_not_stim = np.where(np.isnan(stim_time))

# Set feature of non stimulated movements to nan
feature_matrix_stim = feature_matrix.copy()
feature_matrix_stim[idx_not_stim] = None

# Smooth over 5 consecutive movements for plotting
feature_matrix = utils.smooth_moving_average(feature_matrix, window_size=5, axis=2)
feature_matrix_stim = utils.smooth_moving_average(feature_matrix_stim, window_size=5, axis=2)

# Plot the mean of all datasets
feature_matrix_mean = np.nanmean(feature_matrix, axis=0)
feature_matrix_std = np.nanstd(feature_matrix, axis=0)
utils.plot_conds(feature_matrix_mean, feature_matrix_std)
plt.show()

# Plot the mean of only stimulated movements in all datasets
feature_matrix_mean = np.nanmean(feature_matrix_stim, axis=0)
feature_matrix_std = np.nanstd(feature_matrix_stim, axis=0)
utils.plot_conds(feature_matrix, feature_matrix_std)

plt.show()

plt.savefig(f"../../Plots/{feature_name}_all_stim_{med}.png", format="png", bbox_inches="tight")

plt.show()