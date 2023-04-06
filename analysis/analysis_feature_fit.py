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
datasets_off = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20, 26, 27]
normalize = True
datasets_on = [3, 4, 5, 7, 9, 10, 12, 18, 21, 22, 23, 24, 25]
datasets_all = np.arange(28)

# Load feature matrix
feature_matrix = np.load(f"../../Data/{feature_name}.npy")
n_datasets, _,_, n_trials = feature_matrix.shape

# Choose only the stimulation period
feature_matrix = feature_matrix[:, :, 0, :]

# Reshape matrix such that blocks from one condition are concatenated
feature_matrix = np.reshape(feature_matrix, (n_datasets, 2, n_trials))

# Delete the first 5 movements
feature_matrix = feature_matrix[:, :, 5:]

# Normalize to average of first 5 movements
if normalize:
   feature_matrix = utils.norm_perc(feature_matrix)
   #feature_matrix = utils.norm_perc_every_t_trials(feature_matrix, 45)

# Fit
def func(x, a, b):
    return 1+a*x**b
xdata = np.arange(n_trials-5)
a = np.zeros((len(datasets_off), 2))
for dataset in datasets_off:
    plt.figure()
    for cond in range(2):
        ydata = feature_matrix[dataset, cond, :]
        try:
            popt, pcov = curve_fit(func, xdata, ydata)
            plt.plot(xdata, func(xdata, *popt), 'r-',
                 label='fit: a=%5.3f, b=%5.3f' % tuple(popt))
            a[dataset, cond] = popt[0]
        except:
            print("not found")
        plt.plot(xdata, ydata, label=f'data {cond}')
        plt.legend()
        plt.close()
#plt.show()
x = np.repeat(["Slow", "Fast"], len(datasets_off))
box = sb.boxplot(x=x, y=np.concatenate((a[:, 0], a[:, 1])), showfliers=False)
sb.stripplot(x=x, y=np.concatenate((a[:, 0], a[:, 1])))

# Add statistics
add_stat_annotation(box, x=x, y=np.concatenate((a[:, 0], a[:, 1])),
                    box_pairs=[("Slow", "Fast")],
                    test='Wilcoxon', text_format='simple', loc='inside', verbose=2)

plt.show()


# Plot correlation between initial speed and difference in condition speeds
#datasets_off = datasets_all
#feature_matrix_non_norm = feature_matrix
off_fast_start = np.nanmedian(feature_matrix[datasets_off, 1, :], axis=1) - np.nanmedian(feature_matrix[datasets_off, 0, :], axis=1)
x = off_fast_start
y = median_feature_start[datasets_off]
y = np.percentile(feature_matrix_non_norm[datasets_off, :, :45], 90, axis=(1,2)) \
    - np.percentile(feature_matrix_non_norm[datasets_off, :, :45], 10, axis=(1,2))
y2 = np.percentile(feature_matrix_non_norm[datasets_off, :, -45:], 90, axis=(1,2)) \
    - np.percentile(feature_matrix_non_norm[datasets_off, :, -45:], 10, axis=(1,2))
corr, p = spearmanr(x, y)
plt.figure()
sb.regplot(x=x, y=y)
plt.title(f"Off corr = {np.round(corr, 2)}, p = {np.round(p, 3)}", fontweight='bold')
# Add labels
feature_name_space = feature_name.replace("_", " ")
if normalize:
    plt.xlabel(f"Difference Fast-Slow of change in {feature_name_space} \n in first half of block[%]", fontsize=12)
else:
    plt.xlabel(f"Difference Fast-Slow in {feature_name_space} \n in first half of block[%]", fontsize=12)
plt.ylabel(f"Initial {feature_name_space}", fontsize=12)

# Save figure
plt.subplots_adjust(bottom=0.2, left=0.2)
plt.savefig(f"../../Plots/corr_diff_init_{feature_name}_normalize_{normalize}.svg", format="svg", bbox_inches="tight")

plt.show()

plt.figure()
y = np.percentile(feature_matrix_non_norm[datasets_off, 1, :45], 90, axis=(1)) \
    - np.percentile(feature_matrix_non_norm[datasets_off, 1, :45], 10, axis=(1))
y2 = np.percentile(feature_matrix_non_norm[datasets_off, 1, -45:], 90, axis=(1)) \
    - np.percentile(feature_matrix_non_norm[datasets_off, 1, -45:], 10, axis=(1))
x = np.repeat(["First", "Last"], len(datasets_off))
box = sb.boxplot(x=x, y=np.concatenate((y, y2)), showfliers=False)
sb.stripplot(x=x, y=np.concatenate((y, y2)))