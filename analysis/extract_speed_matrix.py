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
import ICNVigorTask.utils.utils as utils
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
feature = "peak_speed" # out of ["peak_speed", "peak_acc", "move_dur", "RT", "tortu", "variability"]
plot_individual = True
subject_list = ["L001", "EL006", "EL007", "EL008", "EL012", "EL013", "EL014", "EL015", "EL016",
                 "L002", "L003", "L005", "L006", "L007", "L008"]
subject_list = ["EL015"]

# Plot the feature over time for all datasets
feature_array_all = []
with alive_bar(len(subject_list), force_tty=True, bar='smooth') as bar:
    for subject in subject_list:

        # Read one dataset from every participant (peferably Med Off, if non existent Med On)
        file_path = utils.get_bids_filepath(root=bids_root, subject=subject, task="VigorStim", med="Off")
        if not file_path:
            #continue
            file_path = utils.get_bids_filepath(root=bids_root, subject=subject, task="VigorStim", med="On")

        # Load the dataset of interest
        raw = read_raw_bids(bids_path=file_path, verbose=False)

        # Get index of interesting data
        mean_speed_idx = raw.info["ch_names"].index("SPEED_MEAN")
        target_idx = raw.info["ch_names"].index("TARGET")
        target_x_idx = raw.info["ch_names"].index("TARGET_X")
        target_y_idx = raw.info["ch_names"].index("TARGET_Y")
        pen_x_idx = raw.info["ch_names"].index("PEN_X")
        pen_y_idx = raw.info["ch_names"].index("PEN_Y")

        # Structure data in trials and blocks
        data = utils.reshape_data_trials(raw)

        # Extract the feature
        # Peak speed
        if feature == "peak_speed":
            feature_array = np.max(data[:, :, :, mean_speed_idx, :], axis=3)
        # Peak acceleration
        if feature == "peak_acc":
            feature_array = utils.get_peak_acc(data[:, :, :, mean_speed_idx, :])
        # Movement duration
        if feature == "move_dur":
            feature_array = utils.get_move_dur(data[:, :, :, [mean_speed_idx, target_idx], :])
        # Reaction time
        if feature == "RT":
            feature_array = utils.get_RT(data[:, :, :, mean_speed_idx, :])
        # Tortuosity of movement
        if feature == "tortu":
            feature_array = utils.get_tortu(data[:, :, :, [pen_x_idx, pen_y_idx, target_x_idx, target_y_idx], :])
        # Variability of speed curve
        if feature == "variability":
            feature_array = utils.get_variability(data[:, :, :, mean_speed_idx, :])

        # Delete the dataset to reduce memory load
        del data
        gc.collect()

        # Detect and fill outliers (e.g. when subject did not touch the screen)
        np.apply_along_axis(lambda m: utils.fill_outliers(m), axis=2, arr=feature_array)
        np.apply_along_axis(lambda m: utils.fill_outliers(m), axis=2, arr=feature_array)

        # Normalize to the start and smooth over 5 consecutive movements
        #feature_array = utils.smooth_moving_average(utils.norm_perc(feature_array), window_size=5)

        # Plot if needed
        if plot_individual:
            plt.figure(figsize=(10, 5))
            utils.plot_conds(feature_array)
            plt.xlabel("Movements")
            plt.ylabel(f"$\Delta$ {feature} in %")
            plt.title(file_path.basename)

        # Save the feature values for all datasest
        feature_array_all.append(feature_array)

        bar()

feature_array_all = np.array(feature_array_all)

# Save matrix
plt.save(f"../../../Data/peak_speed.npy", feature_array_all)

plt.show()