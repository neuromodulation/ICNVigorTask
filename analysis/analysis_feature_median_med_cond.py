# Script for plotting median features in relation with medication, UPDRS and condition

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
block = "stim" # recovery or stim
datasets_off = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20, 26, 27, 28]
normalize = True
datasets_on = [4, 5, 9, 10, 12, 18, 22, 23, 24, 25, 29]
datasets_all = np.arange(30)

# Load feature matrix
feature_matrix = np.load(f"../../Data/{feature_name}.npy")
n_datasets, _,_, n_trials = feature_matrix.shape

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
median_feature_all = np.nanmean(feature_matrix, axis=2)
median_feature_off = median_feature_all[datasets_off, :]
median_feature_on = median_feature_all[datasets_on, :]
median_feature = np.concatenate((median_feature_off.flatten(), median_feature_on.flatten(), median_feature_all.flatten()))

# Visualize
plt.figure()
x = np.concatenate((np.repeat("Off", len(datasets_off)*2), np.repeat("On", len(datasets_on)*2), np.repeat("Off+On", len(datasets_all)*2)))
hue = np.array([["Slow", "Fast"] for i in range(len(datasets_off) + len(datasets_on) + len(datasets_all))]).flatten()
my_pal = {"Slow": "#00863b", "Fast": "#3b0086", "All": "grey"}
y = median_feature
my_pal_trans = {"Slow": "#80c39d", "Fast": "#9c80c2", "All": "grey"}
box = sb.boxplot(x=x, y=y, hue=hue, showfliers=False, palette=my_pal_trans)
sb.stripplot(x=x, y=y, dodge=True, ax=box, hue=hue, palette=my_pal, legend=None)

# Add statistics
add_stat_annotation(box, x=x, y=y, hue=hue,
                    box_pairs=[(("Off", "Slow"), ("Off", "Fast")),
                               (("On", "Slow"), ("On", "Fast")),
                               (("Off+On", "Slow"), ("Off+On", "Fast"))],
                    test='Wilcoxon', text_format='simple', loc='inside', verbose=2, comparisons_correction=None)

# Add labels
feature_name_space = feature_name.replace("_", " ")
if normalize:
    plt.ylabel(f"Median change in {feature_name_space} [%]", fontsize=14)
else:
    plt.ylabel(f"{feature_name_space}", fontsize=14)
plt.title(f"{block}", fontweight='bold')
plt.legend('', frameon=False)
plt.xticks(fontsize=14)
utils.despine()

# Save figure
plt.savefig(f"../../Plots/median_cond_{feature_name}_normalize_{normalize}_{block}.svg", format="svg", bbox_inches="tight")
plt.show()

# Correlate median difference in feature between Slow/Fast with UPDRS scores
median_feature_off = np.diff(median_feature_all[datasets_off, :], axis=1)
UPDRS = np.array([None, 26, 31, 22, 22, 27, 14, 14, 25, 18, 33, None, 30, 12, 28, 13, 27, 35, 28, 32, 23, 15, 14, None, 48, None, 35, 37, 36])
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
    plt.ylabel(f"Difference Slow/Fast of change in {feature_name_space} [%]", fontsize=12)
else:
    plt.ylabel(f"{feature_name_space}", fontsize=14)
plt.xlabel(f"UPDRS", fontsize=14)

# Save figure
plt.savefig(f"../../Plots/corr_UPDRS_median_diff_{feature_name}_normalize_{normalize}_{block}.svg", format="svg", bbox_inches="tight")

plt.show()