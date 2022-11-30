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
            if (file.endswith(".vhdr")) and "VigorStim" in file and "neuro" in file and med in file:
                files_list.append(os.path.join(root, file))

for file in files_list:

    # Load the dataset of interest
    raw_data = mne.io.read_raw_brainvision(file, preload=True)
    ch_names = raw_data.info['ch_names']
    ch_lfp = mne.pick_channels_regexp(ch_names, 'LFP *')

    # Plot power spectrum
    #raw_data.compute_psd(fmin=0, fmax=50).plot()
    # Compute the power spectra
    plt.figure()
    psds, freqs = mne.time_frequency.psd_welch(raw_data.pick_channels(np.array(ch_names)[ch_lfp]), fmin=1, fmax=50, n_fft=500)
    plt.plot(freqs, psds.T)

plt.show()
