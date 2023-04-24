# Script for predict the stimulation eggect based on the percentile of the stimulated movements

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

# Load feature matrix
feature_matrix = np.load(f"../../Data/{feature_name}.npy")

# Load feature matrix
feature_matrix_speed = np.load(f"../../Data/peak_speed.npy")
feature_matrix_speed = feature_matrix_speed[dataset, :, 0, :]
np.apply_along_axis(lambda m: utils.fill_outliers_mean(m, threshold=3), axis=2, arr=feature_matrix_speed)
feature_matrix_speed = feature_matrix_speed[:, :, 5:]
feature_matrix_speed = utils.norm_perc(feature_matrix_speed)

# Select datasets of interest, keep only stimulation block
feature_matrix = feature_matrix[dataset, :, 0, :]
n_dataset, _, n_trials = feature_matrix.shape

# Detect and fill outliers (e.g. when subject did not touch the screen)
np.apply_along_axis(lambda m: utils.fill_outliers_mean(m, threshold=3), axis=2, arr=feature_matrix)

# Load stim time matrix
stim_time = np.load(f"../../Data/stim_time.npy")
stim_time = stim_time[dataset, :, 0, :]

# Select only stimulated movements
stim = stim_time.copy()
stim[np.isnan(stim)] = 0
stim[np.nonzero(stim)] = 1
stim = stim.astype(int)

# Delete the first 5 movements
feature_matrix = feature_matrix[:, :, 5:]
stim = stim[:, :, 5:]

# Normalize to average of first 5 movements
feature_matrix_non_norm = feature_matrix.copy()
if normalize:
    feature_matrix = utils.norm_perc(feature_matrix)

cond_names = ["Slow", "Fast"]
half_names = ["First half", "Second half"]
n_moves = 40
feature_matrix_start = feature_matrix[:, :, :n_moves]
feature_matrix_nn_start = feature_matrix_non_norm[:, :, :n_moves]
stim_start = stim[:, :, :n_moves]
percentile_stim = np.zeros((n_dataset))
# Get the percentile of the stimulated fast movements
for i in range(n_dataset):
    percentile_stim[i] = np.nanmedian([percentileofscore(feature_matrix_nn_start[i, 1, :], x, nan_policy='omit') for x in feature_matrix_nn_start[i, 1, :][stim_start[i, 1, :] == 1]])
    #percentile_stim[i] = np.nanmedian([percentileofscore(feature_matrix_nn_start[i, 0, :], x, nan_policy='omit') for x in feature_matrix_nn_start[i, 0, :][stim_start[i, 0, :] == 1]])
    #percentile_stim[i] = np.nanmedian([percentileofscore(feature_matrix_nn_start[i, 0, :], x, nan_policy='omit') for x in feature_matrix_nn_start[i, 0, :][stim_start[i, 0, :] == 1]]) - \
    #                     np.nanmedian([percentileofscore(feature_matrix_nn_start[i, 1, :], x, nan_policy='omit') for x in feature_matrix_nn_start[i, 1, :][stim_start[i, 1, :] == 1]])

# Correlate percentile of fast stimulated movements with stimulation effect
plt.figure(figsize=(11, 4))
plt.subplot(1, 2, 1)
# Compute effect of stimulation in the second part of the experiment
#x = np.nanmedian(feature_matrix[:, 1, 45:], axis=1) - np.nanmedian(feature_matrix[:, 0, 45:], axis=1)
#x = np.nanmedian(feature_matrix[:, 1, :n_moves], axis=1) - np.nanmedian(feature_matrix[:, 0, :n_moves], axis=1)
x = np.nanmedian(feature_matrix[:, 1, :], axis=1) - np.nanmedian(feature_matrix[:, 0, :], axis=1)
#x = np.nanmedian(feature_matrix_speed[:, 1, :], axis=1) - np.nanmedian(feature_matrix_speed[:, 0, :], axis=1)
y = percentile_stim
corr, p = spearmanr(x, y, nan_policy='omit')
sb.regplot(x=x, y=y)
plt.title(f"corr = {np.round(corr, 2)}, p = {np.round(p, 3)}", fontweight='bold')
feature_name_space = feature_name.replace("_", " ")
plt.xlabel(f"Difference Fast-Slow of change \n in peak speed [%]", fontsize=12)
plt.ylabel(f"Percentile of {feature_name_space} \n fast stim in first {n_moves} moves", fontsize=12)
plt.subplots_adjust(left=0.2, bottom=0.2)

# Correlate percentile of fast stimulated movements with median feature
plt.subplot(1, 2, 2)
x = np.nanmedian(feature_matrix_speed[:, 1, :n_moves], axis=1)
y = percentile_stim
corr, p = spearmanr(x, y)
sb.regplot(x=x, y=y)
plt.title(f"corr = {np.round(corr, 2)}, p = {np.round(p, 3)}", fontweight='bold')
feature_name_space = feature_name.replace("_", " ")
plt.xlabel(f"Median \n in peak speed in first {n_moves} moves [%]", fontsize=12)
plt.ylabel(f"Percentile of {feature_name_space} \n fast stim in first {n_moves} moves", fontsize=12)
plt.subplots_adjust(left=0.2, bottom=0.2, wspace=0.4)

# Save the figure
plt.savefig(f"../../Plots/stim_diff_corr_{feature_name}.svg", format="svg", bbox_inches="tight")

plt.show()