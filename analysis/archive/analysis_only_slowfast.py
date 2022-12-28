# Script for analysing

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
plot_individual = True
subject_list = ["L001", "EL006", "EL007", "EL008", "EL012", "EL013", "EL014", "EL015", "EL016",
                 "L002", "L003", "L005", "L006", "L007", "L008"]

feature_arrays_all = []
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

        # Extract fast/slow movement trials

        # Get peak speed
        feature_array = np.max(data[:, :, :, mean_speed_idx, :], axis=3)

        # Get fast/slow movements (those that are faster/slower than the last two movements)
        slow = utils.get_slow_fast(feature_array[0,:,:], "slow").ravel()
        fast = utils.get_slow_fast(feature_array[1,:,:], "fast").ravel()

        # Extract them
        feature_array_slow = feature_array[0,:,:].ravel()[slow == 1]
        feature_array_fast = feature_array[1,:,:].ravel()[fast == 1]

        # Store in list
        feature_arrays = [feature_array_slow, feature_array_fast]

        names = ["slow", "fast"]
        plt.figure(figsize=(15, 5))
        for i,feature_array in enumerate(feature_arrays):

            # Detect and fill outliers (e.g. when subject did not touch the screen)
            feature_array = utils.fill_outliers(feature_array)
            feature_array = utils.fill_outliers(feature_array)

            # Normalize to the start and transform into percentage
            mean_start = np.mean(feature_array[:3])
            feature_array = feature_array - mean_start
            feature_array = ((feature_array - mean_start) / mean_start) * 100

            if plot_individual:
                plt.plot(feature_array, label=names[i])

        plt.legend()
        feature_arrays_all.append(feature_arrays)

        bar()


# Group level analysis


plt.show()
