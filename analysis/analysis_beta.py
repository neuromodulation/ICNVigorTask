# Script for analysing neurophysioligical properties of the data
# Average beta power after movement onset, peak and movement offset

import numpy as np
import matplotlib.pyplot as plt
import mne
import easygui
import gc
import os
from mne_bids import BIDSPath, read_raw_bids, print_dir_tree, make_report
from ICNVigorTask.utils.utils import reshape_data_trials, norm_speed, smooth_moving_average, plot_speed, \
    fill_outliers, norm_perf_speed, norm_0_1, get_bids_filepath, add_average_channels_electrode

bids_root = "C:\\Users\\alessia\\Documents\\Jobs\\ICN\\vigor-stim\\Data\\rawdata\\"

# Set analysis parameters
med = "Off"
plot_individual = True
subject_list = ["EL013", "EL014", "EL015", "EL016", "EL006", "EL007", "EL008",
             "L002", "L005", "L006", "L007", "L008"]

# Plot the speed of all datasets
peak_speed_all = []
peak_speed_cum_all = []
for subject in subject_list:

    # Read one dataset from every participant
    file_path = get_bids_filepath(root=bids_root, subject=subject, task="VigorStim", med=med)
    if not file_path:
        continue

    # Load the dataset of interest
    raw = read_raw_bids(bids_path=file_path, verbose=False)
    raw.load_data()

    # Drop bad channels
    raw.drop_channels(raw.info["bads"])
    ch_names = raw.info['ch_names']

    # Add average channels
    add_average_channels_electrode(raw)

    # Add bipolar channels

    # Get the average left bipolar LFP channels

    # Plot power spectrum
    raw.crop(tmax=20)
    raw.notch_filter(130)
    #raw.filter(l_freq=1, h_freq=60)
    raw.compute_psd(fmin=0, fmax=50, n_fft=1048).plot()

    # Remove the artifact

plt.show()
