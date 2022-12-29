# Script for plotting and analysis of peak speeds individually

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
matplotlib.use('TkAgg')
import warnings
warnings.filterwarnings("ignore")

# Set analysis parameters
# Define which datasets to include based on Dataset_list.csv
# Only OFF (one for each subject)
datasets = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20]

# Load peak speed matrix
peak_speed = np.load(f"../../../Data/peak_speed.npy")

# Select peak speeds of interest
peak_speed = peak_speed[datasets, :, :, :]
n_trials = peak_speed.shape[3]

# Detect and fill outliers (e.g. when subject did not touch the screen)
np.apply_along_axis(lambda m: utils.fill_outliers(m), axis=3, arr=peak_speed)

# Normalize to the start of each stimulation block (mean peak speed of movement 5-10)
peak_speed = utils.norm_perc(peak_speed)

# Smooth over 5 consecutive movements for plotting
peak_speed_smooth = utils.smooth_moving_average(peak_speed, window_size=5, axis=3)

# Plot individual dataset and perform significance test
for i, (peak_speed_ind, peak_speed_smooth_ind) in enumerate(zip(peak_speed, peak_speed_smooth)):

    # Plot smoothed peak speeds
    plt.figure(figsize=(18, 5))
    plt.subplot(1, 2, 1)
    utils.plot_conds(peak_speed_smooth_ind)
    plt.xlabel("Movements")
    plt.ylabel(f"$\Delta$ peak speed in %")

    # Compute significance in 4 bins
    feature_bin = np.hstack((peak_speed_ind[:, :, :int(n_trials / 2)],
                             peak_speed_ind[:, :, int(n_trials / 2):]))[:, [0, 2, 1, 3], :]

    # Plot significance for 4 bins
    plt.subplot(1, 2, 2)
    x_names = ['First half stim', 'Second half stim', 'First half recov', 'Second half recov']
    hue_names = ['Slow', 'Fast']
    feature_bin = np.transpose(feature_bin, (1, 2, 0))
    dim1, dim2, dim3 = np.meshgrid(x_names, np.arange(feature_bin.shape[1]), hue_names, indexing='ij')
    ax = sb.barplot(x=dim1.ravel(), y=feature_bin.ravel(), hue=dim3.ravel(), palette=["blue", "red"],
                    estimator=np.median)
    sb.stripplot(x=dim1.ravel(), y=feature_bin.ravel(), hue=dim3.ravel(), dodge=True, ax=ax,
                 palette=["blue", "red"])

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

    # Set title
    plt.suptitle(f"Dataset Nr. {datasets[i]+1}")

    # Save figure
    plt.savefig(f"../../../Plots/speed_dataset_{datasets[i]+1}.png", format="png", bbox_inches="tight")

plt.show()