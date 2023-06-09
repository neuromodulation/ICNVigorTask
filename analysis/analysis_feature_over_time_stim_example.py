# Script for plotting of features over time with stimulated trials marked

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
dataset = 6

# Load feature matrix
feature_matrix = np.load(f"../../Data/{feature_name}.npy")
stim_time = np.load(f"../../Data/stim_time.npy")
stim = stim_time.copy()
stim[np.isnan(stim)] = 0
stim[np.nonzero(stim)] = 1
stim = stim.astype(int)

# Select datasets of interest
feature_matrix = feature_matrix[dataset, :, :, :]
stim = stim[dataset, :, :, :]

n_trials = feature_matrix.shape[-1]

# Detect and fill outliers (e.g. when subject did not touch the screen)
np.apply_along_axis(lambda m: utils.fill_outliers_mean(m, threshold=3), axis=2, arr=feature_matrix)

# Reshape matrix such that blocks from one condition are concatenated
feature_matrix = np.reshape(feature_matrix, (2, n_trials*2))
stim = np.reshape(stim, (2, n_trials*2))

# Delete the first 5 movements
feature_matrix = feature_matrix[:, 5:]
stim = stim[:, 5:]

# Normalize to average of first 5 movements
feature_matrix = utils.norm_perc(feature_matrix)

# Smooth over 5 consecutive movements for plotting
feature_matrix = utils.smooth_moving_average(feature_matrix, window_size=5, axis=1)

# Plot feature over time
plt.figure(figsize=(9, 5))
plt.subplot(1, 2, 1)
plt.plot(feature_matrix[1,:], color="black")
plt.xlabel("Movement number", fontsize=20)
plt.ylabel(f"Change in peak speed [%]", fontsize=20)
#plt.title(f"Fast")
plt.yticks([])
plt.xticks(fontsize=16)
plt.axvline(91, color="black")
utils.despine()
for i, s in enumerate(stim[1, :]):
    if s == 1:
        plt.axvline(i, color="#E25558", alpha=0.4)

plt.subplot(1, 2, 2)
plt.plot(feature_matrix[0,:], color="black")
plt.xlabel("Movement number", fontsize=20)
plt.yticks([])
plt.xticks(fontsize=16)
#plt.ylabel(f"Change in peak speed [%]", fontsize=14)
#plt.title(f"Slow")
plt.axvline(91, color="black")
utils.despine()
for i, s in enumerate(stim[0, :]):
    if s == 1:
        plt.axvline(i, color="#E25558", alpha=0.4)

plt.subplots_adjust(bottom=0.2, wspace=0.2)

plt.savefig(f"../../Plots/trace_example.svg", format="svg", bbox_inches="tight", transparent=True)

plt.show()