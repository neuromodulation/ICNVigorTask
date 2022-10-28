# Script to plot the velocity of one dataset

import numpy as np
import matplotlib.pyplot as plt
import mne
import easygui
from ICNVigorTask.utils.utils import reshape_data_trials

# Load the dataset of interest
filename_neuro = "C:\\Users\\alessia\\Documents\\Jobs\\ICN\\vigor-stim\\Data\Archive\\archive_ICN_data\\Parkinson_Pilot\\Neuro data\\sub-06-MedOff-task-VigorStim-R-Fast-Slow-StimOn-run-01-neuro\sub-008_ses-EphysMedOff01_task-VigorStimR_acq-StimOn_run-01_ieeg_behav.vhdr"
#filename_neuro = easygui.fileopenbox(default="*.vhdr")
raw_data = mne.io.read_raw_brainvision(filename_neuro, preload=True)

# Determine the condition based on the filename
slow_first = 1 if filename_neuro.index("Slow") < filename_neuro.index("Fast") else 0

# Get the channel index of the mean velocity values
mean_vel_idx = raw_data.info["ch_names"].index("mean_vel")

# Structure data in trials and blocks
data = reshape_data_trials(raw_data, slow_first)

# Extract the peak velocity of all trials
peak_vels = np.max(data[:, :, :, mean_vel_idx, :], axis=3)

# Print the peak velocities
plt.plot(peak_vels[0, :, :].flatten(), label="slow")
plt.plot(peak_vels[1, :, :].flatten(), label="fast")
plt.legend()
plt.show()
print("h")

# Normalize peak velocities
peak_vels_norm = peak_vels - np.mean(peak_vels[:, 0, 5:10], axis=1)[:, np.newaxis, np.newaxis]
plt.plot(peak_vels_norm[0, :, :].flatten(), label="slow")
plt.plot(peak_vels_norm[1, :, :].flatten(), label="fast")
plt.legend()
plt.show()

# DONE: I can really start next week
# TODO: Put together data this weekend
# Monday: Write list for analysis
# Python is ready
