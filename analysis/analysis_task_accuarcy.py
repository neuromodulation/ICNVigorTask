# Script for investigating the task performance
# Features per stimulation condition

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
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
feature_name = "mean_speed"
plot_individual = False
med = "all"  # "on", "off", "all"
if med == "all":
    datasets = np.arange(26)
elif med == "off":
    datasets = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20, 26, 27]
else:
    datasets = [3, 4, 5, 7, 9, 10, 12, 18, 21, 22, 23, 24, 25]

# Load feature matrix
feature_matrix = np.load(f"../../Data/{feature_name}.npy")

# Select datasets of interest, keep only stimulation block
feature_matrix = feature_matrix[datasets, :, 0, :]
n_datasets, _, n_trials = feature_matrix.shape

# Detect and fill outliers (e.g. when subject did not touch the screen)
np.apply_along_axis(lambda m: utils.fill_outliers_nan(m, threshold=3), axis=2, arr=feature_matrix)

# Load stim time matrix
stim_time = np.load(f"../../Data/stim_time.npy")
stim_time = stim_time[datasets, :, 0, :]

# Select only stimulated movements
stim = stim_time.copy()
stim[np.isnan(stim)] = 0
stim[np.nonzero(stim)] = 1
stim = stim.astype(int)

# Delete the first 5 movements
feature_matrix = feature_matrix[:, :, 5:]
stim = stim[:, :, 5:]

# Normalize to average of first 5 movements
#feature_matrix = utils.norm_perc(feature_matrix)

# Compute mean/median feature over all trials, only slow and only fast stimulated
feature_all = np.zeros((n_datasets, 3))

# All
feature_all[:, 2] = np.nanmedian(feature_matrix, axis=[1, 2])

# Loop over conditions slow/fast
for cond in range(2):
    for dataset in range(n_datasets):
       feature_all[dataset, cond] = np.nanmedian(feature_matrix[dataset, cond, :][stim[dataset, cond, :] == 1])

# Plot as boxplots
my_pal = {"Slow": "#00863b", "Fast": "#3b0086", "All" : "grey"}
fig = plt.figure()
x = np.repeat(["Slow", "Fast", "All"], n_datasets)
box = sb.boxplot(x=x, y=feature_all.T.flatten(), showfliers=False, palette=my_pal)
sb.stripplot(x=x, y=feature_all.T.flatten(), palette=my_pal)

# Add statistics
add_stat_annotation(box, x=x, y=feature_all.T.flatten(),
                    box_pairs=[("Slow", "Fast"), ("Slow", "All"), ("Fast", "All")],
                    test='Wilcoxon', text_format='star', loc='inside', verbose=2)
# Add labels
feature_name_space = feature_name.replace("_", " ")
plt.ylabel(f"{feature_name_space}", fontsize=14)

# Save figure
plt.show()
plt.savefig(f"../../Plots/task_{feature_name}_{med}.svg", format="svg", bbox_inches="tight")

plt.show()