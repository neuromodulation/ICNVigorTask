# Correlation between number of stimulated movements and peak speed

import numpy as np
import matplotlib.pyplot as plt
from utils import fill_outliers, norm_perc, smooth_moving_average, plot_conds
import seaborn as sb
import matplotlib
from scipy.stats import pearsonr, spearmanr
matplotlib.use('TkAgg')
import warnings
warnings.filterwarnings("ignore")

# Set analysis parameters
plot_individual = False
# Define which datasets to include based on Dataset_list.csv
# Only OFF (one for each subject)
datasets = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20]

# Load peak speed matrix
peak_speed = np.load(f"peak_speed.npy")
peak_speed = peak_speed[datasets, :, :, :]

# Detect and fill outliers (e.g. when subject did not touch the screen)
np.apply_along_axis(lambda m: fill_outliers(m), axis=3, arr=peak_speed)

# Normalize to the start of each stimulation block
peak_speed = norm_perc(peak_speed)

# Smooth over 5 consecutive movements (does this make sense for correlation analysis?
# probably not necessary because peak speed is averaged in bins anyway
#peak_speed = utils.smooth_moving_average(peak_speed, window_size=5, axis=3)

# Load matrix containing time of each stimulation for each movement, Nan if no stimulation occurred
stim_time = np.load(f"stim_time.npy")
stim_time = stim_time[datasets, :, :, :]

# Extract whether a trial was stimulated or not
stim = stim_time.copy()
stim[np.isnan(stim)] = 0
stim[np.nonzero(stim)] = 1

# Bin number of stimulated movements and peak speed
# Number of bins seems to be crucial for the result
n_bins = 12
n_stim = np.array([np.mean(arr, axis=3)*100 for arr in np.array_split(stim, n_bins, axis=3)])
peak_speed_bin = np.array([np.mean(arr, axis=3) for arr in np.array_split(peak_speed, n_bins, axis=3)])

# Plot as scatter plot and compute correlation for each condition
cond_names = ["Slow", "Fast"]
plt.figure(figsize=(12, 5))
for cond in range(2):
    plt.subplot(1, 2, cond+1)
    corr, p = spearmanr(peak_speed_bin[1:, :, cond, 0].ravel(), n_stim[:-1, :, cond, 0].ravel())
    sb.regplot(peak_speed_bin[1:, :, cond, 0].ravel(), n_stim[:-1, :, cond, 0].ravel())
    plt.title(f"{cond_names[cond]} stim, corr = {np.round(corr,2)}, p = {np.round(p,3)}", fontweight='bold')
    plt.xlabel(f"$\Delta$ speed in %", fontsize=14)
    plt.ylabel(f"% of stimulated movements in bin", fontsize=14)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.subplots_adjust(bottom=0.15, hspace=0.2)

plt.show()