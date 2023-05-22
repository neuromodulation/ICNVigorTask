# Script for investigating the task performance
# Features per stimulation condition
# Number of stimulated trials

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
from scipy.stats import percentileofscore
import matplotlib
matplotlib.use('TkAgg')
import warnings
warnings.filterwarnings("ignore")

# Set analysis parameters
feature_name = "peak_speed"
plot_individual = False
datasets_off = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20, 26, 27, 28]
datasets_on = [3, 4, 5, 7, 9, 10, 12, 18, 21, 22, 23, 24, 25]
datasets = [datasets_off, datasets_on]

# Loop over the medication condition

feature_all_med = []
for dataset in datasets:

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

    # Compute mean/median feature over all trials, only slow and only fast stimulated
    feature_all_cond = np.zeros((n_dataset, 2))
    # Loop over conditions slow/fast
    plt.figure(figsize=(12, 8))
    for i in range(n_dataset):
        feature_tmp = []
        for cond in range(2):
            feature_all_cond[i, cond] = np.nanmedian([percentileofscore(feature_matrix[i, cond, :], x, nan_policy='omit') for x in feature_matrix[i, cond, :][stim[i, cond, :] == 1]])
            feature_tmp.append([percentileofscore(feature_matrix[i, cond, :], x, nan_policy='omit') for x in feature_matrix[i, cond, :][stim[i, cond, :] == 1]])
        # Plot violin plot for each dataset
        plt.subplot(int(np.floor(n_dataset/4)), int(np.ceil(n_dataset/4)), i+1)
        y = feature_tmp[0] + feature_tmp[1]
        x = np.concatenate((np.repeat("Slow", len(feature_tmp[0])),np.repeat("Fast", len(feature_tmp[1]))))
        my_pal_trans = {"Slow": "#80c39d", "Fast": "#9c80c2", "All": "lightgrey"}
        sb.violinplot(x=x, y=y, showfliers=False, palette=my_pal_trans, split=True)
        plt.xticks([])
    plt.subplots_adjust(wspace=0.1, hspace=0.1)
    plt.show()
    # Save for plotting
    feature_all_med.extend(feature_all_cond.flatten())

# Plot as boxplot
my_pal = {"Slow": "#00863b", "Fast": "#3b0086", "All": "grey"}
my_pal_trans = {"Slow": "#80c39d", "Fast": "#9c80c2", "All": "lightgrey"}
x = np.concatenate((np.repeat("Off", len(datasets_off)*2), np.repeat("On", len(datasets_on)*2)))
hue = np.array([["Slow", "Fast"] for i in range(len(datasets_off) + len(datasets_on))]).flatten()
y = np.array(feature_all_med)
fig = plt.figure()
box = sb.violinplot(x=x, y=feature_all_med, hue=hue, showfliers=False, palette=my_pal_trans, split=True)
sb.stripplot(x=x, y=feature_all_med, dodge=True, ax=box, hue=hue, palette=my_pal, legend=None)

# Add statistics
add_stat_annotation(box, x=x, y=y, hue=hue,
                    box_pairs=[(("Off", "Slow"), ("Off", "Fast")),
                               (("On", "Slow"), ("On", "Fast"))
                               ],
                    test='Wilcoxon', text_format='simple', loc='inside', verbose=2)
# Add labels
feature_name_space = feature_name.replace("_", " ")
plt.ylabel(f"Percentile of median {feature_name_space} \nof stimulated movements", fontsize=14)
plt.xticks(fontsize=14)
plt.subplots_adjust(left=0.2)
utils.despine()

# Save the figure
plt.savefig(f"../../Plots/task_{feature_name}.svg", format="svg", bbox_inches="tight")

plt.show()