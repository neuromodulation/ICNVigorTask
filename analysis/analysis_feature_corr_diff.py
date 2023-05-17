# Script for correlating size of stimulation effect with different measures

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
feature_name_space = feature_name.replace("_", " ")
datasets_off = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20, 26, 27, 28]
normalize = True
datasets_on = [3, 4, 5, 7, 9, 10, 12, 18, 21, 22, 23, 24, 25, 29]
datasets_all = np.arange(30)

# Load feature matrix
feature_matrix = np.load(f"../../Data/{feature_name}.npy")
n_datasets, _,_, n_trials = feature_matrix.shape

# Choose only the stimulation period
feature_matrix = feature_matrix[:, :, 0, :]

# Reshape matrix such that blocks from one condition are concatenated
feature_matrix = np.reshape(feature_matrix, (n_datasets, 2, n_trials))

# Detect and fill outliers (e.g. when subject did not touch the screen)
np.apply_along_axis(lambda m: utils.fill_outliers_mean(m, threshold=3), axis=2, arr=feature_matrix)

# Get median speed at beginning of task
median_feature_start = np.nanmedian(feature_matrix[:, :, :5], axis=(1, 2))

# Delete the first 5 movements
feature_matrix = feature_matrix[:, :, 5:]

# Normalize to average of first 5 movements
feature_matrix_non_norm = feature_matrix.copy()
if normalize:
   feature_matrix = utils.norm_perc(feature_matrix)
   #feature_matrix = utils.norm_perc_every_t_trials(feature_matrix, 45)

# Define x as the effect in the first half of the stimulation period (difference fast-slow)
x = np.nanmedian(feature_matrix[datasets_off, 1, :45], axis=1) - np.nanmedian(
    feature_matrix[datasets_off, 0, :45], axis=1)
# Loop over different measures that could be correlated

off_fast_end = np.nanmedian(feature_matrix[datasets_off, 1, -45:], axis=1) - np.nanmedian(
    feature_matrix[datasets_off, 0, -45:], axis=1)

init_feature = median_feature_start[datasets_off]

diff_feature_fast = np.nanmedian(np.abs(np.diff(feature_matrix_non_norm[datasets_off, 1, :45], axis=1)), axis=1)

range = np.mean(np.percentile(feature_matrix_non_norm[datasets_off, :, :45], 95, axis=2) - \
        np.percentile(feature_matrix_non_norm[datasets_off, :, :45], 5, axis=2), axis=1)

UPDRS = np.array([None, 26, 31, 22, 22, 27, 14, 14, 25, 18, 33, None, 30, 12, 28, 13, 27, 35, 28, 32, 23, 15, 14, None, 48, None, 35, 37, 36])
UPDRS_off = UPDRS[datasets_off]

features = [init_feature, off_fast_end, diff_feature_fast, range, UPDRS_off]
labels = [f"Initial {feature_name_space}",
          f"Difference Fast-Slow of change in {feature_name_space} \n in second half of block[%]",
          f"Difference consecutive trials in {feature_name_space}",
          f"Range of {feature_name_space} in both conditions",
          "UPDRS"
          ]
for i, y in enumerate(features):
    if i == 4:
        x = x[UPDRS_off != None]
        UPDRS_off = UPDRS_off[UPDRS_off != None].astype(np.int32)
        y = UPDRS_off

    corr, p = spearmanr(x, y)
    plt.figure()
    sb.regplot(x=x, y=y)
    plt.title(f"Off corr = {np.round(corr, 2)}, p = {np.round(p, 3)}", fontweight='bold')
    # Add labels
    if normalize:
        plt.xlabel(f"Difference Fast-Slow of change in {feature_name_space} \n in first half of block[%]", fontsize=12)
    else:
        plt.xlabel(f"Difference Fast-Slow in {feature_name_space} \n in first half of block[%]", fontsize=12)
    plt.ylabel(labels[i], fontsize=12)
    utils.despine()

    # Save figure
    plt.subplots_adjust(bottom=0.2, left=0.2)
    plt.savefig(f"../../Plots/corr_diff_{feature_name}_{i}_normalize_{normalize}.svg", format="svg", bbox_inches="tight")

plt.show()