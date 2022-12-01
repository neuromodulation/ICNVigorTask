
import numpy as np
import matplotlib.pyplot as plt
import mne
import easygui
import gc
import os
from ICNVigorTask.utils.utils import reshape_data_trials, norm_speed, smooth_moving_average, plot_speed, \
    fill_outliers, norm_perf_speed, norm_0_1
import shutil

# Delete non vigor stim datasets
path = "E:\\rawdata\\rawdata\\"
folder_list = os.listdir(path)
files_list = []
for subject_folder in folder_list:
    for root, dirs, files in os.walk(path+subject_folder):
        for dir in dirs:
            keep = False
            for file in os.listdir(os.path.join(root, dir, "ieeg")):
                if "VigorStim" in file:
                    keep = True
            # Delete
            if not keep:
                shutil.rmtree(os.path.join(root, dir))


