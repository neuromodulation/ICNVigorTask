# Create brain vision file with behavioral data

import matplotlib.pyplot as plt
import mne
from scipy.io import loadmat, savemat
from scipy.stats import zscore
import numpy as np
import pandas as pd
import os
import json
from ICNVigorTask.utils.utils import norm_0_1
import os

# Get template file
path = "D:\\rawdata\\rawdata\\"
folder_list = os.listdir(path)
for subject_folder in folder_list:
    for root, dirs, files in os.walk(path+subject_folder):
        for file in files:
            if (file.endswith(".vhdr")) and "VigorStim" in file and "EL012" in file and "new" not in file:
                filename_raw_tmp = os.path.join(root, file)
                break

# Get MATLAB datasets for which a brainvision file should be created
path = "D:\\rawdata\\rawdata\\"
folder_list = os.listdir(path)
IDs = ["sub-05-"]
files_mat_list = []
for subject_folder in folder_list:
    for root, dirs, files in os.walk(path+subject_folder):
        for file in files:
            if (file.endswith(".mat")) and any(ID in file for ID in IDs):
                files_mat_list.append(os.path.join(root, file))

for filename_mat in files_mat_list:

    # Load template TMSi data
    raw_data = mne.io.read_raw_brainvision(filename_raw_tmp, preload=True)
    ch_names_old = raw_data.info["ch_names"]

    # Load the MATLAB data
    behav_data = loadmat(filename_mat)
    # Extract the behavioral data stored in a matrix
    behav_data = behav_data["struct"][0][0][1]
    # Determine the condition based on the filename
    slow_first = 1 if filename_mat.index("Slow") < filename_mat.index("Fast") else 0

    # Add a channel containing the condition
    cond = [0 if i in [1, 2] and slow_first or i in [3, 4] and not slow_first else 1 for i in behav_data[:, 7]]
    behav_data = np.hstack((behav_data, np.array(cond)[:, np.newaxis]))
    # Choose the channels fo interest
    behav_data = behav_data[:, [0,1,3,4,7,8,9,10,11,12,16]]

    # Crop the data
    n_sec = np.ceil(len(behav_data) / raw_data.info["sfreq"])
    raw_data.crop(tmin=0, tmax=n_sec)

    # Add missing 0s
    n_missing = raw_data._data.shape[1] - len(behav_data)
    behav_data = np.vstack((behav_data, np.zeros((n_missing, behav_data.shape[1]))))

    # add behavioral data
    ch_names = ["PEN_X", "PEN_Y", "SPEED_MEAN", "SPEED", "BLOCK", "TRIAL", "TARGET", "STIMULATION", "TARGET_X", "TARGET_Y", "STIM_CONDITION"]
    info = mne.create_info(ch_names, raw_data.info['sfreq'], ["bio"]*len(ch_names))
    behav_raw = mne.io.RawArray(behav_data.T, info)
    raw_data.add_channels([behav_raw], force_update_info=True)

    # Delete neuro channels
    raw_data.drop_channels(ch_names_old)

    # Save new brain vision file
    filename_new = filename_mat[:-4]+"neuro.vhdr"
    mne.export.export_raw(fname=filename_new, raw=raw_data, fmt="brainvision", overwrite=True)
