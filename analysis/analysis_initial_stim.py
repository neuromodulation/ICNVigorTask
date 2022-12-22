# Script for analysing umber of initial movements
# Correlation between number of stimulated movements and other feature

import numpy as np
import matplotlib.pyplot as plt
import mne
import gc
import ICNVigorTask.utils.utils as utils
from mne_bids import BIDSPath, read_raw_bids, print_dir_tree, make_report
from alive_progress import alive_bar
import time
from statannot import add_stat_annotation
import seaborn as sb
from scipy import stats
import matplotlib
from scipy.stats import pearsonr
matplotlib.use('TkAgg')
import warnings
warnings.filterwarnings("ignore")

#bids_root = "C:\\Users\\ICN\\Documents\\VigorStim\\Data\\rawdata\\"
bids_root = "C:\\Users\\alessia\\Documents\\Jobs\\ICN\\vigor-stim\Data\\rawdata\\"

# Set analysis parameters
feature = "peak_speed" # out of ["peak_speed", "peak_acc", "move_dur", "RT", "tortu", "variability"]
plot_individual = False
subject_list = ["L001", "EL006", "EL007", "EL008", "EL012", "EL013", "EL014", "EL015", "EL016",
                 "L002", "L003", "L005", "L006", "L007", "L008"]

n_stim_slow = []
n_stim_fast = []
feature_array_slow_all = []
feature_array_fast_all = []
with alive_bar(len(subject_list), force_tty=True, bar='smooth') as bar:
    for subject in subject_list:

        # Read one dataset from every participant (peferably Med Off, if non existent Med On)
        file_path = utils.get_bids_filepath(root=bids_root, subject=subject, task="VigorStim", med="Off")
        if not file_path:
            file_path = utils.get_bids_filepath(root=bids_root, subject=subject, task="VigorStim", med="On")

        # Load the dataset of interest
        raw = read_raw_bids(bids_path=file_path, verbose=False)

        # Get index of interesting data
        stim_idx = raw.info["ch_names"].index("STIMULATION")
        mean_speed_idx = raw.info["ch_names"].index("SPEED_MEAN")

        # Structure data in trials and blocks
        data = utils.reshape_data_trials(raw)

        # Extract whether a trial was stimulated or not
        stim_data = data[:, 0, :, stim_idx, :]
        stim = np.any(stim_data, axis=2)
        bins = 10
        slow = [np.sum(arr) for arr in np.array_split(stim[0, :], bins)]
        fast = [np.sum(arr) for arr in np.array_split(stim[1, :], bins)]

        # Extract the feature
        # Peak speed
        if feature == "peak_speed":
            feature_array = np.max(data[:, :, :, mean_speed_idx, :], axis=3)

        # Detect and fill outliers (e.g. when subject did not touch the screen)
        np.apply_along_axis(lambda m: utils.fill_outliers(m), axis=2, arr=feature_array)
        np.apply_along_axis(lambda m: utils.fill_outliers(m), axis=2, arr=feature_array)

        # Normalize to the start and smooth over 5 consecutive movements
        feature_array = utils.smooth_moving_average(utils.norm_perc(feature_array), window_size=5)

        # Bin
        feature_array_slow = [np.median(arr) for arr in np.array_split(feature_array[0, 0, :], bins)]
        feature_array_fast = [np.median(arr) for arr in np.array_split(feature_array[1, 0, :], bins)]

        if plot_individual:
            plt.figure(figsize=(15, 5))
            plt.subplot(1, 4, 1)
            plt.plot(slow, label="Slow")
            plt.plot(fast, label="Fast")
            plt.subplot(1, 4, 2)
            plt.plot(feature_array_slow, label="Slow")
            plt.plot(feature_array_fast, label="Fast")
            #plt.title(file_path.basename)
            plt.subplot(1, 4, 3)
            corr, p = pearsonr(feature_array_slow, slow)
            sb.regplot(feature_array_slow, slow)
            plt.title(f"Slow corr = {np.round(corr,2)} p = {np.round(p,3)}")
            plt.subplot(1, 4, 4)
            corr, p = pearsonr(feature_array_fast, fast)
            sb.regplot(feature_array_fast, fast)
            plt.title(f"Fast corr = {np.round(corr,2)} p = {np.round(p,3)}")
            plt.legend()

        # Save in array
        n_stim_slow.append(slow)
        n_stim_fast.append(fast)
        # Save the feature values for all datasest
        feature_array_slow_all.append(feature_array_slow)
        feature_array_fast_all.append(feature_array_fast)

        bar()

# Group level analysis
n_stim_slow = np.array(n_stim_slow)
n_stim_fast = np.array(n_stim_fast)
feature_array_slow_all = np.array(feature_array_slow_all)
feature_array_fast_all = np.array(feature_array_fast_all)
# Average
bis_thres = 10
plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
corr, p = pearsonr(feature_array_slow_all[:,:bis_thres].ravel(), n_stim_slow[:,:bis_thres].ravel())
sb.regplot(feature_array_slow_all[:,:bis_thres].ravel(), n_stim_slow[:,:bis_thres].ravel())
plt.title(f"Slow corr = {np.round(corr,2)} p = {np.round(p,3)}")
plt.xlabel(f"$\Delta$ {feature} in %", fontsize=14)
plt.ylabel(f"# of stimulated movements", fontsize=14)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.subplot(1, 2, 2)
corr, p = pearsonr(feature_array_fast_all[:,:bis_thres].ravel(), n_stim_fast[:,:bis_thres].ravel())
sb.regplot(feature_array_fast_all[:,:bis_thres].ravel(), n_stim_fast[:,:bis_thres].ravel())
plt.title(f"Fast corr = {np.round(corr,2)} p = {np.round(p,3)}")
plt.xlabel(f"$\Delta$ {feature} in %", fontsize=14)
plt.ylabel(f"# of stimulated movements", fontsize=14)

plt.show()
