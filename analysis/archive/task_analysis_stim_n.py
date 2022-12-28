# Script for task analysis

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
n_stim_slow = []
n_stim_fast = []
for file in files_list:

    # Load the dataset of interest
    raw_data = mne.io.read_raw_brainvision(file, preload=True)

    # Extract whether a trial was stimulated or not
    stim_idx = raw_data.info["ch_names"].index("stim")
    data = reshape_data_trials(raw_data)
    stim_data = data[:, 0, :, stim_idx, :]
    stim = np.any(stim_data, axis=2)
    bins = 10
    slow = [np.sum(arr) for arr in np.array_split(stim[0, :], bins)]
    fast = [np.sum(arr) for arr in np.array_split(stim[1, :], bins)]

    if plot_individual:
        plt.figure()
        plt.plot(slow, label="Slow")
        plt.plot(fast, label="Fast")
        plt.title(file.split("\\")[-1])
        plt.legend()

    # Save in array
    n_stim_slow.append(slow)
    n_stim_fast.append(fast)

# Average
slow_mean = np.mean(np.array(n_stim_slow), axis=0)
fast_mean = np.mean(np.array(n_stim_fast), axis=0)
plt.figure()
plt.plot(slow_mean, label="Slow")
plt.plot(fast_mean, label="Fast")
plt.title("Average")
plt.legend()
plt.show()