# Script for analysing variability of a feature over time

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
from scipy.stats import pearsonr, spearmanr
import matplotlib
matplotlib.use('TkAgg')
import warnings
warnings.filterwarnings("ignore")

# Set analysis parameters
feature_name = "peak_speed" # out of ["peak_acc", "mean_speed", "move_dur", "peak_speed", "stim_time", "peak_speed_time", "move_onset_time", "move_offset_time"]
block = "stim" # recovery or stim
datasets_off = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20, 26, 27]
normalize = False
datasets_on = [3, 4, 5, 7, 9, 10, 12, 18, 21, 22, 23, 24, 25]
datasets_all = np.arange(28)

# Load feature matrix
feature_matrix = np.load(f"../../Data/{feature_name}.npy")
n_datasets, _,_, n_trials = feature_matrix.shape

# Choose only the stimulation period
feature_matrix = feature_matrix[:, :, :, :]

# Detect and fill outliers (e.g. when subject did not touch the screen)
np.apply_along_axis(lambda m: utils.fill_outliers_nan(m, threshold=3), axis=3, arr=feature_matrix)

# Reshape matrix such that blocks from one condition are concatenated
feature_matrix = np.reshape(feature_matrix, (n_datasets, 2, n_trials*2))

# Delete the first 5 movements
feature_matrix = feature_matrix[:, :, 5:]

# Normalize to average of first 5 movements
if normalize:
   feature_matrix = utils.norm_perc(feature_matrix)
   #feature_matrix = utils.norm_perc_every_t_trials(feature_matrix, 45)

if block == "recovery":
    feature_matrix = feature_matrix[:, :, 91:181]
else:
    feature_matrix = feature_matrix[:, :, :90]

# Plot the variability over time (in bins)
n_bins = 9
feature_bin_median = np.array([np.nanstd(arr, axis=2) for arr in np.array_split(feature_matrix, n_bins, axis=2)])

#feature_bin_median = np.array([np.nanpercentile(arr, 90, axis=2) - np.nanpercentile(arr, 10, axis=2) for arr in np.array_split(feature_matrix, n_bins, axis=2)])

#feature_bin_median = np.array([np.nanvar(arr, axis=2) for arr in np.array_split(feature_matrix, n_bins, axis=2)])


# Normalize to first bin and transform into percentage
feature_bin_median = ((feature_bin_median - feature_bin_median[0, :, :]) / feature_bin_median[0, :, :]) * 100

# Average over all datasets
feature_bin_median_dataset = np.nanmedian(feature_bin_median, axis=1)
feature_bin_std_dataset = np.nanstd(feature_bin_median, axis=1)

# Plot feature over time
fig = plt.figure()
utils.plot_bins(feature_bin_median_dataset)
plt.xlabel("Number of bin", fontsize=14)
feature_name_space = feature_name.replace("_", " ")
plt.ylabel(f"Change in {feature_name_space} [%]", fontsize=14)
# Add line to mark end of stimulation
axes = plt.gca()
ymin, ymax = axes.get_ylim()
plt.subplots_adjust(bottom=0.2, left=0.15)
utils.adjust_plot(fig)
plt.legend()
plt.show()