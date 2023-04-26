# Script for grouping the data into blocks depending on the amount of stimulated movements

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
from scipy.stats import pearsonr, spearmanr, percentileofscore
matplotlib.use('TkAgg')
import warnings
warnings.filterwarnings("ignore")

# Set analysis parameters
feature_name = "peak_speed"
plot_individual = False
normalize = True
datasets_off = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20, 26, 27]
datasets_on = [3, 4, 5, 7, 9, 10, 12, 18, 21, 22, 23, 24, 25]
dataset = datasets_off
#dataset = datasets_on

# Load feature matrix
feature_matrix = np.load(f"../../Data/{feature_name}.npy")

# Select datasets of interest, keep only stimulation block
feature_matrix = feature_matrix[dataset, :, 0, :]
n_dataset, _, n_trials = feature_matrix.shape

# Detect and fill outliers (e.g. when subject did not touch the screen)
np.apply_along_axis(lambda m: utils.fill_outliers_mean(m, threshold=3), axis=2, arr=feature_matrix)

# Load stim time matrix
stim_time = np.load(f"../../Data/stim_time.npy")
stim_time = stim_time[dataset, :, 0, :]

# Select only stimulated movements
stim = stim_time.copy()
stim[np.isnan(stim)] = 0
stim[np.nonzero(stim)] = 1
stim = stim.astype(int)

# Delete the first 5 movements
feature_matrix = feature_matrix[:, :, 5:]
stim = stim[:, :, 5:]

# Normalize to average of first 5 movements
feature_matrix_non_norm = feature_matrix.copy()
if normalize:
    feature_matrix = utils.norm_perc(feature_matrix)

n_blocks = 5
n_moves = 4
stim_block_median = np.zeros((n_dataset, 2, n_blocks))
# Get the median feature in blocks in which 5 stimulations occured  (1-5, 5-10, 10-15, 15-20)
for i in range(n_dataset):
    for cond in range(2):
        stim_cumsum = np.cumsum(stim[i, cond, :])
        for block in range(n_blocks):
            idx_low = np.where(stim_cumsum == block * n_moves + 1)[0][0]
            idx_high = np.where(stim_cumsum == (block + 1) * n_moves + 1)[0][0]
            stim_block_median[i, cond, block] = np.nanmean(feature_matrix[i, cond, idx_low:idx_high], axis=0)
            #[i, cond, block] = np.nanmean(feature_matrix[i, cond, block * n_moves + 1:(block + 1) * n_moves + 1], axis=0)

# Plot as grouped box plots
# Visualize
plt.figure()
x = []
y = []
box_pairs = []
for block in range(n_blocks):
    block_name = f"{block * n_moves}-{(block + 1) * n_moves}"
    x.extend(np.repeat(block_name, len(dataset)*2))
    y.extend(stim_block_median[:, :, block].flatten())
    box_pairs.append(((block_name, "Slow"), (block_name, "Fast")))

hue = np.array([["Slow", "Fast"] for i in range(len(dataset)*n_blocks)]).flatten()
# = np.concatenate((stim_block_median[:,:,0].flatten(), stim_block_median[:,:,1].flatten(), stim_block_median[:,:,2].flatten(), stim_block_median[:,:,3].flatten()))
my_pal = {"Slow": "#00863b", "Fast": "#3b0086", "All": "grey"}
my_pal_trans = {"Slow": "#80c39d", "Fast": "#9c80c2", "All": "grey"}
box = sb.boxplot(x=x, y=y, hue=hue, showfliers=False, palette=my_pal_trans)
sb.stripplot(x=x, y=y, dodge=True, ax=box, hue=hue, palette=my_pal, legend=None)

# Add statistics
add_stat_annotation(box, x=x, y=y, hue=hue,
                    box_pairs=box_pairs,
                    test='Wilcoxon', text_format='simple', loc='inside', verbose=2, comparisons_correction=None)
# Add labels
feature_name_space = feature_name.replace("_", " ")
if normalize:
    plt.ylabel(f"Median change in {feature_name_space} [%]", fontsize=14)
else:
    plt.ylabel(f"{feature_name_space}", fontsize=14)
plt.xlabel(f"Number of stimulated trials", fontsize=14)
plt.legend('', frameon=False)
plt.xticks(fontsize=14)

# Save figure
plt.savefig(f"../../Plots/median_block_stim_{feature_name}_normalize_{normalize}_{block}.svg", format="svg", bbox_inches="tight")
plt.show()
