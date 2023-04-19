# Load and look at neurophysiological data
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

bids_root = r"C:\\Users\\ICN\\Documents\\VigorStim\\Data\\rawdata\\"

# Set subject ID
subject = "EL013"

# Load the dataset
bids_path = BIDSPath(root=bids_root, subject=subject, task="VigorStimR", extension="vhdr", run="1",
                     description="neurobehav", session="EcogLfpMedOff01", acquisition="StimOnB")

raw = read_raw_bids(bids_path=bids_path, verbose=False)
raw.load_data()
sfreq = raw.info["sfreq"]

# Filter the data
raw.filter(l_freq=10, h_freq=40)

# Inspect raw data
#raw.plot(block=True)

# Remove line noise
raw.notch_filter(50)

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
n_stim = len(stim_idx)
onset = (stim_idx / sfreq) - 0.4
duration = np.repeat(1.1, n_stim)
annot = mne.Annotations(onset, duration, ['bad stim'] * n_stim,
                                  orig_time=raw.info['meas_date'])
raw.set_annotations(annot)
print(raw.annotations)
raw.plot(block=True)

#for i in stim_idx:
#    plt.axvline(i, color="red")

# Compute beta power in each block (without the annotated stimulation periods)


plt.show()



