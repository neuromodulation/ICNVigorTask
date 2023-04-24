# Script for analyzing the de/acceleration

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
feature_1 = "peak_acc"
feature_2 = "peak_deacc"
datasets_off = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20, 26, 27]
normalize = True
datasets_on = [3, 4, 5, 7, 9, 10, 12, 18, 21, 22, 23, 24, 25]
datasets_all = np.arange(28)

# Load the peak speed and acceleration matrix
feature_matrix_1 = np.load(f"../../Data/{feature_1}.npy")
feature_matrix_2 = np.load(f"../../Data/{feature_2}.npy")

# Delete outliers
np.apply_along_axis(lambda m: utils.fill_outliers_nan(m, threshold=3), axis=3, arr=feature_matrix_1)
np.apply_along_axis(lambda m: utils.fill_outliers_nan(m, threshold=3), axis=3, arr=feature_matrix_2)
# Choose only the stimulation period
#feature_matrix = feature_matrix[:, :, 0, :]

# Compute the correlation between peak speed and peak acceleration
x = feature_matrix_1.flatten()
y = feature_matrix_2.flatten()
corr, p = spearmanr(x, y, nan_policy='omit')
plt.figure()
sb.regplot(x=x, y=y)
plt.title(f"Off corr = {np.round(corr, 2)}, p = {np.round(p, 3)}", fontweight='bold')
plt.xlabel(f"{feature_1}")
plt.ylabel(f"{feature_2}")

# Save figure
plt.savefig(f"../../Plots/corr_{feature_1}_{feature_2}.svg", format="svg", bbox_inches="tight")
plt.show()