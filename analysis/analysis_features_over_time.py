# Script for plotting and analysis of how different features change over time
# Peak mean speed
# Peak acceleration
# Path length
# Initiation
# Variability of movement

import numpy as np
import matplotlib.pyplot as plt
import mne
import gc
from ICNVigorTask.utils.utils import reshape_data_trials, norm_speed, smooth_moving_average, plot_conds, \
    fill_outliers, norm_perc, norm_0_1, get_bids_filepath, moving_variance, get_peak_acc
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
feature = "peak_acc" # out of ["peak_speed", "peak_acc"]
plot_individual = False
subject_list = ["EL006", "EL007", "EL008", "EL012", "EL013", "EL014", "EL015", "EL016",
                "L001", "L002", "L003", "L005", "L006", "L007", "L008"]

# Plot the speed of all datasets
feature_array_all = []
with alive_bar(len(subject_list), force_tty=True, bar='smooth') as bar:
    for subject in subject_list:

        # Read one dataset from every participant (peferably Med Off, if non existent Med On)
        file_path = get_bids_filepath(root=bids_root, subject=subject, task="VigorStim", med="Off")
        if not file_path:
            file_path = get_bids_filepath(root=bids_root, subject=subject, task="VigorStim", med="On")

        # Load the dataset of interest
        raw = read_raw_bids(bids_path=file_path, verbose=False)

        # Structure data in trials and blocks
        data = reshape_data_trials(raw)

        # Extract the feature
        if feature == "peak_speed":
            # Get the channel index of the mean speed values
            mean_speed_idx = raw.info["ch_names"].index("SPEED_MEAN")
            feature_array = np.max(data[:, :, :, mean_speed_idx, :], axis=3)
        if feature == "peak_acc":
            # Get the channel index of the mean speed values
            mean_speed_idx = raw.info["ch_names"].index("SPEED_MEAN")
            feature_array = get_peak_acc(data[:, :, :, mean_speed_idx, :])
        if feature == "move_time":


        # Delete the dataset to reduce memory load
        del data
        gc.collect()

        # Detect and fill outliers (e.g. when subject did not touch the screen)
        np.apply_along_axis(lambda m: fill_outliers(m), axis=2, arr=feature_array)
        np.apply_along_axis(lambda m: fill_outliers(m), axis=2, arr=feature_array)

        # Normalize to the start and smooth over 5 consecutive movements
        feature_array = smooth_moving_average(norm_perc(feature_array), window_size=5)

        # Plot if needed
        if plot_individual:
            plt.figure(figsize=(10, 5))
            plot_conds(feature_array)
            plt.xlabel("Movements")
            plt.ylabel(f"$\Delta$ {feature} in %")
            plt.title(file_path.basename)

        # Save the speed values for all datasest
        feature_array_all.append(feature_array)

        bar()

feature_array_all = np.array(feature_array_all)
n_par, _,_,n_trials = feature_array_all.shape

# Average over all datasets
mean_feature_array = np.mean(feature_array_all, axis=0)
# Compute standard deviation over all datasets
std_feature_array = np.std(feature_array_all, axis=0)

# Plot feature over time
plt.figure(figsize=(15, 5))
plt.subplot(1,2,1)
plot_conds(mean_feature_array, std_feature_array)
plt.xlabel("Movements", fontsize=14)
plt.ylabel(f"$\Delta$ {feature} in %", fontsize=14)

# Compute significance in 4 bins
feature_bin = np.dstack((np.mean(feature_array_all[:,:,:,:int(n_trials/2)], axis=3),
              np.mean(feature_array_all[:,:,:,int(n_trials/2):], axis=3)))[:,:,[0,2,1,3]]
t_bin, p_bin = stats.ttest_rel(feature_bin[:,0,:], feature_bin[:,1,:], axis=0)

# Plot mean feature change and significance for 4 bins
plt.subplot(1,2,2)
x_names = ['1-50', '50-100', '100-150', '150-200']
hue_names = ['Slow', 'Fast']
feature_bin = np.transpose(feature_bin, (2, 0, 1))
dim1, dim2, dim3 = np.meshgrid(x_names, np.arange(feature_bin.shape[1]), hue_names, indexing='ij')
ax = sb.barplot(x=dim1.ravel(), y=feature_bin.ravel(), hue=dim3.ravel(), palette=["blue", "red"])
sb.stripplot(x=dim1.ravel(), y=feature_bin.ravel(), hue=dim3.ravel(), dodge=True, ax=ax, palette=["blue", "red"])

# Add statistics
add_stat_annotation(ax, x=dim1.ravel(), y=feature_bin.ravel(), hue=dim3.ravel(),
                    box_pairs=[(("1-50", "Fast"), ("1-50", "Slow")),
                                 (("50-100", "Fast"), ("50-100", "Slow")),
                                 (("100-150", "Fast"), ("100-150", "Slow")),
                                 (("150-200", "Fast"), ("150-200", "Slow"))
                                ],
                    test='t-test_paired', text_format='simple', loc='inside', verbose=2, comparisons_correction=None)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

# Save figure on group basis
plt.savefig(f"../../../Plots/{feature}_group.pdf", format="pdf", bbox_inches="tight")

plt.show()