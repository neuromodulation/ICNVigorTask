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
            if (file.endswith(".tsv")) and "VigorStim" in file and "new" in file:
                files_list.append(os.path.join(root, file))

for file in files_list:
    # Load
    tsv_file = pd.read_csv(file, sep='\t')
    # Save with new name
    new_file = file[:-16] + "desc-neurobehav_channels.tsv"
    with open(new_file,'w') as write_tsv:
        write_tsv.write(tsv_file.to_csv(sep='\t', index=False))


