# Plot number of stimulated movements over blocks

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
matplotlib.use('TkAgg')
import warnings
warnings.filterwarnings("ignore")

# Set analysis parameters
plot_individual = False
med = "on"  # "on", "off", "all"
if med == "all":
    datasets = np.arange(26)
elif med == "off":
    datasets = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20]
else:
    datasets = [3, 4, 5, 7, 9, 10, 12, 18, 21, 22, 23, 24, 25]

# Load stim time matrix
stim_time = np.load(f"../../Data/stim_time.npy")
stim_time = stim_time[datasets, :, :, 3:]

# Extract whether a trial was stimulated or not
stim = stim_time.copy()
stim[np.isnan(stim)] = 0
stim[np.nonzero(stim)] = 1

# Bin number of stimulated movements
bins = 10
n_stim = np.array([np.mean(arr, axis=3)*100 for arr in np.array_split(stim, bins, axis=3)])
n_stim_mean = np.mean(n_stim, axis=1)
n_stim_std = np.std(n_stim, axis=1)

# Plot number of stimulated movements over bins
cond_names = ["Slow", "Fast"]
colors = ["blue", "red"]
plt.figure()
for cond in range(2):
    # Plot average speed
    x = np.arange(len(n_stim))
    plt.plot(n_stim_mean[:, cond, 0], label=cond_names[cond], color=colors[cond], linewidth=3)
    # Plot std
    plt.fill_between(x, n_stim_mean[:, cond, 0] - n_stim_std[:, cond, 0],
                     n_stim_mean[:, cond, 0] + n_stim_std[:, cond, 0]
                     , alpha=0.5, color=colors[cond])

plt.legend()
plt.title(f"Medication: {med}")
plt.ylabel(f"% of stimulated movements (averaged in bin)", fontsize=12)
plt.xlabel("Bin number", fontsize=12)
plt.savefig(f"../../Plots/n_stim_bin_{med}.png", format="png", bbox_inches="tight")

plt.show()