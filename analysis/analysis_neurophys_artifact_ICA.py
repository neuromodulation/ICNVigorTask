# Load and look at neurophysiological data
# Try to filter out the artifact

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

bids_root = r"C:\\Users\\ICN\\Documents\\VigorStim\\Data\\rawdata\\"

# Set subject ID
subject = "EL014"

# Load the dataset
bids_path = BIDSPath(root=bids_root, subject=subject, task="VigorStimR", extension="vhdr", run="1",
                     description="neurobehav", session="EcogLfpMedOff01", acquisition="StimOnB")

raw = read_raw_bids(bids_path=bids_path, verbose=False)
raw.load_data()
sfreq = raw.info["sfreq"]
ch_names = np.array(raw.info["ch_names"])
raw.crop(tmax=raw.tmax-10)
idx_dbs = mne.pick_types(raw.info, dbs=True)
idx_ecog = mne.pick_types(raw.info, ecog=True)

# Filter the data
raw.notch_filter(130)
# Remove line noise
raw.notch_filter(50)
raw.filter(l_freq=4, h_freq=100)

for idx in [idx_dbs, idx_ecog]:
    X = raw.get_data(ch_names[idx]).T
    transformer = FastICA(n_components=len(idx), random_state=0, whiten='unit-variance')
    X_transformed = transformer.fit_transform(X)
    plt.figure(figsize=(12, 12))
    for i in range(len(idx)):
        plt.subplot(len(idx), 1, i+1)
        plt.plot(np.abs(zscore(X_transformed[:, i].flatten())))
        plt.axhline(15, color="red")
    # Select channels as bad that have z-scores above 15
    X_trans_new = X_transformed.copy()
    for chan in range(len(idx)):
        if np.any(np.abs(zscore(X_transformed[:, chan])) > 15):
            X_trans_new[:, chan] = np.zeros(X_trans_new[:, chan].shape)
    # Project back
    X_new = transformer.inverse_transform(X_trans_new)
    # Inspect
    plt.figure(figsize=(12, 12))
    for i in range(len(idx)):
        plt.subplot(len(idx), 1, i + 1)
        plt.plot(X[:, i].flatten())
        plt.plot(X_new[:, i].flatten())
    plt.show()
print("h")
