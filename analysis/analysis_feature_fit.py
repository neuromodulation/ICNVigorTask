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
feature_name = "mean_speed" # out of ["peak_acc", "mean_speed", "move_dur", "peak_speed", "stim_time", "peak_speed_time", "move_onset_time", "move_offset_time"]
datasets_off = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20, 26, 27]
normalize = True
plotting = False
datasets_on = [3, 4, 5, 7, 9, 10, 12, 18, 21, 22, 23, 24, 25]
datasets_all = np.arange(28)

# Load feature matrix
feature_matrix = np.load(f"../../Data/{feature_name}.npy")
n_datasets, _,_, n_trials = feature_matrix.shape

# Choose only the stimulation period
feature_matrix = feature_matrix[:, :, 0, :]

# Reshape matrix such that blocks from one condition are concatenated
feature_matrix = np.reshape(feature_matrix, (n_datasets, 2, n_trials))

# Detect and fill outliers (e.g. when subject did not touch the screen)
np.apply_along_axis(lambda m: utils.fill_outliers_mean(m, threshold=3), axis=2, arr=feature_matrix)

# Delete the first 5 movements
feature_matrix = feature_matrix[:, :, 5:]

# Normalize to average of first 5 movements
if normalize:
   feature_matrix = utils.norm_perc(feature_matrix)

# Define fitting function
def func(x, a, b):
    return 1 + a * x**b

# Fit data to function
xdata = np.arange(n_trials-5)
a = np.zeros((len(datasets_off), 2))
conds = ["Slow", "Fast"]
colors = ["#00863b", "#3b0086"]
for i, dataset in enumerate(datasets_off):
    fig, ax = plt.subplots()
    for cond in range(2):
        ydata = feature_matrix[dataset, cond, :]
        try:
            popt, pcov = curve_fit(func, xdata, ydata, maxfev=10000)
            ax.plot(xdata, func(xdata, *popt),
                 label=f'fit: {conds[cond]} a={np.round(popt[0], 3)}, b={np.round(popt[1], 3)}',
                    color=colors[cond])
            a[i, cond] = popt[0]
        except:
            print("not found")
        ax.plot(xdata, ydata, color=colors[cond])
        plt.legend()
        if not plotting:
            plt.close()

# Plot as boxplot
plt.figure()
my_pal = {"Slow": "#00863b", "Fast": "#3b0086", "All": "grey"}
my_pal_trans = {"Slow": "#80c39d", "Fast": "#9c80c2", "All": "lightgrey"}
x = np.repeat(["Slow", "Fast"], len(datasets_off))
box = sb.boxplot(x=x, y=np.concatenate((a[:, 0], a[:, 1])), showfliers=False, palette=my_pal_trans)
sb.stripplot(x=x, y=np.concatenate((a[:, 0], a[:, 1])), palette=my_pal)
# Add statistics
add_stat_annotation(box, x=x, y=np.concatenate((a[:, 0], a[:, 1])),
                    box_pairs=[("Slow", "Fast")],
                    test='Wilcoxon', text_format='simple', loc='inside', verbose=2)

feature_name_space = feature_name.replace("_", " ")
plt.ylabel(f"Fit parameter a of {feature_name_space}", fontsize=12)

# Save figure
plt.savefig(f"../../Plots/curve_fit_{feature_name}_normalize_{normalize}.svg", format="svg", bbox_inches="tight")

plt.show()
