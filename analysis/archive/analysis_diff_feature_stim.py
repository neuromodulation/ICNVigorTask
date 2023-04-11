# Analyse difference between feature at stimulation trial to previous and subsequent trial


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
n_datasets, _, _, n_trials = feature_matrix.shape

# Detect and fill outliers (e.g. when subject did not touch the screen)
np.apply_along_axis(lambda m: utils.fill_outliers_mean(m), axis=3, arr=feature_matrix)

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

# Delete the first 5 movements
feature_matrix = feature_matrix[:, :, 5:]
stim = stim[:, :, 5:]

# Loop over conditions
colors = ["#00863b",  "#3b0086"]
cond_names = ["Slow", "Fast"]
diff_prev_post_slow_all = []
diff_prev_post_fast_all = []
for dataset in range(n_datasets):
    if plot_individual:
        plt.figure(figsize=(15, 5))
    for cond in range(2):
        # Get index of stimulated movements
        stim_idx = np.where(stim[dataset, cond, :] == 1)[0]
        stim_idx = stim_idx[stim_idx < 93]
        # Extract feature of previous and subsequent moves
        diff_prev_post = []
        for idx in stim_idx:
            # Calculate percentage difference around stimulated movement
            diff_prev = ((feature_matrix[dataset, cond, idx - 1] - feature_matrix[dataset, cond, idx]) /
                         feature_matrix[dataset, cond, idx]) * 100
            diff_post = ((feature_matrix[dataset, cond, idx + 1] - feature_matrix[dataset, cond, idx]) /
                         feature_matrix[dataset, cond, idx]) * 100
            # Append
            diff_prev_post.append([diff_prev, diff_post])
        # Plot correlation individual
        if plot_individual:
            plt.subplot(1, 2, cond+1)
            diff_prev_post = np.array(diff_prev_post)
            corr, p = spearmanr(diff_prev_post[:, 0], diff_prev_post[:, 1])
            sb.regplot(x=diff_prev_post[:, 0], y=diff_prev_post[:, 1])
            plt.xlabel(f"% diff in {feature_name} prev", fontsize=12)
            plt.ylabel(f"% diff in {feature_name} post", fontsize=12)
            plt.title(f"{cond_names[cond]} stim, corr = {np.round(corr, 2)}, p = {np.round(p, 3)}", fontweight='bold')

        # Append for group level analysis
        if cond == 0:
            diff_prev_post_slow_all.extend(diff_prev_post)
        else:
            diff_prev_post_fast_all.extend(diff_prev_post)
    # Save figure
    if plot_individual:
        plt.suptitle(f"Dataset {dataset}")
        plt.savefig(f"../../Plots/{feature_name}_corr_prev_post_dataset_{dataset}_{med}.png", format="png", bbox_inches="tight")
        plt.show()


# Plot on group level
diff_prev_post_all = [diff_prev_post_slow_all,  diff_prev_post_fast_all]
fig = plt.figure(figsize=(7, 3.2))
for cond, diff_cond in enumerate(diff_prev_post_all):
    plt.subplot(1, 2, cond + 1)
    diff_prev_post = np.array(diff_cond)
    corr, p = spearmanr(diff_prev_post[:, 0], diff_prev_post[:, 1])
    sb.regplot(x=diff_prev_post[:, 0], y=diff_prev_post[:, 1], color=colors[cond],  scatter_kws={'alpha':0.5})
    feature_name_space = feature_name.replace("_", " ")
    plt.xlabel(f"Change in {feature_name_space}:\n Subsequent [%]", fontsize=12)
    if cond == 0:
        plt.ylabel(f"Change in {feature_name_space}: \n Previous [%]", fontsize=12)
    plt.title(f"{cond_names[cond]} (corr = {np.round(corr, 2)}, p < 0.001)", fontweight='regular', fontsize=12)
    axes = plt.gca()
    axes.spines[['right', 'top']].set_visible(False)
plt.subplots_adjust(wspace=0.2, bottom=0.25)

# Save plot
plt.savefig(f"../../Plots/{feature_name}_corr_prev_post_all_{med}.svg", format="svg", bbox_inches="tight")

plt.show()