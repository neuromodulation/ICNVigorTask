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

bids_root = r"C:\\Users\\ICN\\Documents\\VigorStim\\Data\\rawdata\\"

# Set subject ID
subject = "EL013"

# Load the dataset
bids_path = BIDSPath(root=bids_root, subject=subject, task="VigorStimR", extension="vhdr", run="1",
                     description="neurobehav", session="EcogLfpMedOff01", acquisition="StimOnB")

raw = read_raw_bids(bids_path=bids_path, verbose=False)
raw.load_data()
sfreq = raw.info["sfreq"]
raw.crop(tmax=raw.tmax-10)

# Add bipolar channel
new_chan = np.diff(raw.get_data(["ECOG_R_04_SMC_AT", "ECOG_R_05_SMC_AT"]), axis=0)
# Add bipolar channel
new_chan = raw.get_data(["ECOG_R_04_SMC_AT"]) - raw.get_data(["ECOG_R_03_SMC_AT"]) * 0.5 - raw.get_data(["ECOG_R_05_SMC_AT"])*0.5
# Create new name and info
new_chan_name = "bipolar_4_5"
info = mne.create_info([new_chan_name], raw.info['sfreq'], ["dbs"])
# Add channel to raw object
new_chan_raw = mne.io.RawArray(new_chan, info)
raw.add_channels([new_chan_raw], force_update_info=True)

# Filter the data
raw.notch_filter(130)
# Remove line noise
raw.notch_filter(50)
raw.filter(l_freq=20, h_freq=40)

X, _ = load_digits(return_X_y=True)
X = raw.get_data(["ECOG_R_04_SMC_AT", "ECOG_R_05_SMC_AT", "ECOG_R_01_SMC_AT", "ECOG_R_02_SMC_AT", "ECOG_R_03_SMC_AT", "ECOG_R_06_SMC_AT"]).T
transformer = FastICA(n_components=6, random_state=0, whiten='unit-variance')
X_transformed = transformer.fit_transform(X)
X_transformed.shape
plt.subplot(1, 2, 1)
for i in range(6):
    plt.plot(X[:, i].flatten())
plt.figure()
for i in range(6):
    plt.subplot(6, 1, i+1)
    plt.plot(X_transformed[:, i].flatten())
plt.show()


# Add bipolar channel
new_chan = X_transformed[:, 2]
# Create new name and info
new_chan_name = "ICA"
info = mne.create_info([new_chan_name], raw.info['sfreq'], ["dbs"])
# Add channel to raw object
new_chan_raw = mne.io.RawArray(new_chan[np.newaxis,:], info)
raw.add_channels([new_chan_raw], force_update_info=True)


# Inspect raw data
#raw.plot(block=True)

# Inspect power spectral density
#raw.compute_psd(tmin=raw.tmax-130, tmax=raw.tmax-30, fmin=1, fmax=80, n_fft=int(sfreq*1)).plot()
#plt.show()

# Inspect the behavioral data
plt.subplot(3, 1, 1)
spead_mean = raw.get_data(["SPEED_MEAN"])
plt.plot(spead_mean.flatten()[:])
plt.subplot(3, 1, 2)
stim_cond = raw.get_data(["STIM_CONDITION"])
plt.plot(stim_cond.flatten()[:])
plt.subplot(3, 1, 3)
stim = raw.get_data(["STIMULATION"])
plt.plot(stim.flatten()[:]*0.005)
plt.subplot(3, 1, 3)
lfp = raw.get_data(["LFP_L_01_STN_MT"])
plt.plot(lfp.flatten()[:])
plt.close()
#plt.show()

# Get onset, offset, peak events
onset_idx = utils.get_onset_idx(raw)
offset_idx = utils.get_offset_idx(raw)
peak_idx = utils.get_peak_idx(raw)
stim_idx = utils.get_stim_idx(raw)

# Extract whether it was slow/fast or fast/slow
slow_first = 1 if stim_cond[0, 0] == 0 else 0

# Get onset of stimulation and recovery blocks
slow_stim = [onset_idx[0], offset_idx[96]]
slow_recovery = [onset_idx[96], offset_idx[96*2]]
fast_stim = [onset_idx[96*2], offset_idx[96*3]]
fast_recovery = [onset_idx[96*3], offset_idx[96*4-1]]

# Add stimulation periods to raw object as annotation
"""
n_stim = len(stim_idx)
onset = (stim_idx / sfreq) - 0.4
duration = np.repeat(1.1, n_stim)
annot = mne.Annotations(onset, duration, ['bad stim'] * n_stim,
                                  orig_time=raw.info['meas_date'])"""

# Add stimulation periods to raw object as annotation
n_stim = len(onset_idx)
onset = (np.array(onset_idx) / sfreq) - 0.2
duration = np.repeat(0.4, n_stim)
annot = mne.Annotations(onset, duration, ['bad stim'] * n_stim,
                                  orig_time=raw.info['meas_date'])
raw_inspect = raw.copy()
raw_inspect.set_annotations(annot)
print(raw_inspect.annotations)
#raw_inspect.plot(block=True)
#plt.show()

#for i in stim_idx:
#    plt.axvline(i, color="red")

# Compute beta power at start, peak and end of movements
# Use only not stimulated movements

# Check
"""
plt.figure()
lfp = raw.get_data(["bipolar_4_5"])
plt.plot(lfp.flatten()[:])
for i in onset_idx[-190:]:
    plt.axvline(i, color="red")
    plt.axvline(i+100, color="blue")
    plt.axvline(i-100, color="green")
plt.figure()
for i in range(190):
    plt.plot(x[i,:,:].flatten())
    
    """

# Create events array from onset_idx
channel = 'ICA' #"bipolar_4_5"# "LFP_L_01_STN_MT" # or "bipolar_4_5"

# Plot in one plot
fig, axes1 = plt.subplots(nrows=3, ncols=3)
fig2, axes2 = plt.subplots(nrows=1, ncols=3)
for i, idx in enumerate([offset_idx, peak_idx, onset_idx]):
    idx = np.hstack((idx[96:96*2], idx[96*3:]))
    idx = idx[:96]
    n_moves = len(idx)
    events = np.stack((idx, np.zeros(n_moves), np.ones(n_moves))).T
    epochs_onset = mne.Epochs(raw, events=events.astype(int), event_id=1, tmin=-0.6, tmax=0.6)
    x = epochs_onset.get_data([channel])

    epochs_onset.plot_image(picks=[channel], axes=axes1[:, i], show=False)

    # Inspect power
    #epochs_onset.plot_psd(fmin=10, fmax=40, average=True)

    frequencies = np.arange(4, 50, 1)
    power = mne.time_frequency.tfr_morlet(epochs_onset, n_cycles=2, return_itc=False,
                                          freqs=frequencies, decim=3)
    power.plot([channel], axes=axes2[i], show=False)#, baseline=(-0.6, 0.6))
beta_fast = np.mean(power.data[-1, 15:35, :], axis=0)


fig, axes1 = plt.subplots(nrows=3, ncols=3)
fig2, axes2 = plt.subplots(nrows=1, ncols=3)
for i, idx in enumerate([peak_idx, offset_idx, onset_idx]):
    #idx = np.hstack((idx[96:96*2], idx[96*3:]))
    idx = idx[96*2:96*3]
    n_moves = len(idx)
    events = np.stack((idx, np.zeros(n_moves), np.ones(n_moves))).T
    epochs_onset = mne.Epochs(raw, events=events.astype(int), event_id=1, tmin=-0.6, tmax=0.6)
    x = epochs_onset.get_data([channel])

    epochs_onset.plot_image(picks=[channel], axes=axes1[:, i], show=False)

    # Inspect power
    #epochs_onset.plot_psd(fmin=10, fmax=40, average=True)

    frequencies = np.arange(4, 50, 1)
    power = mne.time_frequency.tfr_morlet(epochs_onset, n_cycles=2, return_itc=False,
                                          freqs=frequencies, decim=3)
    power.plot([channel], axes=axes2[i], show=False)#, baseline=(-0.6, 0.6))
beta_slow = np.mean(power.data[-1, 15:35, :], axis=0)
#plt.show()

# Plot average beta power over time around peak
plt.figure()
plt.plot(beta_fast, label="Fast")
plt.plot(beta_slow, label="Slow")
plt.legend()
plt.show()
print("hu")
