# Script for change in acceleration over time

import numpy as np
import matplotlib.pyplot as plt
import mne
import gc
from ICNVigorTask.utils.utils import reshape_data_trials, norm_speed, smooth_moving_average, plot_speed, \
    fill_outliers, norm_perf_speed, norm_0_1, get_bids_filepath, moving_variance, get_peak_acc
from mne_bids import BIDSPath, read_raw_bids, print_dir_tree, make_report
from alive_progress import alive_bar
import time
from statannot import add_stat_annotation
import seaborn as sb
from scipy import stats
import matplotlib
matplotlib.use('TkAgg')
import warnings
warnings.filterwarnings("ignore")

#bids_root = "C:\\Users\\ICN\\Documents\\VigorStim\\Data\\rawdata\\"
bids_root = "C:\\Users\\alessia\\Documents\\Jobs\\ICN\\vigor-stim\Data\\rawdata\\"

# Set analysis parameters
med = "Off"
plot_individual = True
subject_list = ["EL006", "EL007", "EL008", "EL012", "EL03", "EL014", "EL015", "EL016",
                "L001", "L002", "L003", "L005", "L006", "L007", "L008"]

# Plot the speed of all datasets
peak_acc_all = []
with alive_bar(len(subject_list), force_tty=True, bar='smooth') as bar:
    for subject in subject_list:

        # Read one dataset from every participant
        file_path = get_bids_filepath(root=bids_root, subject=subject, task="VigorStim", med=med)
        if not file_path:
            continue

        # Load the dataset of interest
        raw = read_raw_bids(bids_path=file_path, verbose=False)

        # Get the channel index of the mean speed values
        mean_speed_idx = raw.info["ch_names"].index("SPEED")

        # Structure data in trials and blocks
        data = reshape_data_trials(raw)

        # Extract the peak acceleration of all trials
        peak_acc = get_peak_acc(data[:, :, :, mean_speed_idx, :])
        del data
        gc.collect()

        # Detect and fill outliers (e.g. when subject did not touch the screen)
        np.apply_along_axis(lambda m: fill_outliers(m), axis=2, arr=peak_acc)
        np.apply_along_axis(lambda m: fill_outliers(m), axis=2, arr=peak_acc)

        # Normalize them to the start acceleration
        peak_acc = norm_perf_speed(peak_acc)

        # Plot if needed
        if plot_individual:
            plt.figure(figsize=(10, 5))
            plot_speed(smooth_moving_average(peak_acc))
            plt.xlabel("Movements")
            plt.ylabel("$\Delta$ speed in %")

        # Save the speed values for all datasest
        peak_acc_all.append(peak_acc)

        bar()
# Average over all datasets
mean_peak_acc = np.mean(peak_acc_all, axis=0)

# Plot speed over time
plt.figure(figsize=(10,5))
plt.subplot(1,2,1)
plot_speed(smooth_moving_average(mean_peak_acc))
plt.xlabel("Movements")
plt.ylabel("$\Delta$ speed in %")

# Reshape array such that data from one condition is flattened
peak_acc_all = np.array(peak_acc_all)
n_par, _,_,n_trials = peak_acc_all.shape
peak_acc_all_long = np.reshape(peak_acc_all, (n_par, 2, n_trials*2))

# Compute significance for each sample
t_all, p_all = stats.ttest_rel(peak_acc_all_long[:,0,:], peak_acc_all_long[:,1,:], axis=0)
sig_samp = np.where(p_all < 0.05)[0]

# Compute significance in 4 bins
peak_acc_bin = np.dstack((np.mean(peak_acc_all[:,:,:,:int(n_trials/2)], axis=3),
              np.mean(peak_acc_all[:,:,:,int(n_trials/2):], axis=3)))[:,:,[0,2,1,3]]
t_bin, p_bin = stats.ttest_rel(peak_acc_bin[:,0,:], peak_acc_bin[:,1,:], axis=0)

# Plot mean speed change and significance for 4 bins
plt.subplot(1,2,2)
x_names = ['1-50', '50-100', '100-150', '150-200']
hue_names = ['Slow', 'Fast']
peak_acc_bin = np.transpose(peak_acc_bin, (2, 0, 1))
dim1, dim2, dim3 = np.meshgrid(x_names, np.arange(peak_acc_bin.shape[1]), hue_names, indexing='ij')
ax = sb.barplot(x=dim1.ravel(), y=peak_acc_bin.ravel(), hue=dim3.ravel())
sb.stripplot(x=dim1.ravel(), y=peak_acc_bin.ravel(), hue=dim3.ravel(), dodge=True, ax=ax)

# Add statistics
add_stat_annotation(ax, x=dim1.ravel(), y=peak_acc_bin.ravel(), hue=dim3.ravel(),
                    box_pairs=[(("1-50", "Fast"), ("1-50", "Slow")),
                                 (("50-100", "Fast"), ("50-100", "Slow")),
                                 (("100-150", "Fast"), ("100-150", "Slow")),
                                 (("150-200", "Fast"), ("150-200", "Slow"))
                                ],
                    test='t-test_paired', text_format='simple', loc='inside', verbose=2, comparisons_correction=None)

plt.show()