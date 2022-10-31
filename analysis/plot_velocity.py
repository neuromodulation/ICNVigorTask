# Script to plot the velocity of one dataset
# TODO Plot average speed --> until museum
# After museum: Start new analysis and do list 

import numpy as np
import matplotlib.pyplot as plt
import mne
import easygui
from ICNVigorTask.utils.utils import reshape_data_trials, norm_speed, smooth_moving_average, plot_speed

# Load the dataset of interest
filename_neuro = 'D:\\rawdata\\rawdata\\sub-015\\sub-015\\ses-EcogLfpMedOn01\\ieeg\\sub-015_ses-EcogLfpMedOn01_task-VigorStimR_acq-StimOnB_run-1_ieeg_behav.vhdr'
#filename_neuro = easygui.fileopenbox(default="*.vhdr")
raw_data = mne.io.read_raw_brainvision(filename_neuro, preload=True)

# Get the channel index of the mean speed values
mean_speed_idx = raw_data.info["ch_names"].index("mean_vel")

# Structure data in trials and blocks
data = reshape_data_trials(raw_data)

# Extract the peak speed of all trials
peak_speed = np.max(data[:, :, :, mean_speed_idx, :], axis=3)

# Normalize them to the start speed
peak_speed = norm_speed(peak_speed)

# Print the peak velocities
#plt.plot(peak_speed[0, :, :].flatten(), label="slow")
#plt.plot(peak_speed[1, :, :].flatten(), label="fast")
#plt.legend()
#plt.show()

# Smooth the speed values
peak_speed_smooth = smooth_moving_average(peak_speed)
plot_speed(peak_speed_smooth)
plt.legend()
plt.show()