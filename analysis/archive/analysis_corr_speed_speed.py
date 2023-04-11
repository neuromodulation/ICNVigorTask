# Correlation between peak speed of stimulated movement and peak speed of subsequent movement
# binned
# Peak speed of stimulated movements over time

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
datasets = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20]

# Load peak speed matrix
peak_speed = np.load(f"../../Data/peak_speed.npy")
peak_speed = peak_speed[datasets, :, :, :]

# Detect and fill outliers (e.g. when subject did not touch the screen)
np.apply_along_axis(lambda m: utils.fill_outliers_nan(m), axis=3, arr=peak_speed)

# Normalize to the start of each stimulation block
peak_speed = utils.norm_perc(peak_speed)

# Load stim time matrix
stim_time = np.load(f"../../Data/stim_time.npy")
stim_time = stim_time[datasets, :, :, :]

plt.figure(figsize=(15, 5))
cond_names = ["Slow", "Fast"]
for cond in range(2):
    plt.subplot(2, 2, cond+1)
    stim_cond = stim_time[:, cond, 0, :]
    peak_speed_cond = peak_speed[:, cond, 0, :]
    # Get stim idx
    idx_stim = np.where(~np.isnan(stim_cond))
    # Select only stimulated movements and subsequent movement
    idx_stim = list(idx_stim)
    idx_stim[1] = idx_stim[1] + 1
    # Filter out indices than are larger than the array
    delete_idx = np.where(idx_stim[1] > 95)
    idx_stim = [np.delete(tmp, delete_idx) for tmp in idx_stim]
    # Select subsequent movements
    peak_speed_sub = peak_speed_cond[tuple(idx_stim)]
    # Select stimulated movement
    idx_stim[1] = idx_stim[1] - 1
    peak_speed_stim = peak_speed_cond[tuple(idx_stim)]
    # Correlate
    corr, p = spearmanr(peak_speed_sub.ravel(), peak_speed_stim.ravel())
    sb.regplot(x=peak_speed_sub.ravel(), y=peak_speed_stim.ravel())
    plt.title(f"{cond_names[cond]} stim, corr = {np.round(corr, 2)}, p = {np.round(p, 4)}", fontweight='bold')
    plt.ylabel(f"$\Delta$ peak speed of subsequent move in %", fontsize=14)
    plt.xlabel(f"$\Delta$ peak speed of stimulated move in %", fontsize=14)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.subplots_adjust(bottom=0.15, hspace=0.2)

plt.savefig(f"../../Plots/corr_stim_speed_sub_speed.png", format="png", bbox_inches="tight")

plt.show()