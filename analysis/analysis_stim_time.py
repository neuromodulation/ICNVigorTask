# Analysis of time of stimulation

import numpy as np
import matplotlib.pyplot as plt
import mne
import gc
import utils.utils as utils
from mne_bids import BIDSPath, read_raw_bids, print_dir_tree, make_report
from alive_progress import alive_bar
import time
from statannot import add_stat_annotation
import seaborn as sb
from scipy import stats
import matplotlib
from scipy.stats import pearsonr, spearmanr
from scipy.io import loadmat
import os
matplotlib.use('TkAgg')
import warnings
warnings.filterwarnings("ignore")

# Set analysis parameters
datasets_off = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20, 26, 27]
datasets_on = [3, 4, 5, 7, 9, 10, 12, 18, 21, 22, 23, 24, 25]
datasets = [datasets_off, datasets_on]

# Loop over the medication condition

rel_stim_time_all_med = []
diff_stim_stop_all_med = []
for dataset in datasets:

    # Load time of onset, offset and peak, stim
    move_onset_time = np.load(f"../../Data/move_onset_time.npy")
    move_onset_time = move_onset_time[dataset, :, :, :]
    move_offset_time = np.load(f"../../Data/move_offset_time.npy")
    move_offset_time = move_offset_time[dataset, :, :, :]
    peak_speed_time = np.load(f"../../Data/peak_speed_time.npy")
    peak_speed_time = peak_speed_time[dataset, :, :, :]
    stim_time = np.load(f"../../Data/stim_time.npy")
    stim_time = stim_time[dataset, :, :, :]

    # Compute and save relative time of stim in movement
    rel_stim_time = (stim_time - move_onset_time) / (move_offset_time - move_onset_time)
    rel_stim_time_median = np.nanmedian(rel_stim_time, axis=(2, 3)) * 100
    rel_stim_time_all_med.extend(rel_stim_time_median.flatten())

    # Compute distance of movement offset to stimulation offset
    diff_stim_stop = move_offset_time - (stim_time + 0.3)
    diff_stim_stop_median = np.nanmedian(diff_stim_stop, axis=(2, 3))
    diff_stim_stop_all_med.extend(diff_stim_stop_median.flatten())

# Plot
plt.figure(figsize=(8, 4))

# Plot the relative stimulation time and difference between stim and move offset
features = [rel_stim_time_all_med, diff_stim_stop_all_med]
labels = ["Time of stimulation [% of movement]", "Difference move end-stim end [seconds]"]
for i, feature in enumerate(features):
    plt.subplot(1, 2, i+1)
    x = np.concatenate((np.repeat("Off", len(datasets_off)*2), np.repeat("On", len(datasets_on)*2)))
    hue = np.array([["Slow", "Fast"] for j in range(len(datasets_off) + len(datasets_on))]).flatten()
    y = np.array(feature)
    my_pal = {"Slow": "#00863b", "Fast": "#3b0086", "All": "grey"}
    my_pal_trans = {"Slow": "#80c39d", "Fast": "#9c80c2", "All": "lightgrey"}
    box = sb.boxplot(x=x, y=y, hue=hue, showfliers=False, palette=my_pal_trans)
    sb.stripplot(x=x, y=y, hue=hue, palette=my_pal, legend=None, dodge=True, ax=box)
    plt.ylabel(labels[i], fontsize=12)

    # Add statistics
    add_stat_annotation(box, x=x, y=y, hue=hue,
                        box_pairs=[(("Off", "Slow"), ("Off", "Fast")),
                                   (("On", "Slow"), ("On", "Fast")),
                                   ],
                        test='Wilcoxon', text_format='simple', loc='inside', verbose=2)
plt.subplots_adjust(wspace=0.35)

# Save figure
plt.savefig(f"../../Plots/stim_timing.svg", format="svg", bbox_inches="tight")
plt.show()




