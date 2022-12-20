import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import zscore
from mne_bids import BIDSPath
import mne
import itertools
from typing import Sequence

def norm_0_1(array):
    """Return array normalized to values between 0 and 1"""
    return (array - np.min(array)) / (np.max(array - np.min(array)))


def norm_speed(array):
    """Normalize speed to stimulation block start
    array: (2x2x96)(Conditions, Blocks, Trials)"""
    # Substract the mean of the first 5 movements in each stimulation block from the speed of the subsequent stimulation
    # and recovery block
    array_norm = array - np.mean(array[:, 0, 5:10], axis=1)[:, np.newaxis, np.newaxis]
    return array_norm


def norm_perf_speed(array):
    """Normalize speed to stimulation block start and return as percentage
    array: (2x2x96)(Conditions, Blocks, Trials)"""
    mean_start = np.mean(array[:, 0, 5:10], axis=1)[:, np.newaxis, np.newaxis]
    array_norm = ((array - mean_start) / mean_start) * 100
    return array_norm


def reshape_data_trials(raw_data):
    """Gives back the data in a array format reshaped in trials
    shape (2x2x96xn_chansx50000)(Conditions, Blocks, Trials, Channels, Time samples)
    2 conditions = 1 slow - 2 fast (always this order)
    2 blocks per condition = 1 stimulation - 2 recovery
    96 trials per block
    50000 = standard trial length, filled with 0s if trial is shorter """
    blocks = raw_data.get_data(["BLOCK"])
    trials = raw_data.get_data(["TRIAL"])
    data = raw_data.get_data()
    n_chans = data.shape[0]
    n_trials = int(np.max(trials))
    data_trials = np.zeros((2, 2, n_trials, n_chans, 43000))
    for i_block in range(1, 5):
        block_type = 0 if i_block in [1, 3] else 1
        for i_trial in range(1, n_trials+1):
            mask = np.where(np.logical_and(blocks == i_block, trials == i_trial))[1]
            trial_length = mask.shape[0]
            cond = int(np.unique(data[-1, mask]))
            data_trials[cond, block_type, i_trial - 1, :, :trial_length] = data[:, mask]
    return data_trials


def smooth_moving_average(array, window_size=5):
    """Return the smoothed array where values are averaged in a moving window"""
    box = np.ones(window_size) / window_size
    array_smooth = np.apply_along_axis(lambda m: np.convolve(m, box, mode='valid'), axis=2, arr=array)
    return array_smooth


def moving_variance(array, window_size=15):
    """Return array where values are variance in a moving window"""
    array_var = np.array([np.var(array[i:i+window_size]) for i in range(len(array))])
    return array_var


def get_peak_acc(array):
    """Get peak acceleration of speed array"""
    peak_acc = np.max(np.diff(array, axis=3), axis=3)
    return peak_acc


def plot_speed(speed_array):
    # Plot without the first 5 movements
    plt.plot(speed_array[0, :, :].flatten()[5:], label="slow")
    plt.plot(speed_array[1, :, :].flatten()[5:], label="fast")


def fill_outliers(array):
    idx_outlier = np.where(np.abs(zscore(array)) > 3)[0]
    for idx in idx_outlier:
        if idx < array.shape[0]-1:
            array[idx] = np.mean([array[idx-1], array[idx+1]])
        else:
            array[idx] = np.mean([array[idx - 1], array[idx -2]])
    return array


def get_bids_filepath(root, subject, task, med):
    """Return the filepath with the given specifications, if not existent return None"""

    # Get all datasets for the given subject
    files = BIDSPath(root=root, subject=subject, suffix="ieeg").match()
    # Get the corresponding file
    target_file = None
    for file in files:
        if task in file.basename and med in file.basename and ".vhdr" in file.basename:
            target_file = file
            break
    return target_file


def add_average_channels_electrode(raw):
    """Add channels consisting of the average signals from all contacts on one level of the electrode"""

    ch_names = raw.info["ch_names"]
    new_ch_names = []

    # Average the remaining channels on the same electrode level
    average_channels_list = [
        ["LFP_L_02_STN_MT", "LFP_L_03_STN_MT", "LFP_L_04_STN_MT"],
        ["LFP_L_05_STN_MT", "LFP_L_06_STN_MT", "LFP_L_07_STN_MT"],
        ["LFP_R_02_STN_MT", "LFP_R_03_STN_MT", "LFP_R_04_STN_MT"],
        ["LFP_R_05_STN_MT", "LFP_R_06_STN_MT", "LFP_R_07_STN_MT"],
    ]
    for av_channel in average_channels_list:
        # Check if any of the channels are present in the dataset
        present_chans = [chan for chan in av_channel if chan in ch_names]
        if len(present_chans) > 0:
            # Average them
            new_chan = raw.get_data(present_chans).mean(axis=0)
            # Create new name and info
            new_chan_number = "_".join([chan.split("_")[2] for chan in present_chans])
            new_chan_name = "_".join(present_chans[0].split("_")[:2] + [new_chan_number] + present_chans[0].split("_")[3:])
            info = mne.create_info([new_chan_name], raw.info['sfreq'], ["dbs"])
            # Add channel to raw object
            new_chan_raw = mne.io.RawArray(new_chan[np.newaxis, :], info)
            raw.add_channels([new_chan_raw], force_update_info=True)
            new_ch_names.append(new_chan_name)
    return new_ch_names


def add_bipolar_channels(raw, average_channels):
    """Add all combinations of bipolar channels on one electrode (use the averaged channels added at the end of the dataset)"""

    ch_names = raw.info["ch_names"]
    new_ch_names = []

    # Look over electrode sides
    for side in ["R", "L"]:
        # Get the source channels based on which bipolar channels can be constructed
        source_chans = [chan for chan in average_channels if f"LFP_{side}" in chan]\
                    + [chan for chan in [f"LFP_{side}_01_STN_MT", f"LFP_{side}_08_STN_MT"] if chan in ch_names]

        # Get all combinations
        all_combs = list(itertools.combinations(source_chans, 2))

        # Compute the bipolar channels
        for comb in all_combs:
            new_chan = raw.get_data(comb[0]) - raw.get_data(comb[1])
            new_chan_number_0 = ["".join(comb[0].split("_")[2:-2])]
            new_chan_number_1 = ["".join(comb[1].split("_")[2:-2])]
            new_chan_name = "_".join(comb[0].split("_")[:2] + new_chan_number_0 + new_chan_number_1 + comb[0].split("_")[-2:])
            info = mne.create_info([new_chan_name], raw.info['sfreq'], ["dbs"])
            # Add channel to raw object
            new_chan_raw = mne.io.RawArray(new_chan, info)
            raw.add_channels([new_chan_raw], force_update_info=True)
            new_ch_names.append(new_chan_name)
    return new_ch_names


def get_onset_idx(raw):
    """Return the iindex at which trials start (speed crosses threshold)"""

    speed = raw.get_data(["SPEED"])
    blocks = raw.get_data(["BLOCK"])
    trials = raw.get_data(["TRIAL"])
    n_trials = int(np.max(trials))
    n_blocks = int(np.max(blocks))
    onset_idx = []
    for i_block in range(1, n_blocks+1):
        for i_trial in range(1, n_trials + 1):
            onset_idx.append(np.where(np.logical_and.reduce([blocks == i_block, trials == i_trial, speed > 500]))[1][0])

    return onset_idx


def get_offset_idx(raw):
    """Return the index at which trials ends (speed crosses threshold)"""

    speed = raw.get_data(["SPEED"])
    blocks = raw.get_data(["BLOCK"])
    trials = raw.get_data(["TRIAL"])
    n_trials = int(np.max(trials))
    n_blocks = int(np.max(blocks))
    offset_idx = []
    for i_block in range(1, n_blocks+1):
        for i_trial in range(1, n_trials + 1):
            offset_idx.append(np.where(np.logical_and.reduce([blocks == i_block, trials == i_trial, speed > 500]))[1][-1])

    return offset_idx


def get_peak_idx(raw):
    """Return the index at which trials ends (speed crosses threshold)"""

    speed = raw.get_data(["SPEED"])
    blocks = raw.get_data(["BLOCK"])
    trials = raw.get_data(["TRIAL"])
    n_trials = int(np.max(trials))
    n_blocks = int(np.max(blocks))
    peak_idx = []
    for i_block in range(1, n_blocks+1):
        for i_trial in range(1, n_trials + 1):
            mask = np.where(np.logical_and(blocks == i_block, trials == i_trial))[1]
            peak_idx.append(mask[np.argmax(speed[:, mask])])

    return peak_idx


def add_events(raw, onset_idx, offset_idx, peak_idx):

    n_trials = len(onset_idx)

    # Add the events
    new_events = np.vstack((np.hstack((onset_idx, offset_idx, peak_idx)), np.zeros(n_trials * 3),
                            np.hstack((np.ones(n_trials) * 1, np.ones(n_trials) * 2, np.ones(n_trials) * 3)))).T
    info = mne.create_info(['STI'], raw.info['sfreq'], ['stim'])
    stim_raw = mne.io.RawArray(np.zeros((1, len(raw.times))), info)
    raw.add_channels([stim_raw], force_update_info=True)
    raw.add_events(new_events, stim_channel=None)
    events = mne.find_events(raw, stim_channel='STI')
    return events


def compute_difference_over_time(data):
    """Data: conditionsxblocksxtrialsxsamples"""
    diffs = np.zeros((2,2,95))
    for cond in range(2):
        for block in range(2):
            for trial in range(95):
                diffs[cond, block, trial] = np.mean(np.abs(data[cond, block, trial, :] -
                                                           data[cond, block, trial + 1, :]))
    return diffs
