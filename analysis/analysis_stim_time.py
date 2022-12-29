# Analysis of tiem of stimulation

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
from scipy.io import loadmat
import os
matplotlib.use('TkAgg')
import warnings
warnings.filterwarnings("ignore")

matlab_files_root = "C:\\Users\\alessia\\Documents\\Jobs\ICN\\vigor-stim\\Data\\behavioral_data\\"

# Set analysis parameters
plot_individual = False
datasets = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20]

# Loop over all datasets
for filename in os.listdir(matlab_files_root):

    # Load behavioral data
    data = loadmat(os.path.join(matlab_files_root, filename))
    data = data["struct"][0][0][1]

    # Determine the condition based on the filename
    slow_first = 1 if filename.index("Slow") < filename.index("Fast") else 0

    # Extract the relative time of stimulation for each movement
    # At how much % of the movement the stimulation started
    n_trials = 96
    feature = np.zeros((2, 2, n_trials))
    for i_block in range(1, 5):
        block_type = 0 if i_block in [1, 3] else 1
        cond = 0 if i_block in [1, 2] and slow_first or i_block in [3, 4] and not slow_first else 1
        for i_trial in range(1, n_trials + 1):
            mask = np.where(np.logical_and(data[:, 7] == i_block, data[:, 8] == i_trial))
            data_move = np.squeeze(data[mask, :])
            # Get index of peak speed
            idx_peak_speed = np.argmax(data_move[:, 3])
            # Get idx of movement onset and offset (closest sample to peak below threshold)
            move_thres = 500
            onset_idx = np.where(data_move[:, 3] < move_thres)[0][np.where((idx_peak_speed - np.where(data_move[:, 3] < move_thres)) > 0)[1][-1]]
            offset_idx = np.where(data_move[:, 3] < move_thres)[0][np.where((idx_peak_speed - np.where(data_move[:, 3] < move_thres)) < 0)[1][0]]
            # Compute different things tomorrow

            plt.figure()
            plt.plot(data_move[:,3].ravel())
            plt.axvline(onset_idx)
            plt.axvline(offset_idx)
            plt.show()



    # Detect and fill outliers (e.g. when subject did not touch the screen)
    np.apply_along_axis(lambda m: utils.fill_outliers(m), axis=3, arr=peak_speed)

# Normalize to the start of each stimulation block
peak_speed = utils.norm_perc(peak_speed)

# Smooth over 5 consecutive movements
#peak_speed = utils.smooth_moving_average(peak_speed, window_size=5, axis=3)

# Load stim time matrix
stim_time = np.load(f"../../../Data/stim_time.npy")
stim_time = stim_time[datasets, :, :, :]

# Load speed peak time matrix
peak_speed_time = np.load(f"../../../Data/peak_speed_time.npy")
peak_speed_time = peak_speed_time[datasets, :, :, :]

# Bin time of stimulation and peak speed
bins = 15
stim_time_bin = np.array([np.nanmean(arr, axis=3) for arr in np.array_split(stim_time, bins, axis=3)])
peak_speed_bin = np.array([np.median(arr, axis=3) for arr in np.array_split(peak_speed, bins, axis=3)])

# Plot as scatter plot and compute correlation for each condition
cond_names = ["Slow", "Fast"]
plt.figure(figsize=(12, 4))
for cond in range(2):
    plt.subplot(1, 2, cond+1)
    corr, p = spearmanr(peak_speed_bin[:, :, cond, 0].ravel(), stim_time_bin[:, :, cond, 0].ravel())
    sb.regplot(peak_speed_bin[:, :, cond, 0].ravel(),stim_time_bin[:, :, cond, 0].ravel())
    plt.title(f"{cond_names[cond]} stim, corr = {np.round(corr,2)}, p = {np.round(p,3)}", fontweight='bold')
    plt.xlabel(f"$\Delta$ speed in %", fontsize=14)
    plt.ylabel(f"Time of stimualtion", fontsize=14)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.subplots_adjust(bottom=0.15, hspace=0.2)

plt.show()