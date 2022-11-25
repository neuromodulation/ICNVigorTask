import matplotlib.pyplot as plt
import mne
from scipy.io import loadmat, savemat
from scipy.stats import zscore
import numpy as np
import pandas as pd
import easygui
from ICNVigorTask.utils.utils import norm_0_1

# Add synchronized behavioral data to brain vision file

# Load the TMSi data
filename_neuro = easygui.fileopenbox(default="*.vhdr")
#filename_neuro = "D:\\rawdata\\rawdata\\sub-015\\sub-015\\ses-EcogLfpMedOn01\\ieeg\\sub-015_ses-EcogLfpMedOn01_task-VigorStimR_acq-StimOnB_run-1_ieeg.vhdr"
raw_data = mne.io.read_raw_brainvision(filename_neuro, preload=True)

# Load the MATLAB data
filename_behav = easygui.fileopenbox(default="*.mat")
#filename_behav = "D:\\rawdata\\rawdata\\sub-015\\sub-014-MedOn-task-VigorStim-R-Fast-Slow-StimOn-run-01-behavioral.mat"
behav_data = loadmat(filename_behav)
# Extract the behavioral data stored in a matrix
behav_data = behav_data["struct"][0][0][1]
# Determine the condition based on the filename
slow_first = 1 if filename_behav.index("Slow") < filename_behav.index("Fast") else 0

# Downsample the neuro data to 500 Hz
raw_data.resample(500)

# Get the times of the samples
time_array_neuro = raw_data.times.flatten()

# Get a LFP channel based on which stimulation onset is determined
# based on saved bads?
# FIX THIS
target_chan_name = "LFP_L_05_STN_MT"
target_chan = raw_data.get_data([target_chan_name]).flatten()

# Plot for visual inspection
plt.plot(target_chan)
plt.show()

# Find the first sample above a threshold
idx_onset_neuro = np.where(np.abs(zscore(target_chan[:-10])) > 3)[0][0]

# Plot for visual inspection
plt.plot(target_chan)
plt.axvline(idx_onset_neuro, color="red")
plt.show()

# Find the first sample with stimulation in the behavioral data
behav_data_stim = behav_data[:, 10].flatten()
idx_onset_behav = np.where(behav_data_stim == 1)[0][0]

# Get time in sec at which stimulation onsets occur
time_onset_neuro = time_array_neuro[idx_onset_neuro]
time_array_behav = behav_data[:, 2].flatten()
time_onset_behav = time_array_behav[idx_onset_behav]

# Substract the time difference from the neuro data (neuro recording alsways starts first)
diff_time = time_onset_neuro - time_onset_behav
time_array_neuro = time_array_neuro - diff_time

# Get indexes of stimulation onset in behav data and visually check the alignment
idx_stim = np.where(np.diff(behav_data_stim) == 1)[0]
plt.plot(time_array_neuro, target_chan)
for idx in idx_stim:
    plt.axvline(time_array_behav[idx], color="red")
plt.show()

# For every sample in the neuro data find the closest sample in the behav data
n_cols = np.size(behav_data, 1)
behav_data_long = np.zeros((len(time_array_neuro), n_cols))
for i, time_samp in enumerate(time_array_neuro):
    # If neuro sample is before or after onset of behav recording, save zeros
    if time_samp < 0 or time_samp > np.max(time_array_behav):
        behav_data_long[i, :] = np.zeros(16)
    else:
        # Get the sample that is closest in time
        idx_samp_behav = np.argmin(np.abs(time_array_behav - time_samp))
        behav_data_long[i,:] = behav_data[idx_samp_behav,:]

# Add a channel containing the condition
cond = [0 if i in [1, 2] and slow_first or i in [3, 4] and not slow_first else 1 for i in behav_data_long[:, 7]]
behav_data_long = np.hstack((behav_data_long, np.array(cond)[:, np.newaxis]))

# Select channels that should be saved
behav_data_long = behav_data_long[:, [0,1,3,4,7,8,9,10,11,12,16]]

# Add behavioral channels to the raw mne object
ch_names = ["PEN_X", "PEN_Y", "SPEED_MEAN", "SPEED", "BLOCK", "TRIAL", "TARGET_X", "TARGET_Y", "TARGET", "STIMULATION", "STIM_CONDITION"]
info = mne.create_info(ch_names, raw_data.info['sfreq'], ["bio"]*len(ch_names))
behav_raw = mne.io.RawArray(behav_data_long.T, info)
raw_data.add_channels([behav_raw], force_update_info=True)

# Final plot for visual inspection
target_chans = raw_data.get_data([target_chan_name, "STIMULATION"])
plt.plot(norm_0_1(target_chans[0, :-10]).T)
plt.plot(target_chans[1,:-10].T)
plt.show()

# Save new brain vision file
mne.export.export_raw(fname=filename_neuro, raw=raw_data, fmt="brainvision", overwrite=True)

# Add channels to corresponding tsv file
tsv_filename = filename_neuro[:-4]+"tsv"
tsv_file = pd.read_csv(tsv_filename, sep='\t')
template = tsv_file.loc[len(tsv_file)-1]
template[-1] = "Task"
template[-2] = "Task"
for ch_name in ch_names:
    new_row = template.copy()
    new_row[0] = ch_name
    tsv_file = tsv_file.append(new_row)
# Update the sampling frequency
tsv_file.sampling_frequency = np.ones(len(tsv_file)) * 500
tsv_file.high_cutoff = np.ones(len(tsv_file)) * 250
# Save updated tsv file
with open(tsv_filename,'w') as write_tsv:
    write_tsv.write(tsv_file.to_csv(sep='\t', index=False))

print("Successfully added behavioral data")
