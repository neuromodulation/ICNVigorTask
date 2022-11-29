# Script for further analysis
# Cumlative change in velocity

import numpy as np
import matplotlib.pyplot as plt
import mne
import easygui
import gc
import os
from ICNVigorTask.utils.utils import reshape_data_trials, norm_speed, smooth_moving_average, plot_speed, \
    fill_outliers, norm_perf_speed, norm_0_1

# Set analysis parameters
plot_individual = True
med = "MedOff"

# Get list of all datasets
path = "D:\\rawdata\\rawdata\\"
folder_list = os.listdir(path)
files_list = []
# Loop over every subject
for subject_folder in folder_list:
    # Get the brainvision files for that subject
    for root, dirs, files in os.walk(path+subject_folder):
        for file in files:
            if (file.endswith(".vhdr")) and "VigorStim" in file and "neuro_behav." in file and "EL012" in file:
                files_list.append(os.path.join(root, file))

# Plot the speed of all datasets
for file in files_list:
    raw_data = mne.io.read_raw_brainvision(file, preload=True)
    # Rename
    # Load the dataset of interest
    filename_new = file[:-11] + ".vhdr"
    mne.export.export_raw(fname=filename_new, raw=raw_data, fmt="brainvision", overwrite=True)


