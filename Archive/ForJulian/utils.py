# Collection of helper function

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import zscore
from mne_bids import BIDSPath
import mne
import itertools
from typing import Sequence


def plot_conds(array, var=None):
    """array = (conds x blocks x trials)
    Plot data divided into two conditions, if given add the variance as shaded area"""
    # Plot without the first 5 movements
    plt.plot(array[0, :, :].flatten()[5:], label="slow", color="blue", linewidth=3)
    plt.plot(array[1, :, :].flatten()[5:], label="fast", color="red", linewidth=3)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    # Add line at 0
    plt.axhline(0, linewidth=2, color="black")
    x = np.arange(len(array[0, :, :].flatten()[5:]))
    # add variance as shaded area
    if var is not None:
        plt.fill_between(x, array[0, :, :].flatten()[5:] - var[0, :, :].flatten()[5:], array[0, :, :].flatten()[5:] + var[0, :, :].flatten()[5:]
                         , color="blue", alpha =0.5)
        plt.fill_between(x, array[1, :, :].flatten()[5:] - var[1, :, :].flatten()[5:],
                         array[1, :, :].flatten()[5:] + var[1, :, :].flatten()[5:]
                         , color="red", alpha=0.5)


def fill_outliers(array):
    """Fill outliers in 1D array using the mean of surrounding non-outliers"""
    # Get index of outliers
    idx_outlier = np.where(np.abs(zscore(array)) > 3)[0]
    idx_non_outlier = np.where(np.abs(zscore(array)) <= 3)[0]
    # Fill each outlier with mean of closest non outlier
    for idx in idx_outlier:
        # Get index of the closest non-outlier before and after
        where_before = np.where(idx_non_outlier < idx)[0]
        where_after = np.where(idx_non_outlier > idx)[0]
        if len(where_before) > 0 and len(where_after) > 0:  # Middle sample
            array[idx] = np.mean([array[idx_non_outlier[where_before[-1]]], array[idx_non_outlier[where_after[0]]]])
        elif len(where_before) == 0 and len(where_after) > 0:  # First sample
            array[idx] = np.mean([array[idx_non_outlier[where_after[1]]], array[idx_non_outlier[where_after[0]]]])
        elif len(where_before) > 0 and len(where_after) == 0:  # Last sample
            array[idx] = np.mean([array[idx_non_outlier[where_before[-2]]], array[idx_non_outlier[where_before[-1]]]])
    return array


def norm_perc(array):
    """Normalize feature to stimulation block start (mean of trial 5-10) and return as percentage"""
    mean_start = np.mean(array[..., 0, 5:10], axis=-1)[..., np.newaxis, np.newaxis]
    array_norm_perc = ((array - mean_start) / mean_start) * 100
    return array_norm_perc


def smooth_moving_average(array, window_size=5, axis=2):
    """Return the smoothed array where values are averaged in a moving window along the given axis"""
    box = np.ones(window_size) / window_size
    array_smooth = np.apply_along_axis(lambda m: np.convolve(m, box, mode='valid'), axis=axis, arr=array)
    return array_smooth


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


def moving_variance(array, window_size=15):
    """Return array where values are variance in a moving window"""
    array_var = np.array([np.var(array[i:i+window_size]) for i in range(len(array))])
    return array_var


def get_slow_fast(array, cond):
    """Return array indicating if move is slow/fast (depending on cond)"""
    res = np.zeros((2, 96))
    for block in range(2):
        for trial in range(2, 96):
            diff = array[block, trial - 2:trial] - array[block, trial]
            if cond == "slow" and np.all(diff > 0) :
                res[block, trial] = 1
            if cond == "fast" and np.all(diff < 0) :
                res[block, trial] = 1
    return res


def get_peak_acc(array):
    """Get peak acceleration of speed array"""
    peak_acc = np.max(np.diff(array, axis=3), axis=3)
    return peak_acc


def get_move_dur(array):
    """Compute the movement duration for each movement"""
    onset_idx = np.apply_along_axis(lambda m: np.where(m > 300)[0][0], axis=3, arr=array[:, :, :, 0, :])
    offset_idx = np.apply_along_axis(lambda m: np.where(m == 1)[0][0], axis=3, arr=array[:, :, :, 1, :])
    dur_array = offset_idx - onset_idx
    return dur_array


def get_RT(array):
    """Compute the reaction time for each movement (time of movement onset)"""
    onset_array = np.apply_along_axis(lambda m: np.where(m > 300)[0][0], axis=3, arr=array)
    return onset_array


def get_tortu(array):
    """Compute the tortuosity of each movement"""
    # Get the position of the target for each movement
    target_x = np.apply_along_axis(lambda m: np.unique(m)[np.unique(m) > 0][0], axis=3, arr=array[:, :, :, 2, :])
    target_y = np.apply_along_axis(lambda m: np.unique(m)[np.unique(m) > 0][0], axis=3, arr=array[:, :, :, 3, :])
    # Get start position
    start_x = np.apply_along_axis(lambda m: m[0], axis=3, arr=array[:, :, :, 0, :])
    start_y = np.apply_along_axis(lambda m: m[0], axis=3, arr=array[:, :, :, 1, :])
    # Compute the shortest path from start to target
    path_min = np.sqrt((target_x - start_x)**2 + (target_y - start_y)**2)
    # Compute the actual path
    path_x = np.sum(np.diff(array[:, :, :, 0, :]), axis=3)
    path_y = np.sum(np.diff(array[:, :, :, 1, :]), axis=3)
    path = np.sqrt(path_x**2 + path_y**2)
    # Compute teh tortuosity
    tortuosity = path/path_min
    return tortuosity


def align_move_onset(array, threshold=300):
    """Align speed array to movement onset defines by thresholf"""
    start_idx = np.where(array > threshold)[0][0]
    array_tmp = array[start_idx:]
    new_array = np.zeros(array.shape)
    new_array[:len(array_tmp)] = array_tmp
    return new_array


def get_variability_old(array, window=5):
    """Compute variability of movements over time, moving window with 10 moves per window"""
    # Align onset of movements
    array = np.apply_along_axis(lambda m: align_move_onset(m), axis=3, arr=array)
    # Compute median variance over a set of movements
    var_array = np.zeros((2, 2, 95-window))
    for trial in range(95-window):
        var_array[:, :, trial] = np.mean(np.var(array[:, :, trial:trial+window, :500], axis=2), axis=2)
    return var_array


def get_variability(array, window=5):
    """Compute variability of movements over time, moving window with 10 moves per window"""
    # Align onset of movements
    array = np.apply_along_axis(lambda m: align_move_onset(m), axis=3, arr=array)
    # Compute median variance over a set of movements
    var_array = np.zeros((2, 2, 95))
    for trial in range(95):
        var_array[:, :, trial] = np.mean(np.abs(array[:, :, trial,:1000] - array[:, :, trial+1,:1000]), axis=2)
    return var_array


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


