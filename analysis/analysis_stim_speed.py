# Plot speed of stimulated movements over time

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
plot_individual = False
med = "on"  # "on", "off", "all"
if all:
    datasets = np.range(26)
elif med == "off":
    datasets = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20]
else:
    datasets = [3, 4, 5, 7, 9, 10, 12, 18, 21, 22, 23, 24, 25]

# Load peak speed matrix
peak_speed = np.load(f"../../Data/peak_speed.npy")
peak_speed = peak_speed[datasets, :, :, :]

# Detect and fill outliers (e.g. when subject did not touch the screen)
np.apply_along_axis(lambda m: utils.fill_outliers(m), axis=3, arr=peak_speed)

# Normalize to the start of each stimulation block
peak_speed = utils.norm_perc(peak_speed)

# Load stim time matrix
stim_time = np.load(f"../../Data/stim_time.npy")
stim_time = stim_time[datasets, :, :, :]

# Get index of not stimulated movements
idx_nan = np.where(np.isnan(stim_time))

# Set peak speeds of non stimulated movements to nan
peak_speed_stim = peak_speed.copy()
peak_speed_stim[idx_nan] = None
peak_speed = peak_speed[:, :, 0, :]
peak_speed_stim = peak_speed_stim[:, :, 0, :]

# Calculate average speed of stimulated movements in bins
bins = 12
peak_speed_bin = np.array([np.nanmean(arr, axis=2) for arr in np.array_split(peak_speed, bins, axis=2)])
peak_speed_stim_bin = np.array([np.nanmean(arr, axis=2) for arr in np.array_split(peak_speed_stim, bins, axis=2)])
#peak_speed_stim_bin = np.array([np.nanvar(arr, axis=2) for arr in np.array_split(peak_speed_stim, bins, axis=2)])

# Compute mean over datasets
peak_speed_mean = np.nanmean(peak_speed_bin, axis=0)
peak_speed_std = np.nanstd(peak_speed_bin, axis=0)
peak_speed_stim_mean = np.nanmean(peak_speed_stim_bin, axis=0)
peak_speed_stim_std = np.nanstd(peak_speed_stim_bin, axis=0)
cond_names = ["Slow", "Fast"]
colors = ["blue", "red"]
plt.figure()
for cond in range(2):
    # Plot average speed
    x = np.arange(len(peak_speed_mean))
    plt.plot(peak_speed_mean[:,cond].ravel(), label=cond_names[cond]+" All move", color=colors[cond])
    # Plot std
    plt.fill_between(x, peak_speed_mean[:,cond].ravel() - peak_speed_std[:,cond].ravel(),
                     peak_speed_mean[:,cond].ravel() + peak_speed_std[:,cond].ravel()
                     , alpha=0.5, color=colors[cond])
    plt.plot(peak_speed_stim_mean[:, cond].ravel(), label=cond_names[cond]+" Stim only", color="dark"+colors[cond])
    # Plot std
    plt.fill_between(x, peak_speed_stim_mean[:, cond].ravel() - peak_speed_stim_std[:, cond].ravel(),
                     peak_speed_stim_mean[:, cond].ravel() + peak_speed_stim_std[:, cond].ravel()
                     , alpha=0.5, color="dark"+colors[cond])

plt.legend()
plt.ylabel(f"$\Delta$ peak speed in % (averaged in bin)", fontsize=12)
plt.xlabel("Bin number", fontsize=12)
plt.savefig(f"../../Plots/peak_speed_stim_only_{med}.png", format="png", bbox_inches="tight")

plt.show()