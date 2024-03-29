# Script for statsitical analysis of feature

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
import matplotlib
matplotlib.use('TkAgg')
import warnings
warnings.filterwarnings("ignore")

# Set analysis parameters
feature_name = "peak_speed" # out of ["peak_acc", "mean_speed", "move_dur", "peak_speed", "stim_time", "peak_speed_time", "move_onset_time", "move_offset_time"]
plot_individual = False
med = "off"  # "on", "off", "all"
if med == "all":
    datasets = np.arange(26)
elif med == "off":
    datasets = [1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20, 26, 27, 28, 30]
else:
    datasets = [3, 4, 5, 7, 9, 10, 12, 18, 21, 22, 23, 24, 25]

# Load feature matrix
feature_matrix = np.load(f"../../Data/{feature_name}.npy")
trial_side = np.load(f"../../Data/trial_side.npy")

# Select datasets of interest
feature_matrix = feature_matrix[datasets, :, :, :]
trial_side = trial_side[datasets, :, :, :]
n_datasets, _,_, n_trials = feature_matrix.shape

# Detect and fill outliers (e.g. when subject did not touch the screen)
np.apply_along_axis(lambda m: utils.fill_outliers_nan(m), axis=3, arr=feature_matrix)
#np.apply_along_axis(lambda m: utils.fill_outliers_nan(m), axis=3, arr=feature_matrix)

# Reshape matrix such that blocks from one condition are concatenated
feature_matrix = np.reshape(feature_matrix, (n_datasets, 2, n_trials*2))
trial_side = np.reshape(trial_side, (n_datasets, 2, n_trials*2))

# Delete the first 5 movements
feature_matrix = feature_matrix[:, :, 5:]
trial_side = trial_side[:, :, 5:]

# Normalize to average of first 5 movements
feature_matrix = utils.norm_perc(feature_matrix)

# Compute significance for first/last half of stimulation/recovery
fig = plt.figure(figsize=(5.6, 5.6))
color_slow = "#00863b"
color_fast = "#3b0086"
bar_pos = [1, 2]
sides = [0, 1]
for i in range(1, 3):

    feature_matrix_mean = np.zeros((n_datasets, 2))
    # Loop over every patient
    for d in range(n_datasets):
        for cond in range(2):
            f = feature_matrix[d, cond, int(91*(i-1)):int(91*i)]
            t = trial_side[d, cond, int(91*(i-1)):int(91*i)]
            feature_matrix_mean[d, cond] = np.nanmean(f[np.where(t==sides[cond])])

    # Median over all movements in that period
    #feature_matrix_mean = np.nanmean(feature_matrix[:, :, int(91*(i-1)):int(91*i)], axis=2)

    # Plot the mean bar
    if i == 1:
        plt.bar(bar_pos[i-1]-0.25, np.mean(feature_matrix_mean[:, 0]), color=color_slow, label="Slow", width=0.5, alpha=0.5)
        plt.bar(bar_pos[i-1]+0.25, np.mean(feature_matrix_mean[:, 1]), color=color_fast, label="Fast", width=0.5, alpha=0.5)
    else:
        plt.bar(bar_pos[i - 1] - 0.25, np.mean(feature_matrix_mean[:, 0]), color=color_slow, width=0.5, alpha=0.5)
        plt.bar(bar_pos[i - 1] + 0.25, np.mean(feature_matrix_mean[:, 1]), color=color_fast, width=0.5, alpha=0.5)

    # Plot the individual points
    for dat in feature_matrix_mean:
        plt.plot(bar_pos[i-1]-0.25, dat[0], marker='o', markersize=3, color=color_slow)
        plt.plot(bar_pos[i-1] + 0.25, dat[1], marker='o', markersize=3, color=color_fast)
        # Add line connecting the points
        plt.plot([bar_pos[i-1]-0.25, bar_pos[i-1]+0.25], dat, color="black", linewidth=0.7, alpha=0.5)

    # Add statistics
    z, p = scipy.stats.wilcoxon(x=feature_matrix_mean[:, 0], y=feature_matrix_mean[:, 1])
    sig = "bold" if p < 0.05 else "regular"
    plt.text(bar_pos[i-1]-0.25, np.max(feature_matrix_mean)+5, f"p = {np.round(p, 3)}", weight=sig, fontsize=18)
    plt.yticks(fontsize=16)

# Adjust plot
plt.xticks(bar_pos, ["Stimulation", "Recovery"], fontsize=20)
feature_name_space = feature_name.replace("_", " ")
plt.ylabel(f"Change in {feature_name_space} [%]", fontsize=20)
#plt.ylabel(f"Change in peak deceleration [%]", fontsize=14)
plt.subplots_adjust(bottom=0.2, left=0.17)
plt.legend(loc="best",  prop={'size': 16})
#utils.adjust_plot(fig)
utils.despine()
axes = plt.gca()
axes.spines[['right', 'top']].set_visible(False)

# Save figure on group basis
#plt.savefig(f"../../Plots/stats_{feature_name}_{med}_poster.svg", format="svg", bbox_inches="tight", transparent=True)

plt.show()