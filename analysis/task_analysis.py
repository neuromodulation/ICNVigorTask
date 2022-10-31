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
peak_speed_all = []
peak_speed_cum_all = []
for file in files_list:

    # Load the dataset of interest
    raw_data = mne.io.read_raw_brainvision(file, preload=True)

    # Extract whether a trial was stimulated or not
    stim_idx = raw_data.info["ch_names"].index("stim")
    data = reshape_data_trials(raw_data)
    stim_data = data[:, 0, :, stim_idx, :]
    stim = np.any(stim_data, axis=2)
    slow_idx = np.where(stim[0, :])
    fast_idx = np.where(stim[1, :])
    plt.hist(slow_idx, bins=10, label="Slow")
    plt.hist(fast_idx, bins=10, label="Fast")
    plt.legend()
    print("END")