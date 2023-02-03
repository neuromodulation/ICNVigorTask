# Plot feature 3 moves after a stimulated movement

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
feature_name = "peak_speed"
plot_individual = False
med = "off"
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

# Extract whether a trial was stimulated or not
stim = stim_time.copy()
stim[np.isnan(stim)] = 0
stim[np.nonzero(stim)] = 1

# Reshape matrix such that blocks from one condition are concatenated
feature_matrix = np.reshape(feature_matrix, (n_datasets, 2, n_trials*2))
stim = np.reshape(stim, (n_datasets, 2, n_trials*2))

# Delete the first 3 movements
feature_matrix = feature_matrix[:, :, 5:]
stim = stim[:, :, 5:]

# Loop over conditions
colors = ["#00863b",  "#3b0086"]
cond_names = ["Slow", "Fast"]
fig = plt.figure()
for cond in range(2):
    subsequent_moves = []
    for dataset in range(n_datasets):
        # Get index of stimulated movements
        stim_idx = np.where(stim[dataset, cond, :] == 1)[0]
        stim_idx = stim_idx[stim_idx < 93]
        # Extract feature of three consecutive movement
        subsequent_moves_dataset = []
        for idx in stim_idx:
            # Calculate percentage change from stimulated movement
            diff_perc = ((feature_matrix[dataset, cond, idx:idx + 4] - feature_matrix[dataset, cond, idx]) /
                         feature_matrix[dataset, cond, idx]) * 100
            subsequent_moves_dataset.append(diff_perc)
        subsequent_moves.append(np.nanmedian(np.array(subsequent_moves_dataset), axis=0))
    # Average over movements and datasets
    subsequent_moves_mean = np.nanmean(np.array(subsequent_moves), axis=0)
    subsequent_moves_std = np.nanstd(np.array(subsequent_moves), axis=0)
    # Plot as bars
    plt.plot(subsequent_moves_mean, color=colors[cond], label=cond_names[cond], linewidth=3)
    # Plot variance
    plt.fill_between(np.arange(4), subsequent_moves_mean - subsequent_moves_std, subsequent_moves_mean + subsequent_moves_std, color=colors[cond], alpha=0.2)

plt.axhline(0, color="grey", linewidth=1)
feature_name_space = feature_name.replace("_", " ")
plt.ylabel(f"Change in {feature_name_space} [%]", fontsize=14)
plt.xlabel("Move after stim", fontsize=14)
plt.xticks([1, 2, 3], ["1", "2", "3"])
plt.subplots_adjust(left=0.2, bottom=0.2)
utils.adjust_plot(fig)
plt.legend()

plt.savefig(f"../../Plots/{feature_name}_after_stim_{med}.png", format="png", bbox_inches="tight")

plt.show()