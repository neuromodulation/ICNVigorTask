# Script for change in speed over time (percentage & cumulative)
# With bids loading

import numpy as np
import matplotlib.pyplot as plt
import mne
import easygui
import gc
import os
from ICNVigorTask.utils.utils import reshape_data_trials, norm_speed, smooth_moving_average, plot_speed, \
    fill_outliers, norm_perf_speed, norm_0_1
from mne_bids import BIDSPath, read_raw_bids, print_dir_tree, make_report

bids_root = "C:\\Users\\alessia\\Documents\\Jobs\\ICN\\vigor-stim\\Data\\rawdata\\" # op.join(op.dirname(sample.data_path()), dataset)

# Set analysis parameters
plot_individual = True
subject_list = ["EL006", "EL007", "EL008", "EL012", "EL03", "EL014", "EL015", "EL016",
                "L001", "L002", "L003", "L005", "L006", "L007", "L008"]

# Plot the speed of all datasets
peak_speed_all = []
peak_speed_cum_all = []
for subject in subject_list:

    # Read one dataset from every participant
    for task_name in ["VigorStimR", "VigorStimL"]:
        if subject in ["EL012", "L001"]:
            bids_match = BIDSPath(root=bids_root, suffix="ieeg", subject=subject, task=task_name, description="behav").match()
        else:
            bids_match = BIDSPath(root=bids_root, suffix="ieeg", subject=subject, task=task_name, description="neurobehav").match()
        if len(bids_match) > 0:
            file_path = bids_match[1]
            # Loop through dataset to get the Off dataset
            for bids_m in bids_match[1::2]:
                if "Off" in bids_m.basename:
                    file_path = bids_m

    # Load the dataset of interest
    raw = read_raw_bids(bids_path=file_path, verbose=False)

    # Get the channel index of the mean speed values
    mean_speed_idx = raw.info["ch_names"].index("SPEED_MEAN")

    # Structure data in trials and blocks
    data = reshape_data_trials(raw)

    # Extract the peak speed of all trials
    peak_speed = np.max(data[:, :, :, mean_speed_idx, :], axis=3)
    del data
    gc.collect()

    # Detect and fill outliers (e.g. when subject did not touch the screen)
    np.apply_along_axis(lambda m: fill_outliers(m), axis=2, arr=peak_speed)
    np.apply_along_axis(lambda m: fill_outliers(m), axis=2, arr=peak_speed)

    # Normalize them to the start speed
    peak_speed = norm_perf_speed(peak_speed)

    # Compute the cumulative change in peak speed
    peak_speed_cum = np.cumsum(peak_speed, axis=2)
    peak_speed_cum[:,1,:] += peak_speed_cum[:,0,-1][:, np.newaxis]

    # Plot if needed
    if plot_individual:
        plt.figure()
        plt.subplot(1,2,1)
        plot_speed(smooth_moving_average(peak_speed))
        plt.subplot(1,2,2)
        plot_speed(peak_speed_cum)
        plt.legend()
        plt.suptitle(file_path.basename.split("\\")[0])

    # Save the speed values for all datasest
    peak_speed_all.append(peak_speed)
    peak_speed_cum_all.append(peak_speed_cum)

# Average over all datasets
peak_speed_all = np.array(peak_speed_all)
mean_peak_speed = np.mean(peak_speed_all, axis=0)
peak_speed_cum_all = np.array(peak_speed_cum_all)
mean_peak_speed_cum = np.mean(peak_speed_cum_all, axis=0)

# Plot
plt.figure()
plt.subplot(1,2,1)
plot_speed(mean_peak_speed)
plt.subplot(1,2,2)
plot_speed(mean_peak_speed_cum)
plt.title("Average")
plt.show()