import matplotlib.pyplot as plt
import mne
from scipy.io import loadmat, savemat
from scipy.stats import zscore
import numpy as np
from scipy.signal import detrend

# Add synchronized behavioral data to brain vision file

# Load the TMSi data
filename = "C:\\Users\\alessia\\Documents\\Jobs\\ICN\\vigor-stim\\Data\\Parkinson_Pilot\\Neuro data\\sub-03-MedOff-task-VigorStim-R-Fast-Slow-StimOn-run-01-neuro\\ieeg\\sub-526RI66_ses-EphysMedOff02_task-VigorStimR_acq-StimOn_run-01_ieeg.vhdr"
raw_data = mne.io.read_raw_brainvision(filename, preload=True)

# Load the MATLAB data
filename = "C:\\Users\\alessia\\Documents\\Jobs\\ICN\\vigor-stim\\Data\\Parkinson_Pilot\\data_sub-03-MedOff-task-VigorStim-R-Fast-Slow-StimOn-run-01-behavioral.mat"
behav_data = loadmat(filename)
behav_data = behav_data["behav_data"]

# Downsample the neuro data to 500
raw_data.resample(500)

# Delete zero entries from behavioral data (used for averaging at beginning of trial)
idx_zeros = np.where(np.mean(behav_data,axis=1) == 0)[0]
behav_data = np.delete(behav_data,idx_zeros,axis=0)

# Get the times of the samples
time_array_neuro = raw_data.times.flatten()

# Get the time of first stimulation

# Get a channel based on which the onset is determined
target_chan = raw_data.get_data(["LFP_R_1_STN_MT"]).flatten()
# Plot for visual inspection
plt.plot(target_chan)
#plt.show()
# Find the first sample above a threshold
idx_onset_neuro = np.where(np.abs(zscore(target_chan)) > 0.5)[0][0]
# Plot for visual inspection
plt.plot(target_chan)
plt.axvline(idx_onset_neuro,color="red")
#plt.show()

# Find the first sample with stimulation in the behavioral data
behav_data_stim = behav_data[:,10].flatten()
idx_onset_behav = np.where(behav_data_stim == 1)[0][0]

# Get time in sec at which stimulation onsets occur
time_onset_neuro = time_array_neuro[idx_onset_neuro]
time_array_behav = behav_data[:,2].flatten()
time_onset_behav = time_array_behav[idx_onset_behav]

# Substract the time difference from the neuro data (neuro recording alsways starts first)
diff_time = time_onset_neuro - time_onset_behav
time_array_neuro = time_array_neuro - diff_time

# Visually check the alignment
# Get indexes of stimulation onset in behav data
idx_stim = np.where(np.diff(behav_data_stim) == 1)[0]
plt.plot(time_array_neuro, target_chan)
for idx in idx_stim:
    plt.axvline(time_array_behav[idx],color="red")
#plt.show()

# Delete the neuro samples that come before or after the behav data
idx_neuro_delete = np.where(np.logical_or(time_array_neuro < 0,time_array_neuro > np.max(time_array_behav)))
time_array_neuro = np.delete(time_array_neuro, idx_neuro_delete)
target_chan = np.delete(target_chan, idx_neuro_delete)

# For every sample in the neuro data find the closest sample in the behav data
n_cols = np.size(behav_data,1)
behav_data_long = np.zeros((len(time_array_neuro), n_cols))
for i,time_samp in enumerate(time_array_neuro):
    # Get the sample that is closest in time
    idx_samp_behav = np.argmin(np.abs(time_array_behav - time_samp))
    behav_data_long[i,:] = behav_data[idx_samp_behav,:]

# Get the whole neuro dataset
neuro_data = raw_data._data
# Delete the part before and after the behavioral task
neuro_data = np.delete(neuro_data, idx_neuro_delete, axis=1)
# Concatenate the data
neuro_behav_data = np.vstack((neuro_data, behav_data_long.T))
# Save it together
raw_data._data = neuro_behav_data
# Add channel names

# Another visual inspection
plt.plot(behav_data_long[:,10]*np.mean(target_chan))
plt.plot(target_chan)

print("h")