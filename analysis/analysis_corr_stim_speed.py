# Script for analysing number of initial movements
# Correlation between number of stimulated movements and other feature

import numpy as np
import matplotlib.pyplot as plt
import mne
import gc
import ICNVigorTask.utils.utils as utils
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
datasets = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20]

# Load peak speed matrix
peak_speed = np.load(f"../../../Data/peak_speed.npy")
peak_speed = peak_speed[datasets, :, :, :]

# Detect and fill outliers (e.g. when subject did not touch the screen)
np.apply_along_axis(lambda m: utils.fill_outliers(m), axis=3, arr=peak_speed)

# Normalize to the start of each stimulation block
peak_speed = utils.norm_perc(peak_speed)

# Smooth over 5 consecutive movements
#peak_speed = utils.smooth_moving_average(peak_speed, window_size=5, axis=3)

# Load stim time matrix
stim_time = np.load(f"../../../Data/stim_time.npy")
stim_time = stim_time[datasets,:,:,:]

# Extract whether a trial was stimulated or not
stim = stim_time.copy()
stim[np.isnan(stim)] = 0
stim[np.nonzero(stim)] = 1

# Bin number of stimulated movements
bins = 15
n_stim = np.array([np.mean(arr, axis=3) for arr in np.array_split(stim, bins, axis=3)])
peak_speed_bin = np.array([np.median(arr, axis=3) for arr in np.array_split(peak_speed, bins, axis=3)])

# Plot as scatter plot and compute correlation for each condition
cond_names = ["Slow", "Fast"]
plt.figure(figsize=(12, 4))
for cond in range(2):
    plt.subplot(1, 2, cond+1)
    corr, p = spearmanr(peak_speed_bin[:, :, cond, 0].ravel(), n_stim[:, :, cond, 0].ravel())
    sb.regplot(peak_speed_bin[:, :, cond, 0].ravel(), n_stim[:, :, cond, 0].ravel())
    plt.title(f"{cond_names[cond]} stim, corr = {np.round(corr,2)}, p = {np.round(p,3)}", fontweight='bold')
    plt.xlabel(f"$\Delta$ speed in %", fontsize=14)
    plt.ylabel(f"% of stimulated movements", fontsize=14)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.subplots_adjust(bottom=0.15, hspace=0.2)

plt.show()