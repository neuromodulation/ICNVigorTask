# Extract feature from behavioral matlab data

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
import os
from scipy.io import loadmat
import pandas as pd
matplotlib.use('TkAgg')
import warnings
warnings.filterwarnings("ignore")

matlab_files_root = "../../Data/behavioral_data/"

# Set analysis parameters
plot_individual = False
feature_name = "peak_speed" # out of ["mean_speed","move_dur", "peak_speed", "stim_time", "peak_speed_time", "move_onset_time", "move_offset_time", "fast", "slow"]

feature_all = []
slow_first_all = []
# Loop over all files in folder
for filename in os.listdir(matlab_files_root):

    # Load behavioral data
    data = loadmat(os.path.join(matlab_files_root, filename))
    data = data["struct"][0][0][1]

    # Determine the condition based on the filename
    slow_first = 1 if filename.index("Slow") < filename.index("Fast") else 0

    # Save
    slow_first_all.append(slow_first)

    # Extract the peak for each trial
    n_trials = 96
    feature = np.zeros((2, 2, n_trials))
    for i_block in range(1, 5):
        block_type = 0 if i_block in [1, 3] else 1
        cond = 0 if i_block in [1, 2] and slow_first or i_block in [3, 4] and not slow_first else 1
        for i_trial in range(1, n_trials+1):
            mask = np.where(np.logical_and(data[:,7] == i_block, data[:,8] == i_trial))
            data_mask = np.squeeze(data[mask, :])
            if feature_name == "peak_speed":
                feature[cond, block_type, i_trial - 1] = np.max(data[mask, 3])
                #feature[cond, block_type, i_trial - 1] = np.percentile(data[mask, 3], 95)
            elif feature_name == "peak_acc":
                # Get index of peak speed
                idx_peak_speed = np.argmax(data_mask[:, 3])
                # Get idx of movement onset and offset (closest sample to peak below threshold)
                move_thres = 300
                onset_idx = np.where(data_mask[:, 3] < move_thres)[0][
                    np.where((idx_peak_speed - np.where(data_mask[:, 3] < move_thres)) > 0)[1][-1]]
                try:
                    offset_idx = np.where(data_mask[:, 3] < move_thres)[0][
                        np.where((idx_peak_speed - np.where(data_mask[:, 3] < move_thres)) < 0)[1][0]]
                    feature[cond, block_type, i_trial - 1] = np.percentile(np.diff(data_mask[onset_idx:offset_idx, 3]), 95)
                except:
                    feature[cond, block_type, i_trial - 1] = np.percentile(np.diff(data_mask[onset_idx:, 3]), 95)
            elif feature_name == "stim_time":
                idx_stim = np.where(data_mask[:, 10] == 1)[0]
                if len(idx_stim) > 0:
                    stim_time = data_mask[idx_stim[0], 2] - data_mask[0, 2]
                else:
                    stim_time = None
                feature[cond, block_type, i_trial - 1] = stim_time
            elif feature_name == "speed_peak_time":
                peak_idx = np.argmax(data_mask[:, 3])
                feature[cond, block_type, i_trial - 1] = data_mask[peak_idx, 2] - data_mask[0, 2]
            elif feature_name == "move_onset_time":
                # Get index of peak speed
                idx_peak_speed = np.argmax(data_mask[:, 3])
                # Get idx of movement onset (closest sample to peak below threshold)
                move_thres = 300
                onset_idx = np.where(data_mask[:, 3] < move_thres)[0][
                    np.where((idx_peak_speed - np.where(data_mask[:, 3] < move_thres)) > 0)[1][-1]]
                feature[cond, block_type, i_trial - 1] = data_mask[onset_idx, 2] - data_mask[0, 2]
            elif feature_name == "move_offset_time":
                idx_peak_speed = np.argmax(data_mask[:, 3])
                move_thres = 300
                try:
                    offset_idx = np.where(data_mask[:, 3] < move_thres)[0][np.where((idx_peak_speed - np.where(data_mask[:, 3] < move_thres)) < 0)[1][0]]
                    feature[cond, block_type, i_trial - 1] = data_mask[offset_idx, 2] - data_mask[0, 2]
                except:
                    feature[cond, block_type, i_trial - 1] = None
            elif feature_name == "move_dur":
                # Get index of peak speed
                idx_peak_speed = np.argmax(data_mask[:, 3])
                # Get idx of movement onset and offset (closest sample to peak below threshold)
                move_thres = 300
                try:
                    onset_idx = np.where(data_mask[:, 3] < move_thres)[0][np.where((idx_peak_speed - np.where(data_mask[:, 3] < move_thres)) > 0)[1][-1]]
                    offset_idx = np.where(data_mask[:, 3] < move_thres)[0][np.where((idx_peak_speed - np.where(data_mask[:, 3] < move_thres)) < 0)[1][0]]
                    feature[cond, block_type, i_trial - 1] = data_mask[offset_idx, 2] - data_mask[onset_idx, 2]
                except:
                    feature[cond, block_type, i_trial - 1] = data_mask[-1, 2] - data_mask[onset_idx, 2]
            elif feature_name == "move_dur_start":
                # Get index of peak speed
                idx_peak_speed = np.argmax(data_mask[:, 3])
                # Get idx of movement onset and offset (closest sample to peak below threshold)
                move_thres_2 = 500
                move_thres_1 = 100
                try:
                    onset_idx = np.where(data_mask[:, 3] < move_thres_1)[0][
                        np.where((idx_peak_speed - np.where(data_mask[:, 3] < move_thres_1)) > 0)[1][-1]]
                    offset_idx = np.where(data_mask[:, 3] < move_thres_2)[0][
                        np.where((idx_peak_speed - np.where(data_mask[:, 3] < move_thres_2)) < 0)[1][0]]
                    feature[cond, block_type, i_trial - 1] = data_mask[offset_idx, 2] - data_mask[onset_idx, 2]
                except:
                    feature[cond, block_type, i_trial - 1] = None
            elif feature_name == "mean_speed":
                # Get index of peak speed
                idx_peak_speed = np.argmax(data_mask[:, 3])
                # Get idx of movement onset and offset (closest sample to peak below threshold)
                move_thres = 300
                try:
                    onset_idx = np.where(data_mask[:, 3] < move_thres)[0][np.where((idx_peak_speed - np.where(data_mask[:, 3] < move_thres)) > 0)[1][-1]]
                    offset_idx = np.where(data_mask[:, 3] < move_thres)[0][np.where((idx_peak_speed - np.where(data_mask[:, 3] < move_thres)) < 0)[1][0]]
                    feature[cond, block_type, i_trial - 1] = np.mean(data_mask[onset_idx:offset_idx, 3])
                except:
                    feature[cond, block_type, i_trial - 1] = None
            elif feature_name == "median_acc":
                # Get index of peak speed
                idx_peak_speed = np.argmax(data_mask[:, 3])
                # Get idx of movement onset and offset (closest sample to peak below threshold)
                move_thres = 300
                onset_idx = np.where(data_mask[:, 3] < move_thres)[0][
                    np.where((idx_peak_speed - np.where(data_mask[:, 3] < move_thres)) > 0)[1][-1]]
                try:
                    offset_idx = np.where(data_mask[:, 3] < move_thres)[0][
                        np.where((idx_peak_speed - np.where(data_mask[:, 3] < move_thres)) < 0)[1][0]]
                    feature[cond, block_type, i_trial - 1] = np.median(np.diff(data_mask[onset_idx:offset_idx, 3]))
                except:
                    feature[cond, block_type, i_trial - 1] = np.median(np.diff(data_mask[onset_idx:, 3]))
            # Get index of all slow movements (peak speed slower than the last two movements)
            elif feature_name == "fast" and i_trial > 3:
                # Get peak speed from current trials and two previous trials
                peak_speed = np.max(data[mask, 3])
                peak_speed_prev_1 = np.max(data[np.where(np.logical_and(data[:, 7] == i_block, data[:, 8] == i_trial - 1)), 3])
                peak_speed_prev_2 = np.max(data[np.where(np.logical_and(data[:, 7] == i_block, data[:, 8] == i_trial - 2)), 3])
                if peak_speed > peak_speed_prev_1 and peak_speed > peak_speed_prev_2:
                    feature[cond, block_type, i_trial - 1] = 1
            elif feature_name == "slow" and i_trial > 3:
                # Get peak speed from current trials and two previous trials
                peak_speed = np.max(data[mask, 3])
                peak_speed_prev_1 = np.max(data[np.where(np.logical_and(data[:, 7] == i_block, data[:, 8] == i_trial - 1)), 3])
                peak_speed_prev_2 = np.max(data[np.where(np.logical_and(data[:, 7] == i_block, data[:, 8] == i_trial - 2)), 3])
                if peak_speed < peak_speed_prev_1 and peak_speed < peak_speed_prev_2:
                    feature[cond, block_type, i_trial - 1] = 1
            elif feature_name == "time_to_peak":
                # Get index of peak speed
                idx_peak_speed = np.argmax(data_mask[:, 3])
                # Get idx of movement onset (closest sample to peak below threshold)
                move_thres = 300
                onset_idx = np.where(data_mask[:, 3] < move_thres)[0][
                    np.where((idx_peak_speed - np.where(data_mask[:, 3] < move_thres)) > 0)[1][-1]]
                feature[cond, block_type, i_trial - 1] = data_mask[idx_peak_speed, 2] - data_mask[onset_idx, 2]
            elif feature_name == "motor_range":
                feature[cond, block_type, i_trial - 1] = np.percentile(data_mask[:, 3], 95) - np.percentile(data_mask[:, 3], 5)

    # Save the feature values for all datasest
    feature_all.append(feature)

    # Plot if needed
    if plot_individual:
        # Detect and fill outliers (e.g. when subject did not touch the screen)
        np.apply_along_axis(lambda m: utils.fill_outliers_mean(m), axis=2, arr=feature)

        # Normalize to the start and smooth over 5 consecutive movements
        feature = utils.smooth_moving_average(utils.norm_perc(feature), window_size=5)

        plt.figure(figsize=(10, 5))
        utils.plot_conds(feature)
        plt.xlabel("Movements")
        plt.ylabel(f"$\Delta$ {feature_name} in %")
        plt.title(filename)

feature_all = np.array(feature_all)

# Save matrix
np.save(f"../../Data/{feature_name}.npy", feature_all)

# Save slow first
np.save(f"../../Data/slow_first.npy", slow_first_all)

plt.show()