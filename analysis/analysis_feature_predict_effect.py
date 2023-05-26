# Script for predicting the stimulation effect based on the percentile of the stimulated movements

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
feature_name = "peak_dec"
normalize = True
datasets_off = [8, 11, 13, 14, 15, 16, 17, 19, 20, 26, 27, 28]
datasets_on = [3, 4, 5, 7, 9, 10, 12, 18, 21, 22, 23, 24, 25, 29]
dataset = datasets_off
#dataset = datasets_on

# Load feature matrix
feature_matrix = np.load(f"../../Data/{feature_name}.npy")
fast = np.load(f"../../Data/fast.npy")
slow = np.load(f"../../Data/slow.npy")
stim = np.load(f"../../Data/stim.npy")

# Select the dataset of interest
feature_matrix = feature_matrix[dataset, :, :, :]
stim = stim[dataset, :, :, :]
fast = fast[dataset, :, :, :]
slow = slow[dataset, :, :, :]
n_dataset, _, _, n_trials = feature_matrix.shape

# Delete outliers
np.apply_along_axis(lambda m: utils.fill_outliers_nan(m, threshold=3), axis=3, arr=feature_matrix)
np.apply_along_axis(lambda m: utils.fill_outliers_nan(m, threshold=3), axis=3, arr=feature_matrix)

# Loop over stimulation and recovery blocks
block_names = ["Stimulation", "Recovery"]
plt.figure(figsize=(10, 4))
for block in range(2):

    # Select only the block of interest and delete the first 5 movements
    feature_matrix_tmp = feature_matrix[:, :, block, 5:]
    stim_tmp = stim[:, :, block, 5:]
    fast_tmp = fast[:, :, block, 5:]
    slow_tmp = slow[:, :, block, 5:]

    # Normalize to average of next 5 movements
    feature_matrix_tmp = utils.norm_perc(feature_matrix_tmp)

    """
    feature_matrix_tmp = feature_matrix_tmp[:, :, :45]
    stim_tmp = stim_tmp[:, :, :45]
    fast_tmp = fast_tmp[:, :, :45]
    slow_tmp = slow_tmp[:, :, :45]"""

    # Get the difference in peak speed between the conditions for all datasets
    diff_effect = np.nanmedian(feature_matrix_tmp[:, 1, :], axis=1) - np.nanmedian(feature_matrix_tmp[:, 0, :], axis=1)

    # Get the difference between percentile of Slow vs Fast movements for all datasets
    diff_percentile_stim = np.zeros(n_dataset)

    for i in range(n_dataset):
        # Select stimulated movements if block == 1 and post-hoc determined slow/fast movements for block == 1
        if block == 0:
            diff_percentile_stim[i] = np.nanmedian([percentileofscore(feature_matrix_tmp[i, 1, :], x, nan_policy='omit')
                                                    for x in feature_matrix_tmp[i, 1, :][stim_tmp[i, 1, :] == 1]]) - \
                                     np.nanmedian([percentileofscore(feature_matrix_tmp[i, 0, :], x, nan_policy='omit')
                                                   for x in feature_matrix_tmp[i, 0, :][stim_tmp[i, 0, :] == 1]])
        else:
            diff_percentile_stim[i] = np.nanmedian([percentileofscore(feature_matrix_tmp[i, 1, :], x, nan_policy='omit')
                                                    for x in feature_matrix_tmp[i, 1, :][fast_tmp[i, 1, :] == 1]]) - \
                                      np.nanmedian([percentileofscore(feature_matrix_tmp[i, 0, :], x, nan_policy='omit')
                                                    for x in feature_matrix_tmp[i, 0, :][slow_tmp[i, 0, :] == 1]])
    # Compute correlation coefficient and plot
    plt.subplot(1, 2, block+1)
    x = diff_effect
    y = diff_percentile_stim
    corr, p = spearmanr(x, y, nan_policy='omit')
    sb.regplot(x=x, y=y)
    plt.title(f"corr = {np.round(corr, 2)}, p = {np.round(p, 3)}", fontweight='bold')
    feature_name_space = feature_name.replace("_", " ")
    plt.xlabel(f"Difference Fast-Slow of change \n in peak speed [%]", fontsize=12)
    plt.ylabel(f"Difference of stimulated percentile of \n {feature_name_space} in block {block_names[block]}", fontsize=12)

plt.subplots_adjust(left=0.2, bottom=0.2, wspace=0.4, hspace=0.4)

# Save the figure
plt.savefig(f"../../Plots/predict_effect_{feature_name}.svg", format="svg", bbox_inches="tight")

plt.show()