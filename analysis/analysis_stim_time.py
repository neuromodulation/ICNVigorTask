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
med = "off"  # "on", "off", "all"
if med == "all":
    datasets = np.arange(26)
elif med == "off":
    datasets = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20, 26, 27]
else:
    datasets = [3, 4, 5, 7, 9, 10, 12, 18, 21, 22, 23, 24, 25]
n_datasets = len(datasets)

# Load time of onset, offset and peak, stim
move_onset_time = np.load(f"../../Data/move_onset_time.npy")
move_onset_time = move_onset_time[datasets, :, :, :]
move_offset_time = np.load(f"../../Data/move_offset_time.npy")
move_offset_time = move_offset_time[datasets, :, :, :]
peak_speed_time = np.load(f"../../Data/peak_speed_time.npy")
peak_speed_time = peak_speed_time[datasets, :, :, :]
stim_time = np.load(f"../../Data/stim_time.npy")
stim_time = stim_time[datasets, :, :, :]

# Plot histogram of movement durations
move_dur = move_offset_time - move_onset_time
plt.figure()
plt.subplot(1, 2, 1)
sb.boxplot(move_dur.flatten(), showfliers=False, color="grey")
plt.xticks([])
plt.ylabel("Movement duration [second]", fontsize=12)

# Compute relative time of stim in movement
rel_stim_time = (stim_time - move_onset_time) / (move_offset_time - move_onset_time)

# Loop over conditions slow/fast
rel_stim_time_mean = np.zeros((2, n_datasets))
for cond in range(2):
    for dataset in range(n_datasets):
       rel_stim_time_mean[cond, dataset] = np.nanmedian(rel_stim_time[dataset, cond, :, :])

#rel_stim_time = np.vstack((rel_stim_time[:, 0, :, :].flatten(), rel_stim_time[:, 1, :, :].flatten()))
# Transform into %
rel_stim_time *= 100
plt.subplot(1, 2, 2)
x = np.repeat(["Slow", "Fast"], n_datasets)
my_pal = {"Slow": "#00863b", "Fast": "#3b0086", "All": "grey"}
box = sb.boxplot(x=x, y=rel_stim_time_mean.flatten(), showfliers=False, palette=my_pal)
sb.stripplot(x=x, y=rel_stim_time_mean.flatten(), palette=my_pal)
plt.ylabel("Time of stimulation [% of movement]", fontsize=12)

# Add stats
add_stat_annotation(box, x=x, y=rel_stim_time_mean.flatten(),
                    box_pairs=[("Slow", "Fast")],
                    test='Wilcoxon', text_format='star', loc='inside', verbose=2)

plt.subplots_adjust(wspace=0.5)
plt.show()

plt.savefig(f"../../Plots/Stim_time_{med}.png", format="png", bbox_inches="tight")

plt.show()
