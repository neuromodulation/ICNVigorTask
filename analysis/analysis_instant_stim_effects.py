# Analysis of the instantaneous effects of stimulation

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
feature_name = "peak_speed"
feature_name_space = feature_name.replace("_", " ")
plotting = False
datasets_off = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20, 26, 27]
datasets_on = [3, 4, 5, 7, 9, 10, 12, 18, 21, 22, 23, 24, 25]
datasets = [datasets_off, datasets_on]

# Load feature matrix
feature_matrix = np.load(f"../../Data/{feature_name}.npy")

# Load time of onset, offset and peak, stim
move_onset_time = np.load(f"../../Data/move_onset_time.npy")
move_offset_time = np.load(f"../../Data/move_offset_time.npy")
peak_speed_time = np.load(f"../../Data/speed_peak_time.npy")
stim_time = np.load(f"../../Data/stim_time.npy")
stim = stim_time.copy()
stim[np.isnan(stim)] = 0
stim[np.nonzero(stim)] = 1

# Detect and fill outliers (e.g. when subject did not touch the screen)
np.apply_along_axis(lambda m: utils.fill_outliers_mean(m), axis=3, arr=feature_matrix)
np.apply_along_axis(lambda m: utils.fill_outliers_mean(m), axis=3, arr=stim_time)
np.apply_along_axis(lambda m: utils.fill_outliers_mean(m), axis=3, arr=move_onset_time)
np.apply_along_axis(lambda m: utils.fill_outliers_mean(m), axis=3, arr=move_offset_time)

# Loop over the medication condition
rel_stim_time_all_med = []
diff_stim_stop_all_med = []
n_stim_all_med = []
dataset_names = ["Off", "On"]
cond_names = ["Slow", "Fast"]
corr_stim_time_all = []
corr_stim_post_all = []
for j, dataset in enumerate(datasets):

    # loop over subjects
    for subject in dataset:
        plt.figure()

        # loop over conditions
        for cond in range(2):

            # Get index of all stimulated movements, previous and consecutive
            stim_idx = np.where(stim[subject, cond, 0, :] == 1)[0]
            stim_idx_post = stim_idx + 1

            # Compute the relative time of stim in movement
            rel_stim_time = (stim_time[subject, cond, 0, :] - move_onset_time[subject, cond, 0, :]) / \
                            (move_offset_time[subject, cond, 0, :] - move_onset_time[subject, cond, 0, :])
            # Keep only not None
            rel_stim_time = rel_stim_time[stim_idx]

            # Delete entries that are longer than the array
            n_del = np.sum(stim_idx_post > 95)
            if n_del > 0:
                stim_idx = stim_idx[:-n_del]
                stim_idx_post = stim_idx_post[:-n_del]
                rel_stim_time = rel_stim_time[:-n_del]
            # Get feature of subsequent movement
            feature_post = feature_matrix[subject, cond, 0, stim_idx_post]

            # Compute a correlation between time of stimulation and feature of next move
            x = rel_stim_time
            y = feature_post
            corr, p = spearmanr(x, y)
            if plotting:
                plt.subplot(1, 2, cond + 1)
                sb.regplot(x=x, y=y)
                plt.title(f"{subject} {dataset_names[j]} {cond_names[cond]} corr = {np.round(corr, 2)}, p = {np.round(p, 3)}", fontweight='bold')
                plt.close()
            else:
                plt.close()

            # Save the correlation value
            corr_stim_time_all.append(corr)

            # Compute correlation between feature of the stimulated move and the subsequent move
            x = feature_matrix[subject, cond, 0, stim_idx]
            y = feature_post
            corr, p = spearmanr(x, y)
            if plotting:
                plt.subplot(1, 2, cond + 1)
                sb.regplot(x=x, y=y)
                plt.title(
                    f"{subject} {dataset_names[j]} {cond_names[cond]} corr = {np.round(corr, 2)}, p = {np.round(p, 3)}",
                    fontweight='bold')
                plt.show()
            else:
                plt.close()
            # Save
            corr_stim_post_all.append(corr)

# Plot the relative stimulation time and difference between stim and move offset
features = [corr_stim_time_all, corr_stim_post_all]
labels = [f"Spearman correlation value \n (stim time vs subsequent {feature_name_space}",
          f"Spearman correlation value \n (stim vs subsequent {feature_name_space}"]
plt.figure(figsize=(12, 4))
for i, feature in enumerate(features):
    plt.subplot(1, 2, i+1)
    # Plot the correlation values (to get a feeling for the overall tendency in the dataset)
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
plt.savefig(f"../../Plots/corr_subsequent_{feature_name}.svg", format="svg", bbox_inches="tight")
plt.show()



