# Script for plotting and analysis of peak speeds

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

# Select peak speeds of interest
peak_speed = peak_speed[datasets, :, :, :]
n_trials = peak_speed.shape[3]

# Detect and fill outliers (e.g. when subject did not touch the screen)
np.apply_along_axis(lambda m: utils.fill_outliers(m), axis=3, arr=peak_speed)

# Normalize to the start of each stimulation block (mean peak speed of movement 5-10)
peak_speed = utils.norm_perc(peak_speed)

# Smooth over 5 consecutive movements for plotting
peak_speed_smooth = utils.smooth_moving_average(peak_speed, window_size=5, axis=3)

# Average over all datasets
median_peak_speed = np.median(peak_speed_smooth, axis=0)

# Compute standard deviation over all datasets
std_peak_speed = np.std(peak_speed_smooth, axis=0)

# Plot feature over time
plt.figure(figsize=(18, 5))
plt.subplot(1,2,1)
utils.plot_conds(median_peak_speed, std_peak_speed)
plt.xlabel("Movements", fontsize=14)
plt.ylabel(f"$\Delta$ peak speed in %", fontsize=14)

# Compute significance in 4 bins
feature_bin = np.dstack((np.median(peak_speed[:,:,:,:int(n_trials/2)], axis=3),
              np.median(peak_speed[:,:,:,int(n_trials/2):], axis=3)))[:,:,[0,2,1,3]]
t_bin, p_bin = stats.ttest_rel(feature_bin[:,0,:], feature_bin[:,1,:], axis=0)

# Plot mean feature change and significance for 4 bins
plt.subplot(1, 2, 2)
x_names = ['First half stim', 'Second half stim', 'First half recov', 'Second half recov']
hue_names = ['Slow', 'Fast']
feature_bin = np.transpose(feature_bin, (2, 0, 1))
dim1, dim2, dim3 = np.meshgrid(x_names, np.arange(feature_bin.shape[1]), hue_names, indexing='ij')
ax = sb.barplot(x=dim1.ravel(), y=feature_bin.ravel(), hue=dim3.ravel(), palette=["blue", "red"], estimator=np.median)
sb.stripplot(x=dim1.ravel(), y=feature_bin.ravel(), hue=dim3.ravel(), dodge=True, ax=ax, palette=["blue", "red"])

# Add statistics
add_stat_annotation(ax, x=dim1.ravel(), y=feature_bin.ravel(), hue=dim3.ravel(),
                    box_pairs=[(("First half stim", "Fast"), ("First half stim", "Slow")),
                                 (("Second half stim", "Fast"), ("Second half stim", "Slow")),
                                 (("First half recov", "Fast"), ("First half recov", "Slow")),
                                 (("Second half recov", "Fast"), ("Second half recov", "Slow"))
                                ],
                    test='Wilcoxon', text_format='simple', loc='inside', verbose=2, comparisons_correction=None)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)


# Save figure on group basis
plt.savefig(f"../../Plots/speed_group_{med}.png", format="png", bbox_inches="tight")

plt.show()