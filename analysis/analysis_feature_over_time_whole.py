# Script for plotting of features over the time of the whole experiment

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
import matplotlib
matplotlib.use('TkAgg')
import warnings
warnings.filterwarnings("ignore")

# Set analysis parameters
feature_name = "peak_speed" # out of ["peak_acc", "mean_speed", "move_dur", "peak_speed", "stim_time", "peak_speed_time", "move_onset_time", "move_offset_time"]
datasets_all = np.arange(3, 26)
#datasets_all = np.delete(datasets_all, 12)
datasets_off = [6, 8, 11, 13, 14, 15, 16, 17, 19, 20, 26, 27]
datasets_on = [3, 4, 5, 7, 9, 10, 18, 21, 22, 23, 24, 25]

# Load feature matrix
feature_matrix = np.load(f"../../Data/{feature_name}.npy")

# Plot median speed for each medication
median_feature_long = np.concatenate((np.nanmedian(feature_matrix[datasets_all, :, :, :], axis=[1, 2, 3]),
                                np.nanmedian(feature_matrix[datasets_off, :, :, :], axis=[1, 2, 3]),
                                np.nanmedian(feature_matrix[datasets_on, :, :, :], axis=[1, 2, 3])))

median_feature_long = np.concatenate((np.nanstd(feature_matrix[datasets_all, :, :, :], axis=(1, 2, 3)),
                                np.nanstd(feature_matrix[datasets_off, :, :, :], axis=(1, 2, 3)),
                                np.nanstd(feature_matrix[datasets_on, :, :, :], axis=(1, 2, 3))))
# Visualize
x = np.concatenate((np.repeat("All", len(datasets_all)), np.repeat("Off", len(datasets_off)), np.repeat("On", len(datasets_on))))
my_pal = {"Off": "red", "On": "green", "All" : "grey"}
box = sb.boxplot(x=x, y=median_feature_long, showfliers=False, palette=my_pal)
sb.stripplot(x=x, y=median_feature_long, palette=my_pal)

# Add statistics
add_stat_annotation(box, x=x, y=median_feature_long.flatten(),
                    box_pairs=[("On", "Off")],
                    test='Wilcoxon', text_format='star', loc='inside', verbose=2)
# Add labels
feature_name_space = feature_name.replace("_", " ")
plt.ylabel(f"{feature_name_space}", fontsize=14)
plt.xticks(fontsize=14)

plt.show()

# Save figure
plt.savefig(f"../../Plots/median_med_{feature_name}.svg", format="svg", bbox_inches="tight")

plt.show()