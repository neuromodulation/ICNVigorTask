# Load and look at neurophysiological data
# Try to filter out the artifact by cutting out the edge artifact and interpolating the values

import mne_bids
import numpy as np
import matplotlib.pyplot as plt
import mne
import gc
import os
import utils.utils as utils
#mne.viz.set_browser_backend('qt')
from mne.time_frequency import tfr_multitaper
import matplotlib
from mne_bids import BIDSPath, read_raw_bids, print_dir_tree, make_report
import utils.utils as utils
from sklearn.datasets import load_digits
from sklearn.decomposition import FastICA
from scipy.stats import zscore
from scipy.signal import detrend

bids_root = r"C:\\Users\\ICN\\Documents\\VigorStim\\Data\\rawdata\\"

# Set subject ID
subject = "EL013"

# Load the dataset
bids_path = BIDSPath(root=bids_root, subject=subject, task="VigorStimR", extension="vhdr", run="1",
                     description="neurobehav", session="EcogLfpMedOff01", acquisition="StimOnB")

raw = read_raw_bids(bids_path=bids_path, verbose=False)
raw.load_data()
sfreq = raw.info["sfreq"]
chans = raw.info["ch_names"]
raw.crop(tmax=raw.tmax-10)

# Get the channels with neurophysiological data
idx_neurophys = mne.pick_types(raw.info, dbs=True, ecog=True)

# Filter the data
raw.notch_filter(50)
raw.filter(l_freq=4, h_freq=100)

# Detrend and demean the data
raw._data[idx_neurophys, :] = detrend(raw._data[idx_neurophys, :], axis=1)
raw._data[idx_neurophys, :] = raw._data[idx_neurophys, :] - np.mean(raw._data[idx_neurophys, :], axis=1)[..., np.newaxis]

# Loop through these channels and remove edge artifact samples
thres = 2*1e-5  # 10 mikrovolt
for idx in idx_neurophys:
    plt.figure()
    chan = raw.get_data([chans[idx]])
    y = np.abs(chan.flatten())
    x = np.arange(len(y)) / sfreq
    plt.plot(x, y.flatten())
    plt.axhline(2*1e-5, color="red")
    plt.axhline(-2 * 1e-5, color="red")
    plt.title(chans[idx])
    #plt.figure()
    idx_noise = y > thres
    idx_noise_2 = np.zeros(len(y))
    n_samps = 30
    for i in range(n_samps, len(y)-n_samps):
        if np.any(y[i - n_samps:i + n_samps] > thres):
            idx_noise_2[i] = 1
        else:
            idx_noise_2[i] = 0
    #plt.plot(x, idx_noise.flatten())
    #plt.plot(x, idx_noise_2)
    plt.title(f"Lost {(np.sum(idx_noise_2)/len(idx_noise_2)) * 100} % of the data")

    # How to fill this??
    # Start with copy pasting the surrounding data
    idx_start = np.where(np.diff(idx_noise_2) == 1)[0]
    idx_stop = np.where(np.diff(idx_noise_2) == -1)[0]
    new_chan = chan.copy()
    for (i_s, i_e) in zip(idx_start, idx_stop):
        dur = i_e - i_s
        #plt.axvline(i_s/sfreq, color="red")
        #plt.axvline(i_e/sfreq, color="red")
        #plt.plot(x,idx_noise_2)

        prev = np.int(np.floor((dur/2)))
        post = np.int(np.ceil((dur/2)))
        new_chan[:, i_s:i_s+prev] = chan[:, i_s-prev-10:i_s-10]
        new_chan[:, i_s+prev:i_e] = chan[:, i_e+10:i_e + post+10]
        #plt.plot(x, new_chan.flatten())

    plt.plot(x, new_chan.flatten())
    plt.show()
    #np.where(y > 3)
    # Remove the samples
    plt.show()
