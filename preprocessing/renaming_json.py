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
import pandas as pd
import json


# Get list of all datasets
path = "D:\\rawdata\\rawdata\\"
folder_list = os.listdir(path)
files_list = []
# Loop over every subject
for subject_folder in folder_list:
    # Get the brainvision files for that subject
    for root, dirs, files in os.walk(path+subject_folder):
        for file in files:
            if (file.endswith(".json")) and "VigorStim" in file and "new" in file:
                files_list.append(os.path.join(root, file))

for file in files_list:
    # Load
    with open(file, 'r') as f:
        json_file = json.load(f)
    # Save with new name
    new_file = file[:-13] + "desc-neurobehav_ieeg.json"
    with open(new_file, 'w', encoding='utf-8') as f:
        json.dump(json_file, f, indent=4)


