# Script for analysing the difference between stimulated movements to the current mean

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
feature_name = "peak_speed"
plot_individual = False
normalize = True
datasets_off = [1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20, 26, 27]
datasets_on = [3, 4, 5, 7, 9, 10, 12, 18, 21, 22, 23, 24, 25]
dataset = datasets_off
#dataset = np.arange(28)

# Load feature matrix
feature_matrix = np.load(f"../../Data/{feature_name}.npy")

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

# Loop over the first and second half of the stimulation block
feature_all = []
cond_names = ["Slow", "Fast"]
half_names = ["First half", "Second half"]
n_moves = 25
for half in range(2):

    if half == 0:
        feature_matrix_tmp = feature_matrix[:, :, :n_moves]
        feature_matrix_nn_tmp = feature_matrix_non_norm[:, :, :n_moves]
        stim_tmp = stim[:, :, :n_moves]
    else:
        feature_matrix_tmp = feature_matrix[:, :, 45:]
        feature_matrix_nn_tmp = feature_matrix_non_norm[:, :, 45:]
        stim_tmp = stim[:, :, 45:]

    # Compute the median distance of the stimulated movements to the mean of all movements
    feature_all_cond = np.zeros((n_dataset, 2))
    # Loop over conditions slow/fast
    for cond in range(2):
        for i in range(n_dataset):
            #stim_feature = np.nanmedian(feature_matrix_nn_tmp[i, cond, :][stim_tmp[i, cond, :] == 1])
            #median_feature = np.nanmedian(feature_matrix_nn_tmp[i, cond, :])
            #feature_all_cond[i, cond] = stim_feature - median_feature
            feature_all_cond[i, cond] = np.nanmedian([percentileofscore(feature_matrix_nn_tmp[i, cond, :], x) for x in feature_matrix_nn_tmp[i, cond, :][stim_tmp[i, cond, :] == 1]])

    # Save for plotting
    feature_all.extend(feature_all_cond.flatten())

    # Extract effect
    x = np.nanmedian(feature_matrix[:, 1, 45:], axis=1) - np.nanmedian(feature_matrix[:, 0, 45:], axis=1)
    # Correlate it with the difference between stimulated and mean movements
    plt.figure(figsize=(12, 4))
    for cond in range(2):
        plt.subplot(1, 2, cond + 1)
        y = feature_all_cond[:, cond]
        corr, p = spearmanr(x, y)
        sb.regplot(x=x, y=y)
        plt.title(f"{cond_names[cond]} corr = {np.round(corr, 2)}, p = {np.round(p, 3)}", fontweight='bold')
        feature_name_space = feature_name.replace("_", " ")
        plt.xlabel(f"Difference Fast-Slow of change \n in {feature_name_space} second half [%]", fontsize=12)
        plt.ylabel(f"Percentile of {feature_name_space} \n stimulated moves", fontsize=1)
    plt.suptitle(f"{half_names[half]}", fontweight='bold')

# Plot as boxplot
my_pal = {"Slow": "#00863b", "Fast": "#3b0086", "All": "grey"}
my_pal_trans = {"Slow": "#80c39d", "Fast": "#9c80c2", "All": "lightgrey"}
x = np.concatenate((np.repeat("First Half", len(dataset)*2), np.repeat("Last Half", len(dataset)*2)))
hue = np.array([["Slow", "Fast"] for i in range(len(dataset)*2)]).flatten()
y = np.array(feature_all)
fig = plt.figure()
box = sb.boxplot(x=x, y=y, hue=hue, showfliers=False, palette=my_pal_trans)
sb.stripplot(x=x, y=y, dodge=True, ax=box, hue=hue, palette=my_pal, legend=None)

# Add statistics
add_stat_annotation(box, x=x, y=y, hue=hue,
                    box_pairs=[(("First Half", "Slow"), ("Last Half", "Slow")),
                               (("First Half", "Fast"), ("Last Half", "Fast"))],
                    test='Wilcoxon', text_format='simple', loc='inside', verbose=2)
# Add labels
feature_name_space = feature_name.replace("_", " ")
plt.ylabel(f"Percentile of median {feature_name_space}", fontsize=14)
plt.xticks(fontsize=14)

# Save the figure
plt.savefig(f"../../Plots/stim_diff_{feature_name}.svg", format="svg", bbox_inches="tight")

plt.show()