# Script for extracting the outcome measure used for leaddbs analysis -_> difference between mean/median peak speed in Fast vs Slow condition

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
import os
import warnings
warnings.filterwarnings("ignore")

# Set analysis parameters
feature_name = "peak_speed"
block = "stim" # recovery or stim
normalize = True
med = "OFF"
patients = [1, 2, 3, 3, 3, 4, 5, 5, 6, 6, 7, 8, 8, 9, 10, 11, 12, 13, 14, 15, 16, 16, 16, 17, 18, 19, 20, 21, 22, 22]
if med == "OFF":
    datasets = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20, 26, 27, 28]
else:
    datasets = [4, 5, 9, 10, 12, 18, 22, 23, 24, 25, 29]

# Load feature matrix
feature_matrix = np.load(f"../../Data/{feature_name}.npy")
n_datasets, _,_, n_trials = feature_matrix.shape

# Detect and fill outliers (e.g. when subject did not touch the screen)
np.apply_along_axis(lambda m: utils.fill_outliers_nan(m, threshold=3), axis=3, arr=feature_matrix)
#np.apply_along_axis(lambda m: utils.fill_outliers_nan(m, threshold=3), axis=3, arr=feature_matrix)

# Reshape matrix such that blocks from one condition are concatenated
feature_matrix = np.reshape(feature_matrix, (n_datasets, 2, n_trials*2))

# Delete the first 5 movements
feature_matrix = feature_matrix[:, :, 5:]

# Normalize to average of first 5 movements
if normalize:
   feature_matrix = utils.norm_perc(feature_matrix)

if block == "recovery":
    feature_matrix = feature_matrix[:, :, 91:]
else:
    feature_matrix = feature_matrix[:, :, :91]

# Compute difference
outcome_measure = np.nanmean(feature_matrix[:, 1, :], axis=1) - np.nanmean(feature_matrix[:, 0, :], axis=1)
outcome_measure = outcome_measure[datasets]

# Check if correct
filenames = os.listdir("../../Data/behavioral_data/")
for i, filename in enumerate(filenames):
    if i in datasets: print(filename)

# Save as tex file
with open(f"{feature_name}_mean.txt", "w") as o:
    for line, dataset in zip(outcome_measure, datasets):
        print("{} {}".format(patients[dataset], line), file=o)

print("End")