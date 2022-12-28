# Extract peak speed from behavioral matlab data

import numpy as np
import matplotlib.pyplot as plt
import mne
import gc
import ICNVigorTask.utils.utils as utils
from mne_bids import BIDSPath, read_raw_bids, print_dir_tree, make_report
from alive_progress import alive_bar
import time
from statannot import add_stat_annotation
import seaborn as sb
from scipy import stats
import matplotlib
import os
from scipy.io import loadmat
import pandas as pd
matplotlib.use('TkAgg')
import warnings
warnings.filterwarnings("ignore")

#bids_root = "C:\\Users\\ICN\\Documents\\VigorStim\\Data\\rawdata\\"
bids_root = "C:\\Users\\alessia\\Documents\\Jobs\\ICN\\vigor-stim\Data\\rawdata\\"
matlab_files_root = "C:\\Users\\alessia\\Documents\\Jobs\ICN\\vigor-stim\\Data\\behavioral_data\\"

# Set analysis parameters
plot_individual = True

# Plot the feature over time for all datasets
peaks_all = []
meds = []
subject = []

# Loop over all files in folder
for filename in os.listdir(matlab_files_root):

    # Load behavioral data
    data = loadmat(os.path.join(matlab_files_root, filename))
    data = data["struct"][0][0][1]

    # Determine the condition based on the filename
    slow_first = 1 if filename.index("Slow") < filename.index("Fast") else 0
    med = "Off" if "Off" in filename else "On"
    meds.append(med)

    # Extract the peak for each trial
    n_trials = 96
    peaks = np.zeros((2, 2, n_trials))
    for i_block in range(1, 5):
        block_type = 0 if i_block in [1, 3] else 1
        cond = 0 if i_block in [1, 2] and slow_first or i_block in [3, 4] and not slow_first else 1
        for i_trial in range(1, n_trials+1):
            mask = np.where(np.logical_and(data[:,7] == i_block, data[:,8] == i_trial))
            peaks[cond, block_type, i_trial - 1] = np.max(data[mask, 3])

    # Save the feature values for all datasest
    peaks_all.append(peaks)

    # Detect and fill outliers (e.g. when subject did not touch the screen)
    np.apply_along_axis(lambda m: utils.fill_outliers(m), axis=2, arr=peaks)
    np.apply_along_axis(lambda m: utils.fill_outliers(m), axis=2, arr=peaks)

    # Normalize to the start and smooth over 5 consecutive movements
    peaks = utils.smooth_moving_average(utils.norm_perc(peaks), window_size=5, axis=3)

    # Plot if needed
    if plot_individual:
        plt.figure(figsize=(10, 5))
        utils.plot_conds(peaks)
        plt.xlabel("Movements")
        plt.ylabel(f"$\Delta$ Speed in %")
        plt.title(filename)

peaks_all = np.array(peaks_all)

# Load the updsr scores and subject names
#df = pd.read_csv("C:\\Users\\alessia\\Documents\\Jobs\ICN\\vigor-stim\\Data\\Dataset_list.xlsx",encoding= 'unicode_escape')

# Save matrix
np.save(f"../../../Data/peak_speed.npy", peaks_all)

plt.show()