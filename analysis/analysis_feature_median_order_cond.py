# Script for investigating the order effect

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
datasets_off = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20, 26, 27]
normalize = True
datasets_on = [3, 4, 5, 7, 9, 10, 12, 18, 21, 22, 23, 24, 25]
datasets_all = [datasets_off, datasets_on]

# Load slow first
slow_first = np.load(f"../../Data/slow_first.npy")

# Print order percentage in on and off medication
print(f"Off \n Slow/Fast: {np.sum(slow_first[datasets_off])}/{len(datasets_off)}")
print(f"On \n Slow/Fast: {np.sum(slow_first[datasets_on])}/{len(datasets_on)}")

# Load feature matrix
feature_matrix = np.load(f"../../Data/{feature_name}.npy")
n_datasets, _, _, n_trials = feature_matrix.shape

# Choose only the stimulation period
feature_matrix = feature_matrix[:, :, 0, :]

# Reshape matrix such that blocks from one condition are concatenated
feature_matrix = np.reshape(feature_matrix, (n_datasets, 2, n_trials))

# Delete the first 5 movements
feature_matrix = feature_matrix[:, :, 5:]

# Normalize to average of first 5 movements
if normalize:
   feature_matrix = utils.norm_perc(feature_matrix)

# Compute the effect in the first half of the stimulation period (difference fast-slow)
median_effect = np.nanmedian(feature_matrix[datasets_off, 1, :45], axis=1) - np.nanmedian(
    feature_matrix[datasets_off, 0, :45], axis=1)
idx_slow_fast = np.array(np.where(slow_first[datasets_off] == 1)).flatten()
idx_fast_slow = np.array(np.where(slow_first[datasets_off] == 0)).flatten()
y = np.concatenate((median_effect[idx_slow_fast], median_effect[idx_fast_slow]))
# Compare the difference between Slow/Fast and Fast/Slow

# Visualize
plt.figure()
my_pal = {"Fast/Slow": "green", "Slow/Fast": "grey"}
my_pal_trans = {"Fast/Slow": "lightgreen",  "Slow/Fast": "lightgrey"}
x = np.concatenate((np.repeat("Slow/Fast", len(idx_slow_fast)), np.repeat("Fast/Slow", len(idx_fast_slow))))
box = sb.boxplot(x=x, y=y, showfliers=False, palette=my_pal_trans)
sb.stripplot(x=x, y=y, ax=box, palette=my_pal)

# Add statistics
"""add_stat_annotation(box, x=x, y=y,
                    box_pairs=[("Slow/Fast", "Fast/Slow")],
                    test='Wilcoxon', text_format='simple', loc='inside', verbose=2)"""
# Add labels
feature_name_space = feature_name.replace("_", " ")
plt.ylabel(f"Difference Fast-Slow of change in {feature_name_space} [%]", fontsize=12)
plt.xticks(fontsize=14)

# Save figure
plt.savefig(f"../../Plots/order_{feature_name}_normalize_{normalize}.svg", format="svg", bbox_inches="tight")

plt.show()