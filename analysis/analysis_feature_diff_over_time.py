# Script for plotting of features over time

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
med = "off"  # "on", "off", "all"
if med == "all":
    datasets = np.arange(30)
elif med == "off":
    datasets = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20, 26, 27, 28]
else:
    datasets = [3, 4, 5, 7, 9, 10, 12, 18, 21, 22, 23, 24, 25, 29]

# Load feature matrix
feature_matrix = np.load(f"../../Data/{feature_name}.npy")

# Select datasets of interest
feature_matrix = feature_matrix[datasets, :, :, :]
n_datasets, _,_, n_trials = feature_matrix.shape

# Detect and fill outliers (e.g. when subject did not touch the screen)
np.apply_along_axis(lambda m: utils.fill_outliers_nan(m, threshold=3), axis=3, arr=feature_matrix)

# Reshape matrix such that blocks from one condition are concatenated
feature_matrix = np.reshape(feature_matrix, (n_datasets, 2, n_trials*2))

# Delete the first 5 movements
feature_matrix = feature_matrix[:, :, 5:]

# Normalize to average of first 5 movements
feature_matrix = utils.norm_perc(feature_matrix)
#feature_matrix = utils.norm_perc_every_t_trials(feature_matrix, 45)

# Smooth over 5 consecutive movements for plotting
feature_matrix = utils.smooth_moving_average(feature_matrix, window_size=5, axis=2)

# Substract the conditions
feature_matrix = feature_matrix[:, 1, :] - feature_matrix[:, 0, :]

# Average over all datasets
feature_matrix_mean = np.nanmedian(feature_matrix, axis=0)
feature_matrix_std = np.nanstd(feature_matrix, axis=0)

# Plot feature over time
fig = plt.figure()
plt.plot(feature_matrix_mean)
plt.xlabel("Movement number", fontsize=14)
feature_name_space = feature_name.replace("_", " ")
plt.ylabel(f"Change in {feature_name_space} [%]", fontsize=14)

# Add line to mark end of stimulation
n_trials = feature_matrix.shape[-1]
plt.axvline(n_trials/2, color="black", linewidth=1)
axes = plt.gca()
ymin, ymax = axes.get_ylim()
axes.spines[['right', 'top']].set_visible(False)
plt.text(25, ymax+2, "Stimulation", rotation=0, fontsize=12)
plt.text(118, ymax+2, "Recovery", rotation=0, fontsize=12)

# Adjust plot
plt.xlim([0, n_trials-1])
plt.subplots_adjust(bottom=0.2, left=0.15)
utils.adjust_plot(fig)
plt.legend()

# Save figure on group basis
plt.savefig(f"../../Plots/{feature_name}_{med}.svg", format="svg", bbox_inches="tight")

plt.show()