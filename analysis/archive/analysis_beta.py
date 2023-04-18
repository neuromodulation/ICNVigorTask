# Script for analysing neurophysioligical properties of the data
# Average beta power after movement onset, peak and movement offset!

import numpy as np
import matplotlib.pyplot as plt
import mne
#import easygui
import gc
import os
import utils.utils as utils
from mne_bids import BIDSPath, read_raw_bids, print_dir_tree, make_report
#from utils.utils import reshape_data_trials, norm_speed, smooth_moving_average, plot_speed, \
 #   fill_outliers, norm_perf_speed, norm_0_1, get_bids_filepath, add_average_channels_electrode, add_bipolar_channels, \
 #   get_onset_idx, get_offset_idx, get_peak_idx, add_events

bids_root = "C:\\Users\\alessia\\Documents\\Jobs\\ICN\\vigor-stim\\Data\\rawdata\\"

# Set analysis parameters
med = "Off"
plot_individual = True
subject_list = ["EL013", "EL014", "EL015", "EL016", "EL006", "EL007", "EL008", "L002", "L005", "L006", "L007", "L008"]

# Plot the speed of all datasets
peak_speed_all = []
peak_speed_cum_all = []
for subject in subject_list:

    # Read one dataset from every participant
    file_path = utils.get_bids_filepath(root=bids_root, subject=subject, task="VigorStim", med=med)
    if not file_path:
        continue

    # Load the dataset of interest
    raw = read_raw_bids(bids_path=file_path, verbose=False)
    raw.load_data()

    # Drop bad channels
    raw.drop_channels(raw.info["bads"])

    # Add average channels
    average_channels = add_average_channels_electrode(raw)

    # Add bipolar channels (use all average channels that were just added with all possible combinations on one electrode)
    bipolar_channels = add_bipolar_channels(raw, average_channels)

    # Filter the data
    raw.filter(l_freq=1, h_freq=80)
    raw.notch_filter(50)

    # Add onset, offset, peak events
    onset_idx = get_onset_idx(raw)
    offset_idx = get_offset_idx(raw)
    peak_idx = get_peak_idx(raw)
    events = add_events(raw, onset_idx, offset_idx, peak_idx)

    # Epoch around the events and plot the average time frequency plot
    raw.crop(tmin=500)
    raw.pick_channels(bipolar_channels)
    for event_id in [1,2,3]:
        epochs = mne.Epochs(raw, events=events, event_id=event_id, tmin=-0.5, tmax=0.5)
        # Get the time-frequency analysis
        power, itc = mne.time_frequency.tfr_morlet(epochs, freqs=np.arange(5, 80), n_cycles=2)
        power.plot([1], mode='logratio', title=power.ch_names[1])

        power = mne.time_frequency.tfr_morlet(epochs, freqs=np.arange(5, 80), n_cycles=2, average=False, return_itc=False)

    # Crop for initial analysis - remove stimulation artifacts
    #raw.crop(tmax=200)

    # Compute power spectrum
    spectrum = raw.copy().pick_channels(bipolar_channels).compute_psd(method="multitaper", fmin=1, fmax=50)
    spectrum.plot(dB=False)
    lfp_data = raw.get_data(bipolar_channels)
    psds, freqs = mne.time_frequency.psd_array_multitaper(lfp_data, sfreq=500, fmin=1, fmax=50)
    plt.figure()
    plt.plot(freqs, 10 * np.log(psds.T))
    #plt.show()

    # Get the power over time
    lfp_data = raw.get_data(bipolar_channels)[np.newaxis,:,:]
    lfp_tfr = mne.time_frequency.tfr_array_morlet(lfp_data, sfreq=raw.info["sfreq"], freqs=np.arange(2,80), output="power")
    plt.imshow(np.squeeze(10 * np.log(lfp_tfr[:, 3, :, :])), aspect="auto")
    #plt.show()



    # Plot frequenvy spectrum around onset, peak and offset

plt.show()
