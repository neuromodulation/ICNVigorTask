# Script for plotting median features in relation with medication and UPDRS

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
datasets_all = np.arange(28)

# Load feature matrix
feature_matrix = np.load(f"../../Data/{feature_name}.npy")
n_datasets, _,_, n_trials = feature_matrix.shape

# Reshape matrix such that blocks from one condition are concatenated
feature_matrix = np.reshape(feature_matrix, (n_datasets, 2, n_trials*2))

# Delete the first 5 movements
feature_matrix = feature_matrix[:, :, 5:]

# Normalize to average of first 5 movements
if normalize:
    feature_matrix = utils.norm_perc(feature_matrix)
    #feature_matrix = utils.norm_perc_every_t_trials(feature_matrix, 45)

# Plot median speed for each medication
median_feature_all = np.nanmedian(feature_matrix, axis=(1, 2))
median_feature_off = median_feature_all[datasets_off]
median_feature_on = median_feature_all[datasets_on]
median_feature_long = np.concatenate((median_feature_off, median_feature_on))

# Visualize
x = np.concatenate((np.repeat("Off", len(datasets_off)), np.repeat("On", len(datasets_on))))
my_pal = {"Off": "red", "On": "green", "All": "grey"}
box = sb.boxplot(x=x, y=median_feature_long, showfliers=False, palette=my_pal)
sb.stripplot(x=x, y=median_feature_long, palette=my_pal)

# Add statistics
add_stat_annotation(box, x=x, y=median_feature_long.flatten(),
                    box_pairs=[("On", "Off")],
                    test='t-test_ind', text_format='simple', loc='inside', verbose=2)
# Add labels
feature_name_space = feature_name.replace("_", " ")
if normalize:
    plt.ylabel(f"Change in {feature_name_space} [%]", fontsize=14)
else:
    plt.ylabel(f"{feature_name_space}", fontsize=14)
plt.xticks(fontsize=14)

# Save figure
plt.savefig(f"../../Plots/median_med_{feature_name}_normalize_{normalize}.svg", format="svg", bbox_inches="tight")

# Correlate median feature with UPDRS scores
UPDRS = np.array([None, 26, 31, 22, 22, 27, 14, 14, 25, 18, 33, None, 30, 12, 28, 13, 27, 35, 28, 32, 23, 15, 14, None, None, None, None, None])
median_feature_all = median_feature_all[UPDRS != None]
UPDRS = UPDRS[UPDRS != None].astype(np.int32)
corr, p = spearmanr(UPDRS, median_feature_all)
plt.figure()
sb.regplot(x=UPDRS, y=median_feature_all)
plt.title(f"corr = {np.round(corr, 2)}, p = {np.round(p, 3)}", fontweight='bold')
# Add labels
feature_name_space = feature_name.replace("_", " ")
if normalize:
    plt.ylabel(f"Change in {feature_name_space} [%]", fontsize=14)
else:
    plt.ylabel(f"{feature_name_space}", fontsize=14)
plt.xlabel(f"UPDRS", fontsize=14)

# Correlate only off/on
UPDRS = np.array([None, 26, 31, 22, 22, 27, 14, 14, 25, 18, 33, None, 30, 12, 28, 13, 27, 35, 28, 32, 23, 15, 14, None, None, None, None, None])
UPDRS_off = UPDRS[datasets_off]
median_feature_off = median_feature_off[UPDRS_off != None]
UPDRS_off = UPDRS_off[UPDRS_off != None].astype(np.int32)
corr, p = spearmanr(UPDRS_off, median_feature_off)
plt.figure()
sb.regplot(x=UPDRS_off, y=median_feature_off)
plt.title(f"Off corr = {np.round(corr, 2)}, p = {np.round(p, 3)}", fontweight='bold')
# Add labels
feature_name_space = feature_name.replace("_", " ")
if normalize:
    plt.ylabel(f"Change in {feature_name_space} [%]", fontsize=14)
else:
    plt.ylabel(f"{feature_name_space}", fontsize=14)
plt.xlabel(f"UPDRS", fontsize=14)


# Save figure
plt.savefig(f"../../Plots/median_corr_UPDRS_{feature_name}_normalize_{normalize}.svg", format="svg", bbox_inches="tight")

plt.show()