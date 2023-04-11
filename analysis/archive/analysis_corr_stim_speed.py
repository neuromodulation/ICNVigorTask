# Correlation between number of stimulated movements and peak speed

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
feature_name = "move_dur"
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
feature_matrix = feature_matrix[:, :, 3:]
stim = stim[:, :, 3:]

# Bin number of stimulated movements and feature matrix
bins = 21
n_stim = np.array([np.nanmean(arr, axis=2)*100 for arr in np.array_split(stim, bins, axis=2)])
feature_bin = np.array([np.nanmedian(arr, axis=2) for arr in np.array_split(feature_matrix, bins, axis=2)])

# Normalize to first bin and transform into percentage
feature_bin = ((feature_bin - feature_bin[0, :, :]) / feature_bin[0, :, :]) * 10

# Plot as scatter plot and compute correlation for each condition
cond_names = ["Slow", "Fast"]
plt.figure(figsize=(12, 5))
for cond in range(2):
    plt.subplot(1, 2, cond+1)
    corr, p = spearmanr(feature_bin[1:11, :, cond].ravel(), n_stim[:10, :, cond].ravel())
    sb.regplot(x=feature_bin[:10, :, cond].ravel(), y=n_stim[:10, :, cond].ravel())
    plt.title(f"{cond_names[cond]} stim, corr = {np.round(corr,2)}, p = {np.round(p,3)}", fontweight='bold')
    plt.xlabel(f"change in {feature_name}", fontsize=14)
    plt.ylabel(f"% of stimulated movements in bin", fontsize=14)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.subplots_adjust(bottom=0.15, hspace=0.2)

plt.savefig(f"../../Plots/corr_n_stim_{feature_name}_{med}.png", format="png", bbox_inches="tight")

plt.show()