# Fit featture over time for each participant and condition

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
from scipy.optimize import curve_fit
matplotlib.use('TkAgg')
import warnings
warnings.filterwarnings("ignore")

# Set analysis parameters
feature_name = "peak_speed" # out of ["peak_acc", "mean_speed", "move_dur", "peak_speed", "stim_time", "peak_speed_time", "move_onset_time", "move_offset_time"]
normalize = True
plotting = False
block = "stim"
med = "off" # "all", "on"
if med == "all":
    dataset = np.arange(28)
elif med == "off":
    dataset = [1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20, 26, 27, 28]
else:
    dataset = [3, 4, 5, 7, 9, 10, 12, 18, 21, 22, 23, 24, 25, 29]


# Load feature matrix
feature_matrix = np.load(f"../../Data/{feature_name}.npy")
n_datasets, _,_, n_trials = feature_matrix.shape

# Choose only the stimulation period
feature_matrix = feature_matrix[:, :, :, :]

# Detect and fill outliers (e.g. when subject did not touch the screen)
np.apply_along_axis(lambda m: utils.fill_outliers_mean(m, threshold=3), axis=3, arr=feature_matrix)

# Reshape matrix such that blocks from one condition are concatenated
feature_matrix = np.reshape(feature_matrix, (n_datasets, 2, n_trials*2))

# Delete the first 5 movements
feature_matrix = feature_matrix[:, :, 5:]

# Normalize to average of first 5 movements
if normalize:
   feature_matrix = utils.norm_perc(feature_matrix)

if block == "recovery":
    feature_matrix = feature_matrix[dataset, :, 91:]
    #feature_matrix = feature_matrix[dataset, :, :]
else:
    feature_matrix = feature_matrix[dataset, :, :91]

n_datasets, _, n_trials = feature_matrix.shape

# Define fitting function
def func(x, a, b):
    return a * x**b

# Fit data to function
x = np.arange(n_trials)
params = np.zeros((n_datasets, 2, 2))
conds = ["Slow", "Fast"]
colors = ["#00863b", "#3b0086"]
for i in range(n_datasets):
    plt.figure()
    for cond in range(2):
        y = feature_matrix[i, cond, :]
        try:
            popt, pcov = curve_fit(func, x, y, maxfev=10000)
            plt.plot(x, func(x, *popt),
                 label=f'fit: {conds[cond]} a={np.round(popt[0], 3)}, b={np.round(popt[1], 3)}',
                    color=colors[cond])
            params[i, cond, :] = popt
        except:
            print("not found")
        plt.plot(x, y, color=colors[cond])
        plt.legend()
        #plt.savefig(f"../../Plots/fit_sig_{i}_{med}_{block}.svg", format="svg", bbox_inches="tight")
        if not plotting:
            plt.close()

# Plot as boxplot
plt.figure(figsize=(16, 3))
plt.subplot(1, 4, 4)
my_pal = {"Slow": "#00863b", "Fast": "#3b0086", "All": "grey"}
my_pal_trans = {"Slow": "#80c39d", "Fast": "#9c80c2", "All": "lightgrey"}
x = np.repeat(["Slow", "Fast"], n_datasets)
y = np.concatenate((params[:, 0, 0], params[:, 1, 0]))
box = sb.boxplot(x=x, y=y, showfliers=False, palette=my_pal_trans)
sb.stripplot(x=x, y=y, palette=my_pal)
# Add statistics
add_stat_annotation(box, x=x, y=y,
                    box_pairs=[("Slow", "Fast")],
                    test='Wilcoxon', text_format='simple', loc='inside', verbose=2)

feature_name_space = feature_name.replace("_", " ")
plt.ylabel(f"Fit parameter a of {feature_name_space}", fontsize=12)
utils.despine()

# Plot the fitted curves over time and save the values
plt.subplot(1, 4, 1)
x = np.arange(n_trials)
feature_matrix_fit = np.zeros((n_datasets, 2, n_trials))
for i in range(n_datasets):
    for cond in range(2):
        y = func(x, *params[i, cond, :])
        plt.plot(x, y, color=colors[cond], linewidth=3)
        # save
        feature_matrix_fit[i, cond, :] = y
plt.xlabel("Trial number", fontsize=14)
plt.ylabel(f"Fit change in {feature_name_space} [%]", fontsize=14)
utils.despine()

# Compute mean and standard deviation
feature_matrix_fit_mean = np.mean(feature_matrix_fit, axis=0)
feature_matrix_fit_std = np.std(feature_matrix_fit, axis=0)

# Plot
plt.subplot(1, 4, 2)
utils.plot_conds(feature_matrix_fit_mean, feature_matrix_fit_std)
plt.xlabel("Trial number", fontsize=14)
plt.ylabel(f"Fit change in {feature_name_space} [%]", fontsize=14)

# Compute significance for each trial
ps = np.zeros(n_trials)
sig_thres = 0.05
for trial in range(1, n_trials):
    z, p = scipy.stats.wilcoxon(x=feature_matrix_fit[:, 0, trial], y=feature_matrix_fit[:, 1, trial])
    ps[trial] = p
    # Add p values to plot
    if p < sig_thres:
        plt.axvline(trial, linewidth=2, alpha=0.2, color="grey")
plt.title(f"Stimulation block, grey if p < {sig_thres}")
utils.despine()

# Plot the p values over trials
plt.subplot(1, 4, 3)
plt.plot(ps[1:], color="black", linewidth=3)
plt.axhline(0.05, color="red", linewidth=3)
plt.xlabel("Trial number", fontsize=14)
plt.ylabel("p value",  fontsize=14)
utils.despine()

plt.subplots_adjust(wspace=0.35)
# Save figure
plt.savefig(f"../../Plots/fit_sig_{feature_name}_{med}_{block}.svg", format="svg", bbox_inches="tight")
plt.show()