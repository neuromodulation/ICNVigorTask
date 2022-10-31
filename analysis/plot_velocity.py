# Script to plot the velocity of one dataset
# TODO
# After museum: Start new analysis and do list

import numpy as np
import matplotlib.pyplot as plt
import mne
import easygui
import os
from ICNVigorTask.utils.utils import reshape_data_trials, norm_speed, smooth_moving_average, plot_speed, fill_outliers

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
            if (file.endswith(".vhdr")) and "behav" in file:
                files_list.append(os.path.join(root, file))

# Plot the speed of all datasets
peak_speed_all = []
for file in files_list:

    # Load the dataset of interest
    raw_data = mne.io.read_raw_brainvision(file, preload=True)

    # Get the channel index of the mean speed values
    mean_speed_idx = raw_data.info["ch_names"].index("mean_vel")

    # Structure data in trials and blocks
    data = reshape_data_trials(raw_data)

    # Extract the peak speed of all trials
    peak_speed = np.max(data[:, :, :, mean_speed_idx, :], axis=3)

    # Normalize them to the start speed
    peak_speed = norm_speed(peak_speed)

    # Detect and fill outliers (e.g. when subject did not touch the screen)
    peak_speed = fill_outliers(peak_speed)

    # Plot if needed
    if plot_individual:
        plt.figure()
        plot_speed(smooth_moving_average(peak_speed))
        plt.legend()
        plt.title(file.split("\\")[-1])

    # Save the speed values for all datasest
    peak_speed_all.append(peak_speed)

# Average over all datasets
peak_speed_all = np.array(peak_speed_all)
mean_peak_speed = np.mean(peak_speed_all, axis=0)
# Plot
plt.figure()
plot_speed(smooth_moving_average(mean_peak_speed))
plt.legend()
plt.title("Average")
plt.show()