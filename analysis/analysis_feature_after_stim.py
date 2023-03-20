# Plot feature 3 moves after a stimulated movement
# As cmparison use slow/fast movements from the recovery block

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
import scipy.stats
matplotlib.use('TkAgg')
import warnings
warnings.filterwarnings("ignore")

# Set analysis parameters
feature_name = "peak_speed"
plot_individual = False
med = "off"
if med == "all":
    datasets = np.arange(27)
elif med == "off":
    datasets = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20, 26]
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

# Load matrix specifying slow/fast movements
slow = np.load(f"../../Data/slow.npy")
slow = slow[datasets, :, :, :]
fast = np.load(f"../../Data/fast.npy")
fast = fast[datasets, :, :, :]

# Reshape matrix such that blocks from one condition are concatenated
feature_matrix = np.reshape(feature_matrix, (n_datasets, 2, n_trials*2))
stim = np.reshape(stim, (n_datasets, 2, n_trials*2))
slow = np.reshape(slow, (n_datasets, 2, n_trials*2))
fast = np.reshape(fast, (n_datasets, 2, n_trials*2))

# Delete the first 5 movements
feature_matrix = feature_matrix[:, :, 5:]
stim = stim[:, :, 5:]
slow = slow[:, :, 5:]
fast = fast[:, :, 5:]

# Loop over conditions
subsequent_moves = np.zeros((4, n_datasets, 4))
count = 0
for cond in range(2):
    for is_stim in range(2):
        for dataset in range(n_datasets):
            if is_stim == 1:
                # Get index of stimulated movements
                stim_idx = np.where(stim[dataset, cond, :] == 1)[0]
                stim_idx = stim_idx[stim_idx < 93]
            else:
                # Extract fast/slow movements from recovery block
                if cond == 0:
                    stim_idx = np.where(slow[dataset, cond, :] == 1)[0]
                else:
                    stim_idx = np.where(fast[dataset, cond, :] == 1)[0]
                stim_idx = stim_idx[(stim_idx > 93) & (stim_idx < 183)]
                #stim_idx = stim_idx[stim_idx < 93]

            # Extract feature of three consecutive movement
            subsequent_moves_dataset = []
            for idx in stim_idx:
                # Calculate percentage change from stimulated movement
                diff_perc = ((feature_matrix[dataset, cond, idx:idx + 4] - feature_matrix[dataset, cond, idx]) /
                             feature_matrix[dataset, cond, idx]) * 100
                subsequent_moves_dataset.append(diff_perc)
            # Save
            subsequent_moves[count, dataset,:] = np.nanmedian(np.array(subsequent_moves_dataset), axis=0)
        count += 1
#
# Plot
ax = plt.figure(figsize=(10, 5))
x_names = ['0', '1', '2', '3']
hue_names = ['Slow Recovery', 'Slow Stim', 'Fast Recovery', 'Fast Stim']
subsequent_moves = np.transpose(subsequent_moves, (2, 1, 0))
dim1, dim2, dim3 = np.meshgrid(x_names, np.arange(subsequent_moves.shape[1]), hue_names, indexing='ij')
ax = sb.barplot(x=dim1.ravel(), y=subsequent_moves.ravel(), hue=dim3.ravel(), palette=["#80c39d", "#00863b", "#9c80c2", "#3b0086"], estimator=np.median)
sb.stripplot(x=dim1.ravel(), y=subsequent_moves.ravel(), hue=dim3.ravel(), dodge=True, ax=ax, palette=["#80c39d", "#00863b", "#9c80c2", "#3b0086"])

# Add statistics
add_stat_annotation(ax, x=dim1.ravel(), y=subsequent_moves.ravel(), hue=dim3.ravel(),
                    box_pairs=[(("1", "Fast Stim"), ("1", "Fast Recovery")),
                                 (("2", "Fast Stim"), ("2", "Fast Recovery")),
                                 (("3", "Fast Stim"), ("3", "Fast Recovery")),
                               (("1", "Slow Stim"), ("1", "Slow Recovery")),
                               (("2", "Slow Stim"), ("2", "Slow Recovery")),
                               (("3", "Slow Stim"), ("3", "Slow Recovery")),
                                ],
                    test='Wilcoxon', text_format='simple', loc='inside', verbose=2, comparisons_correction=None)

# Get the handles and labels. For this example it'll be 2 tuples
# of length 4 each.
handles, labels = ax.get_legend_handles_labels()

# When creating the legend, only use the first two elements
# to effectively remove the last two.
l = plt.legend(handles[4:8], labels[4:8], bbox_to_anchor=(0.05, 0.7), loc=2, borderaxespad=0.)

# Add labels
plt.xlabel("Number of movement after stimulation", fontsize=14)
feature_name_space = feature_name.replace("_", " ")
plt.ylabel(f"Change in {feature_name_space} [%]", fontsize=14)
plt.show()

plt.savefig(f"../../Plots/{feature_name}_after_stim_{med}.png", format="png", bbox_inches="tight")


""" subsequent_moves_mean = np.nanmean(np.array(subsequent_moves), axis=0)
        subsequent_moves_std = np.nanstd(np.array(subsequent_moves), axis=0)
        # Plot as bars
        plt.plot(subsequent_moves_mean, color=colors[cond][is_stim], label=cond_names[cond][is_stim], linewidth=3)
        # Plot variance
        plt.fill_between(np.arange(4), subsequent_moves_mean - subsequent_moves_std, subsequent_moves_mean + subsequent_moves_std, color=colors[cond][is_stim], alpha=0.2)"""