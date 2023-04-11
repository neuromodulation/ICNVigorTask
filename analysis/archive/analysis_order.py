# Script for order analysis

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
datasets = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20]

# Load peak speed matrix
peak_speed = np.load(f"../../Data/peak_speed.npy")
peak_speed = peak_speed[datasets,:,:,:]
n_trials = peak_speed.shape[3]

# Load orderition order
slow_first = np.load(f"../../Data/slow_first.npy")
slow_first = slow_first[datasets]

# Detect and fill outliers (e.g. when subject did not touch the screen)
np.apply_along_axis(lambda m: utils.fill_outliers(m), axis=3, arr=peak_speed)

# Normalize to the start of each stimulation block
peak_speed = utils.norm_perc(peak_speed)

# Smooth over 5 consecutive movements
peak_speed_smooth = utils.smooth_moving_average(peak_speed, window_size=5, axis=3)

# Plot for each order
plt.figure(figsize=(18, 8))
order_names = ["Fast-Slow", "Slow-Fast"]
for order in range(2):

    idx_order = slow_first == order

    peak_speed_order = peak_speed[idx_order,:,:,:]
    peak_speed_smooth_order = peak_speed_smooth[idx_order, :, :, :]

    # Average over all datasets
    median_peak_speed = np.median(peak_speed_smooth_order, axis=0)

    # Compute standard deviation over all datasets
    std_peak_speed = np.std(peak_speed_smooth_order, axis=0)

    # Plot feature over time
    plt.subplot(2, 2, order + 1)
    utils.plot_conds(median_peak_speed, std_peak_speed)
    plt.xlabel("Movements", fontsize=14)
    plt.ylabel(f"$\Delta$ peak speed in %", fontsize=14)
    plt.ylim([-40, 40])
    plt.title(order_names[order])

    # Compute significance in 4 bins
    feature_bin = np.dstack((np.median(peak_speed_order[:,:,:,:int(n_trials/2)], axis=3),
                  np.median(peak_speed_order[:,:,:,int(n_trials/2):], axis=3)))[:,:,[0,2,1,3]]
    #feature_bin = np.dstack((np.median(peak_speed[:,:,:,:], axis=3),
    #              np.median(peak_speed[:,:,:,:], axis=3)))[:,:,[0,2,1,3]]
    t_bin, p_bin = stats.ttest_rel(feature_bin[:,0,:], feature_bin[:,1,:], axis=0)

    # Plot mean feature change and significance for 4 bins
    plt.subplot(2, 2, order + 3)
    x_names = ['First half stim', 'Second half stim', 'First half recov', 'Second half recov']
    hue_names = ['Slow', 'Fast']
    feature_bin = np.transpose(feature_bin, (2, 0, 1))
    dim1, dim2, dim3 = np.meshgrid(x_names, np.arange(feature_bin.shape[1]), hue_names, indexing='ij')
    ax = sb.barplot(x=dim1.ravel(), y=feature_bin.ravel(), hue=dim3.ravel(), palette=["blue", "red"],
                    estimator=np.median)
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
plt.savefig(f"../../Plots/speed_order.png", format="png", bbox_inches="tight")

plt.show()