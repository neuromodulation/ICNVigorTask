# Script for analyzing the difference between the effect between medication states

import numpy as np
import matplotlib.pyplot as plt
import mne
import gc
import scipy.stats
from statsmodels.stats.diagnostic import lilliefors
import utils.utils as utils
from mne_bids import BIDSPath, read_raw_bids, print_dir_tree, make_report
from alive_progress import alive_bar
import time
from statannot import add_stat_annotation
import seaborn as sb
from scipy import stats
from scipy.stats import pearsonr, spearmanr
import matplotlib
matplotlib.use('TkAgg')
import warnings
warnings.filterwarnings("ignore")

# Set analysis parameters
feature_name = "peak_speed" # out of ["peak_acc", "mean_speed", "move_dur", "peak_speed", "stim_time", "peak_speed_time", "move_onset_time", "move_offset_time"]
block = "recovery" # recovery or stim
datasets_off = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20, 26, 27]
normalize = True
datasets_on = [3, 4, 5, 7, 9, 10, 12, 18, 21, 22, 23, 24, 25]
datasets_all = np.arange(28)

# Load feature matrix
feature_matrix = np.load(f"../../Data/{feature_name}.npy")
n_datasets, _,_, n_trials = feature_matrix.shape

# Choose only the stimulation period
feature_matrix = feature_matrix[:, :, :, :]

# Detect and fill outliers (e.g. when subject did not touch the screen)
np.apply_along_axis(lambda m: utils.fill_outliers_nan(m, threshold=3), axis=3, arr=feature_matrix)

# Reshape matrix such that blocks from one condition are concatenated
feature_matrix = np.reshape(feature_matrix, (n_datasets, 2, n_trials*2))

# Delete the first 5 movements
feature_matrix = feature_matrix[:, :, 5:]

# Normalize to average of first 5 movements
if normalize:
   feature_matrix = utils.norm_perc(feature_matrix)
   #feature_matrix = utils.norm_perc_every_t_trials(feature_matrix, 45)

if block == "recovery":
    feature_matrix = feature_matrix[:, :, 91:]
else:
    feature_matrix = feature_matrix[:, :, :91]

# Plot median speed for each medication and condition
median_feature_all = np.nanmedian(feature_matrix, axis=2)
median_feature_off_diff = median_feature_all[datasets_off, 1] - median_feature_all[datasets_off, 0]
median_feature_on_diff = median_feature_all[datasets_on, 1] - median_feature_all[datasets_on, 0]
median_feature = np.concatenate((median_feature_off_diff.flatten(), median_feature_on_diff.flatten()))

# Visualize
plt.figure()
x = np.concatenate((np.repeat("Off", len(datasets_off)), np.repeat("On", len(datasets_on))))
my_pal = {"Off": "darkred", "On": "green", "All": "grey"}
my_pal_trans = {"Off": "lightcoral", "On": "lightgreen", "All": "lightgrey"}
box = sb.boxplot(x=x, y=median_feature, showfliers=False, palette=my_pal_trans)
sb.stripplot(x=x, y=median_feature, ax=box, palette=my_pal, legend=None, dodge=False)

# Add statistics
add_stat_annotation(box, x=x, y=median_feature,
                    box_pairs=[("On", "Off")],
                    test='t-test_ind', text_format='simple', loc='inside', verbose=2)

# Add labels
feature_name_space = feature_name.replace("_", " ")
plt.ylabel(f"Difference fast-slow of \n change in {feature_name_space}", fontsize=14)
plt.title(f"{block}", fontweight='bold')
plt.legend('', frameon=False)
plt.xticks(fontsize=14)

# Save figure
plt.savefig(f"../../Plots/diff_med_{feature_name}_{block}.svg", format="svg", bbox_inches="tight")


plt.show()