# Script to plot the velocity of one dataset
# TODO
# After museum: Start new analysis and do list

import numpy as np
import matplotlib.pyplot as plt
import mne
import easygui
import os
from ICNVigorTask.utils.utils import reshape_data_trials, norm_speed, smooth_moving_average, plot_speed

# Set analysis parameters
plot_individual = True

# Get list of all datasets
path = "D:\\VigorStim_data\\"
folder_list = os.listdir(path)
files_list = []
files_list_behav = []
slow_first_list = []
# Loop over every subject
for subject_folder in folder_list:
    # Get the brainvision files for that subject
    for root, dirs, files in os.walk(path + subject_folder):
        for file in files:
            if (file.endswith(".vhdr")) and "behav" in file:
                files_list.append(os.path.join(root, file))
            if (file.endswith(".mat")):
                files_list_behav.append(os.path.join(root, file))
                name = os.path.join(root, file)
                # Create txt file with slow_first information
                slow_first = 1 if name.index("Slow") < name.index("Fast") else 0
                with open(root+'\\slow_first.txt', 'w') as f:
                    f.write(str(slow_first))
                slow_first_list.append(slow_first)

# Plot the speed of all datasets
slow_first_list = [0,0,0,1,0,0,0,0,1,0]
for j, file in enumerate(files_list):

    # Load the dataset of interest
    raw_data = mne.io.read_raw_brainvision(file, preload=True)
    # Get the channel index of the mean speed values
    block_idx = raw_data.info["ch_names"].index("block")

    # Add cond
    cond = [0 if i in [1, 2] and slow_first_list[j] or i in [3, 4] and not slow_first_list[j] else 1 for i in raw_data._data[block_idx, :]]

    ch_names = ["cond"]
    info = mne.create_info(ch_names, raw_data.info['sfreq'], ["bio"])
    behav_raw = mne.io.RawArray(np.array(cond)[np.newaxis,:], info)
    raw_data.add_channels([behav_raw], force_update_info=True)

    # Save new brain vision file
    mne.export.export_raw(fname=file, raw=raw_data, fmt="brainvision",
                          overwrite=True)

    print("Successfully merged neurophysiological and behavioral data")
