# Script for plotting and analysis of peak speeds

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

#bids_root = "C:\\Users\\ICN\\Documents\\VigorStim\\Data\\rawdata\\"
bids_root = "C:\\Users\\alessia\\Documents\\Jobs\\ICN\\vigor-stim\Data\\rawdata\\"

# Set analysis parameters
plot_individual = True
datasets = [1,2,3,4,5,6,7,8,9]

# Load peak speed matrix
peak_speed = np.load(f"../../../Data/peak_speed.npy")
n_trials = peak_speed.shape[3]

# Detect and fill outliers (e.g. when subject did not touch the screen)
np.apply_along_axis(lambda m: utils.fill_outliers(m), axis=3, arr=peak_speed)
np.apply_along_axis(lambda m: utils.fill_outliers(m), axis=3, arr=peak_speed)

# Normalize to the start and smooth over 5 consecutive movements
peak_speed = utils.smooth_moving_average(utils.norm_perc(peak_speed), window_size=5)

# Average over all datasets
median_peak_speed = np.median(peak_speed, axis=0)
# Compute standard deviation over all datasets
std_peak_speed = np.std(peak_speed, axis=0)

# Plot feature over time
plt.figure(figsize=(15, 5))
plt.subplot(1,2,1)
utils.plot_conds(median_peak_speed, std_peak_speed)
plt.xlabel("Movements", fontsize=14)
plt.ylabel(f"$\Delta$ peak speed in %", fontsize=14)

# Compute significance in 4 bins
feature_bin = np.dstack((np.mean(peak_speed[:,:,:,:int(n_trials/2)], axis=3),
              np.mean(peak_speed[:,:,:,int(n_trials/2):], axis=3)))[:,:,[0,2,1,3]]
t_bin, p_bin = stats.ttest_rel(feature_bin[:,0,:], feature_bin[:,1,:], axis=0)

# Plot mean feature change and significance for 4 bins
plt.subplot(1, 2, 2)
x_names = ['1-50', '50-100', '100-150', '150-200']
hue_names = ['Slow', 'Fast']
feature_bin = np.transpose(feature_bin, (2, 0, 1))
dim1, dim2, dim3 = np.meshgrid(x_names, np.arange(feature_bin.shape[1]), hue_names, indexing='ij')
ax = sb.barplot(x=dim1.ravel(), y=feature_bin.ravel(), hue=dim3.ravel(), palette=["blue", "red"], estimator=np.median)
sb.stripplot(x=dim1.ravel(), y=feature_bin.ravel(), hue=dim3.ravel(), dodge=True, ax=ax, palette=["blue", "red"])

# Add statistics
add_stat_annotation(ax, x=dim1.ravel(), y=feature_bin.ravel(), hue=dim3.ravel(),
                    box_pairs=[(("1-50", "Fast"), ("1-50", "Slow")),
                                 (("50-100", "Fast"), ("50-100", "Slow")),
                                 (("100-150", "Fast"), ("100-150", "Slow")),
                                 (("150-200", "Fast"), ("150-200", "Slow"))
                                ],
                    test='t-test_paired', text_format='simple', loc='inside', verbose=2, comparisons_correction=None)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

# Save figure on group basis
plt.savefig(f"../../../Plots/speed_group.png", format="png", bbox_inches="tight")

plt.show()