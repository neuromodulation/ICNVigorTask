# Script for task analysis
# Get the time that stimulation occured during movement

import numpy as np
import matplotlib.pyplot as plt
import mne
import easygui
import os
from ICNVigorTask.utils.utils import reshape_data_trials, norm_speed, smooth_moving_average, plot_speed, fill_outliers, norm_perf_speed

# Set analysis parameters
plot_individual = True

# Get list of all datasets
path = "D:\\VigorStim_data\\"
folder_list = os.listdir(path)
files_list = []
# Loop over every subject
for subject_folder in folder_list:
    # Get the brainvision files for that subject
    for root, dirs, files in os.walk(path+subject_folder):
        for file in files:
            if (file.endswith(".vhdr")) and "behav" in file and "Off" in file:
                files_list.append(os.path.join(root, file))

# Plot the speed of all datasets
perc_stim_move_all = []
for file in files_list:

    # Load the dataset of interest
    raw_data = mne.io.read_raw_brainvision(file, preload=True)
    data = reshape_data_trials(raw_data)
    n_trials = data.shape[2]

    # Get the index of channels of interest
    stim_idx = raw_data.info["ch_names"].index("stim")
    target_idx = raw_data.info["ch_names"].index("target")
    mean_speed_idx = raw_data.info["ch_names"].index("mean_vel")
    speed_idx = raw_data.info["ch_names"].index("vel")

    perc_stim_move = np.zeros((2, n_trials))
    for i in range(2):
        for j in range(n_trials):
            # Extract the stimulation onset
            stim = np.where(data[i, 0, j, stim_idx, :])[0]
            if np.any(stim):
                stim_onset_idx = stim[0]
                # Determine the start of the movement
                start_move_idx = np.where(data[i, 0, j, mean_speed_idx, :] > 200)[0][0]
                # Determine the end of movement/when the target is reached
                end_move_idx = np.where(data[i, 0, j, target_idx, :])[0][0]
                # Compute the length of the movement and how much % occured during stimulation
                perc_stim_move[i, j] = (end_move_idx - stim_onset_idx) / (end_move_idx - start_move_idx)

     #Plot
    if plot_individual:
        plt.figure()
        slow_perc = perc_stim_move[0, :]
        slow_perc = slow_perc[slow_perc != 0]
        plt.hist(slow_perc, label="slow")
        fast_perc = perc_stim_move[1, :]
        fast_perc = fast_perc[fast_perc != 0]
        plt.hist(fast_perc, label="fast")
        plt.legend()
        plt.title(file.split("\\")[-1])

    # Save for all datasets
    perc_stim_move_all.append(perc_stim_move)

# Plot for all datasets averaged
mean_perc_stim_move = np.mean(np.array(perc_stim_move_all), axis=0)
plt.figure()
slow_perc = mean_perc_stim_move[0, :]
slow_perc = slow_perc[slow_perc != 0]
plt.hist(slow_perc, label="slow")
fast_perc = mean_perc_stim_move[1, :]
fast_perc = fast_perc[fast_perc != 0]
plt.hist(fast_perc, label="fast")
plt.title("Average")
plt.legend()
plt.show()