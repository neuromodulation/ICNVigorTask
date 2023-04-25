# Script for predicting the stimulation effect based on the percentile of the stimulated movements
# Control using fast/slow movements from not stimulated blocks

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
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
from scipy.stats import pearsonr, spearmanr, percentileofscore
matplotlib.use('TkAgg')
import warnings
warnings.filterwarnings("ignore")

# Set analysis parameters
feature_name = "peak_deacc"
plot_individual = False
normalize = True
datasets_off = [1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20, 26, 27]
datasets_on = [3, 4, 5, 7, 9, 10, 12, 18, 21, 22, 23, 24, 25]
dataset = datasets_off
#dataset = datasets_on
#dataset = np.arange(28)

# Load feature matrix, slow, fast and stim time
feature_matrix = np.load(f"../../Data/{feature_name}.npy")
feature_matrix_speed = np.load(f"../../Data/peak_deacc.npy")
slow = np.load(f"../../Data/slow.npy")
fast = np.load(f"../../Data/fast.npy")
stim_time = np.load(f"../../Data/stim_time.npy")

# Select datasets of interest
feature_matrix = feature_matrix[dataset, :, :, :]
feature_matrix_speed = feature_matrix_speed[dataset, :, :, :]
slow = slow[dataset, :, :, :]
fast = fast[dataset, :, :, :]
stim_time = stim_time[dataset, :, :, :]
n_dataset, _, _, n_trials = feature_matrix.shape

# Get array in which stimulated movements are marked with 1, else 0
stim = stim_time.copy()
stim[np.isnan(stim)] = 0
stim[np.nonzero(stim)] = 1
stim = stim.astype(int)

# Detect and fill outliers in the feature matrices (e.g. when subject did not touch the screen)
np.apply_along_axis(lambda m: utils.fill_outliers_mean(m, threshold=3), axis=3, arr=feature_matrix)
np.apply_along_axis(lambda m: utils.fill_outliers_mean(m, threshold=3), axis=3, arr=feature_matrix_speed)

# Loop over the stimulation and recovery block
block_names = ["stim", "recovery"]
plt.figure(figsize=(11, 8))
for block in range(2):

    # Select the block and delete the first 5 movements
    feature_matrix_tmp = feature_matrix[:, :, block, 5:]
    feature_matrix_speed_tmp = feature_matrix_speed[:, :, block, 5:]
    stim_tmp = stim[:, :, block, 5:]
    slow_tmp = slow[:, :, block, 5:]
    fast_tmp = fast[:, :, block, 5:]

    # Normalize to average of first 5 movements
    feature_matrix_non_norm_tmp = feature_matrix_tmp.copy()
    if normalize:
        feature_matrix_tmp = utils.norm_perc(feature_matrix_tmp)
        feature_matrix_speed_tmp = utils.norm_perc(feature_matrix_speed_tmp)

    # Get the median feature in both conditions
    median_feature = np.nanmedian(feature_matrix_tmp, axis=2)

    # Loop over the datasets and get the percentile of slow/fast movements
    percentile = np.zeros((n_dataset, 2))
    # Get the percentile of the stimulated fast movements
    for i in range(n_dataset):
        # Get the percentile
        if block == 0:
            percentile[i, 0] = np.nanmedian(
                [percentileofscore(feature_matrix_non_norm_tmp[i, 0, :], x, nan_policy='omit') for x in
                 feature_matrix_non_norm_tmp[i, 0, :][fast_tmp[i, 0, :] == 1]])
            percentile[i, 1] = np.nanmedian(
                [percentileofscore(feature_matrix_non_norm_tmp[i, 1, :], x, nan_policy='omit') for x in
                 feature_matrix_non_norm_tmp[i, 1, :][stim_tmp[i, 1, :] == 1]])
        else:
            percentile[i, 0] = np.nanmedian(
                [percentileofscore(feature_matrix_non_norm_tmp[i, 0, :], x, nan_policy='omit') for x in
                 feature_matrix_non_norm_tmp[i, 0, :][fast_tmp[i, 0, :] == 1]])
            percentile[i, 1] = np.nanmedian(
                [percentileofscore(feature_matrix_non_norm_tmp[i, 1, :], x, nan_policy='omit') for x in
                 feature_matrix_non_norm_tmp[i, 1, :][fast_tmp[i, 1, :] == 1]])

    # Correlate with median change in peak speed
    plt.subplot(2, 2, block*2 + 1)
    #plt.subplot(2, 2, 1)
    y = percentile[:, 0]
    x = median_feature[:, 0]
    corr, p = spearmanr(x, y, nan_policy='omit')
    sb.regplot(x=x, y=y)
    plt.title(f"corr = {np.round(corr, 2)}, p = {np.round(p, 3)}", fontweight='bold')
    feature_name_space = feature_name.replace("_", " ")
    plt.xlabel(f"{feature_name_space} [%]", fontsize=12)
    plt.ylabel(f"Percentile of {feature_name_space} \n fast movements slow {block_names[block]} block", fontsize=12)

    plt.subplot(2, 2, block * 2 + 2)
    #plt.subplot(2, 2, 1)
    y = percentile[:, 1]
    x = median_feature[:, 1]
    corr, p = spearmanr(x, y, nan_policy='omit')
    sb.regplot(x=x, y=y)
    plt.title(f"corr = {np.round(corr, 2)}, p = {np.round(p, 3)}", fontweight='bold')
    feature_name_space = feature_name.replace("_", " ")
    plt.xlabel(f"{feature_name_space} [%]", fontsize=12)
    plt.ylabel(f"Percentile of {feature_name_space} \n fast movements fast {block_names[block]} block", fontsize=12)

plt.subplots_adjust(left=0.2, bottom=0.2, wspace=0.4, hspace=0.5)

# Save the figure
plt.savefig(f"../../Plots/perc_median_corr_{feature_name}.svg", format="svg", bbox_inches="tight")

plt.show()