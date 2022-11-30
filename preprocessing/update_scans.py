# Get list of vhdr files in folder and add to scans tsv file

import numpy as np
import matplotlib.pyplot as plt
import mne
import easygui
import gc
import os
from ICNVigorTask.utils.utils import reshape_data_trials, norm_speed, smooth_moving_average, plot_speed, \
    fill_outliers, norm_perf_speed, norm_0_1
import pandas as pd

# Get list of all datasets
path = "D:\\rawdata\\rawdata\\"
folder_list = os.listdir(path)
files_list = []
# Loop over every subject
for subject_folder in folder_list:
    # Get the scan files
    for root, dirs, files in os.walk(path+subject_folder):
        for file in files:
            if (file.endswith(".tsv")) and "scans" in file:
                files_list.append(os.path.join(root, file))

# Loop over every scan file and update it (add all vhdr files in folder)
for file in files_list:

    # Get folder path
    folder_path = "\\".join(file.split("\\")[:-1])+"\\"

    # Load scans file
    scans_file = pd.read_csv(file, sep='\t')

    # Get vhdr files and update scans file if missing
    files_list_tmp = []
    for root, dirs, files in os.walk(folder_path):
        for file_tmp in files:
            if (file_tmp.endswith(".vhdr")):
                tmp = root.split("\\")[-1] + "/" + file_tmp
                # Check if filename already in scans, if not add it
                if not np.any(tmp == scans_file.filename):
                    scans_file.loc[len(scans_file)] = scans_file.loc[0]
                    scans_file.loc[len(scans_file) - 1].filename = tmp

    # Save with new name
    with open(file, 'w') as write_tsv:
        write_tsv.write(scans_file.to_csv(sep='\t', index=False))


