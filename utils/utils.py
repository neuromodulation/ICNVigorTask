import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import zscore

def norm_0_1(array):
    """Return array normalized to values between 0 and 1"""
    return (array - np.min(array)) / (np.max(array - np.min(array)))


def norm_speed(array):
    """Normalize speed to stimulation block start
    array: (2x2x96)(Conditions, Blocks, Trials)"""
    # Substract the mean of the first 5 movements in each stimulation block from the speed of the subsequent stimulation
    # and recovery block
    array_norm = array - np.mean(array[:, 0, :5], axis=1)[:, np.newaxis, np.newaxis]
    return array_norm


def norm_perf_speed(array):
    """Normalize speed to stimulation block start and return as percentage
    array: (2x2x96)(Conditions, Blocks, Trials)"""
    mean_start = np.mean(array[:, 0, :10], axis=1)[:, np.newaxis, np.newaxis]
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
    data = raw_data._data
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


def plot_speed(speed_array):
    plt.plot(speed_array[0, :, :].flatten(), label="slow")
    plt.plot(speed_array[1, :, :].flatten(), label="fast")


def fill_outliers(array):
    idx_outlier = np.where(np.abs(zscore(array)) > 3)[0]
    for idx in idx_outlier:
        if idx < array.shape[0]-1:
            array[idx] = np.mean([array[idx-1], array[idx+1]])
        else:
            array[idx] = np.mean([array[idx - 1], array[idx -2]])
    return array