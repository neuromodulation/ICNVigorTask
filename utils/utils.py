import numpy as np


def norm_0_1(array):
    """Return array normalized to values between 0 and 1"""
    return (array - np.min(array)) / (np.max(array - np.min(array)))

def reshape_data_trials(raw_data, slow_first):
    """Gives back the data in a array format reshaped in trials
    shape [2, 2, 2, 32, n_chans, 50000]
    2 conditions = slow - fast (always this order)
    2 blocks per condition = stimulation - recovery
    32 trials per block
    50000 = standard trial length, filled with 0s if trial is shorter """
    blocks = raw_data.get_data(["block"])
    trials = raw_data.get_data(["trial"])
    data = raw_data._data
    n_chans = data.shape[0]
    data_trials = np.zeros((2, 2, 32, n_chans, 50000))
    for i_block in range(1, 5):
        cond = 0 if slow_first == 1 and i_block in [0, 1] or slow_first == 0 and i_block in [2, 3] else 1
        block_type = 0 if i_block in [0, 2] else 1
        for i_trial in range(1, 33):
            mask = np.where(np.logical_and(blocks == i_block, trials == i_trial))[1]
            trial_length = mask.shape[0]
            data_trials[cond, block_type, i_trial - 1, :, :trial_length] = data[:, mask]
    return data_trials