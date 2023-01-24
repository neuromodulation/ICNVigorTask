# Analysis of tiem of stimulation

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
from scipy.io import loadmat
import os
matplotlib.use('TkAgg')
import warnings
warnings.filterwarnings("ignore")

# Set analysis parameters
plot_individual = False
datasets = np.arange(26)#[0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20]

# Load time of onset, offset and peak, stim
move_onset_time = np.load(f"../../Data/move_onset_time.npy")
move_onset_time = move_onset_time[datasets, :, :, :]
move_offset_time = np.load(f"../../Data/move_offset_time.npy")
move_offset_time = move_offset_time[datasets, :, :, :]
peak_speed_time = np.load(f"../../Data/peak_speed_time.npy")
peak_speed_time = peak_speed_time[datasets, :, :, :]
stim_time = np.load(f"../../Data/stim_time.npy")
stim_time = stim_time[datasets, :, :, :]

# Compute relative time of stim in movement
rel_stim_time = (stim_time - move_onset_time) / (move_offset_time - move_onset_time)
# Set outliers to None
rel_stim_time[rel_stim_time < 0] = None
rel_stim_time[rel_stim_time > 1] = None
# Transform into %
rel_stim_time *= 100

# Plot relative stim for inspection divided by stimulation condition
plt.figure()
plt.hist(rel_stim_time[:, 0, :, :].ravel(), bins=20, label="Slow")
plt.hist(rel_stim_time[:, 1, :, :].ravel(), bins=20, label="Fast")
# Compute significance
t, p = stats.ttest_rel(rel_stim_time[:, 0, :, :].ravel(), rel_stim_time[:, 1, :, :].ravel(), nan_policy="omit")
plt.legend()
plt.xlabel("Relative time of stimulation during movement in %", fontsize=12)
plt.title(f"Paired t-test p={np.round(p, 4)}", fontsize=14)

# Save figure
plt.savefig(f"../../Plots/stim_time_conditions.png", format="png", bbox_inches="tight")

# Load peak speed matrix
peak_speed = np.load(f"../../Data/peak_speed.npy")
peak_speed = peak_speed[datasets, :, :, :]

# Detect and fill outliers (e.g. when subject did not touch the screen)
np.apply_along_axis(lambda m: utils.fill_outliers(m), axis=3, arr=peak_speed)

# Normalize to the start of each stimulation block
peak_speed = utils.norm_perc(peak_speed)

# Compute correlation between relative time of stim and peak speed of next movement
cond_names = ["Slow", "Fast"]
plt.figure(figsize=(15, 5))
for cond in range(2):
    plt.subplot(1, 2, cond+1)
    rel_stim_time_cond = rel_stim_time[:, cond, :, :]
    peak_speed_cond = peak_speed[:, cond, :, :]
    # Get the stim time without nan
    idx_stim = np.where(~np.isnan(rel_stim_time_cond))
    # Get the peak of the subsequent movement
    idx_stim = list(idx_stim)
    idx_stim[2] = idx_stim[2] + 1
    # Filter out indices than are larger than the array
    delete_idx = np.where(idx_stim[2] > 95)
    idx_stim = [np.delete(tmp, delete_idx) for tmp in idx_stim]
    # Index
    peak_speed_cond = peak_speed_cond[tuple(idx_stim)]
    # Substract one to get stim time of previous movement
    idx_stim[2] = idx_stim[2] - 1
    rel_stim_time_cond = rel_stim_time_cond[tuple(idx_stim)]
    # Correlate
    corr, p = spearmanr(rel_stim_time_cond.ravel(), peak_speed_cond.ravel())
    sb.regplot(x=rel_stim_time_cond.ravel(), y=peak_speed_cond.ravel())
    plt.title(f"{cond_names[cond]} stim, corr = {np.round(corr, 2)}, p = {np.round(p, 3)}", fontweight='bold')
    plt.ylabel(f"$\Delta$ peak speed of subsequent move in %", fontsize=14)
    plt.xlabel(f"Relative time of stimulation during movement in %", fontsize=14)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.subplots_adjust(bottom=0.15, hspace=0.2)

plt.savefig(f"../../Plots/corr_stim_next_speed.png", format="png", bbox_inches="tight")

plt.show()
