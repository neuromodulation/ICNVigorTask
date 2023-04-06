# Script for predicting change in feature based on
# Speed at start

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
datasets_off = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20, 26, 27]
normalize = True
datasets_on = [3, 4, 5, 7, 9, 10, 12, 18, 21, 22, 23, 24, 25]
datasets_all = np.arange(28)

# Load feature matrix
feature_matrix = np.load(f"../../Data/{feature_name}.npy")
n_datasets, _,_, n_trials = feature_matrix.shape

# Choose only the stimulation period
feature_matrix = feature_matrix[:, :, 0, :]

# Reshape matrix such that blocks from one condition are concatenated
feature_matrix = np.reshape(feature_matrix, (n_datasets, 2, n_trials))

# Delete the first 5 movements
feature_matrix = feature_matrix[:, :, 5:]

# Get median speed at beginning of task
median_feature_start = np.nanmedian(feature_matrix[:, :, :5], axis=(1, 2))

# Normalize to average of first 5 movements
if normalize:
   feature_matrix = utils.norm_perc(feature_matrix)
   #feature_matrix = utils.norm_perc_every_t_trials(feature_matrix, 45)

# Plot median speed for each medication and condition
off_fast_start = np.nanmedian(feature_matrix[datasets_off, 1, :45], axis=1) - np.nanmedian(feature_matrix[datasets_off, 0, :45], axis=1)
off_fast_end = np.nanmedian(feature_matrix[datasets_off, 1, -45:], axis=1) - np.nanmedian(feature_matrix[datasets_off, 0, -45:], axis=1)
x=off_fast_start
y=off_fast_end
y = median_feature_start[datasets_off]
y = np.percentile(feature_matrix[datasets_off, 1, :], 85, axis=1)
corr, p = spearmanr(x, y)
plt.figure()
sb.regplot(x=x, y=y)
plt.title(f"Off corr = {np.round(corr, 2)}, p = {np.round(p, 3)}", fontweight='bold')
# Add labels
feature_name_space = feature_name.replace("_", " ")
if normalize:
    plt.xlabel(f"Difference Fast-Slow of change in {feature_name_space} \n in first half of block[%]", fontsize=12)
    plt.ylabel(f"Difference Fast-Slow of change in {feature_name_space} \n in last half of block[%]", fontsize=12)
else:
    plt.xlabel(f"Difference Fast-Slow in {feature_name_space} \n in first half of block[%]", fontsize=12)
    plt.ylabel(f"Difference Fast-Slow in {feature_name_space} \n in last half of block[%]", fontsize=12)

# Save figure
plt.subplots_adjust(bottom=0.2, left=0.2)
plt.savefig(f"../../Plots/corr_diff_{feature_name}_normalize_{normalize}.svg", format="svg", bbox_inches="tight")

plt.show()