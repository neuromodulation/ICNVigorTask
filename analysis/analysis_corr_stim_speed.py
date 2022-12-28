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
peak_speed = peak_speed[datasets,:,:,:]

# Detect and fill outliers (e.g. when subject did not touch the screen)
np.apply_along_axis(lambda m: utils.fill_outliers(m), axis=3, arr=peak_speed)

# Normalize to the start of each stimulation block
peak_speed = utils.norm_perc(peak_speed)

# Smooth over 5 consecutive movements
peak_speed = utils.smooth_moving_average(peak_speed, window_size=5, axis=3)

# Load stim time matrix
stim_time = np.load(f"../../../Data/stim_time.npy")
stim_time = stim_time[datasets,:,:,:]

# Extract whether a trial was stimulated or not
stim = stim_time.copy()
stim[np.isnan(stim)] = 0
stim[not np.nonzero(stim)] = 1

# 
bins = 10
slow = [np.sum(arr) for arr in np.array_split(stim[0, :], bins)]
fast = [np.sum(arr) for arr in np.array_split(stim[1, :], bins)]

n_stim_slow = []
n_stim_fast = []
feature_array_slow_all = []
feature_array_fast_all = []




""" # Extract the feature
# Peak speed
if feature == "peak_speed":
    feature_array = np.max(data[:, :, :, mean_speed_idx, :], axis=3)

# Detect and fill outliers (e.g. when subject did not touch the screen)
np.apply_along_axis(lambda m: utils.fill_outliers(m), axis=2, arr=feature_array)

# Normalize to the start and smooth over 5 consecutive movements
feature_array = utils.smooth_moving_average(utils.norm_perc(feature_array), window_size=5)

# Bin
feature_array_slow = [np.median(arr) for arr in np.array_split(feature_array[0, 0, 5:], bins)]
feature_array_fast = [np.median(arr) for arr in np.array_split(feature_array[1, 0, 5:], bins)]

if plot_individual:
    plt.figure(figsize=(15, 5))
    plt.subplot(1, 4, 1)
    plt.plot(slow, label="Slow")
    plt.plot(fast, label="Fast")
    plt.subplot(1, 4, 2)
    plt.plot(feature_array_slow, label="Slow")
    plt.plot(feature_array_fast, label="Fast")
    #plt.title(file_path.basename)
    plt.subplot(1, 4, 3)
    corr, p = pearsonr(feature_array_slow, slow)
    sb.regplot(feature_array_slow, slow)
    plt.title(f"Slow corr = {np.round(corr,2)} p = {np.round(p,3)}")
    plt.subplot(1, 4, 4)
    corr, p = pearsonr(feature_array_fast, fast)
    sb.regplot(feature_array_fast, fast)
    plt.title(f"Fast corr = {np.round(corr,2)} p = {np.round(p,3)}")
    plt.legend()

# Save in array
n_stim_slow.append(slow)
n_stim_fast.append(fast)
# Save the feature values for all datasest
feature_array_slow_all.append(feature_array_slow)
feature_array_fast_all.append(feature_array_fast)

bar()

# Group level analysis
n_stim_slow = np.array(n_stim_slow)
n_stim_fast = np.array(n_stim_fast)
feature_array_slow_all = np.array(feature_array_slow_all)
feature_array_fast_all = np.array(feature_array_fast_all)
# Average
bis_thres = 10
plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
corr, p = spearmanr(feature_array_slow_all[:,:bis_thres].ravel(), n_stim_slow[:,:bis_thres].ravel())
sb.regplot(feature_array_slow_all[:,:bis_thres].ravel(), n_stim_slow[:,:bis_thres].ravel())
plt.title(f"Slow corr = {np.round(corr,2)} p = {np.round(p,3)}")
plt.xlabel(f"$\Delta$ {feature} in %", fontsize=14)
plt.ylabel(f"# of stimulated movements", fontsize=14)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.subplot(1, 2, 2)
corr, p = pearsonr(feature_array_fast_all[:,:bis_thres].ravel(), n_stim_fast[:,:bis_thres].ravel())
sb.regplot(feature_array_fast_all[:,:bis_thres].ravel(), n_stim_fast[:,:bis_thres].ravel())
plt.title(f"Fast corr = {np.round(corr,2)} p = {np.round(p,3)}")
plt.xlabel(f"$\Delta$ {feature} in %", fontsize=14)
plt.ylabel(f"# of stimulated movements", fontsize=14)

plt.show()
"""