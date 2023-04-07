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

# Delete the first 5 movements
feature_matrix = feature_matrix[:, :, 5:]

# Normalize to average of first 5 movements
if normalize:
   feature_matrix = utils.norm_perc(feature_matrix)
   #feature_matrix = utils.norm_perc_every_t_trials(feature_matrix, 45)

# Define fitting function
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
        if not plotting:
            plt.close()

x = np.repeat(["Slow", "Fast"], len(datasets_off))
plt.figure()
box = sb.boxplot(x=x, y=np.concatenate((a[:, 0], a[:, 1])), showfliers=False)
sb.stripplot(x=x, y=np.concatenate((a[:, 0], a[:, 1])))
z, p = scipy.stats.wilcoxon(x=a[:, 0], y=a[:, 1])
plt.title(f"p = {p}")
# Different result
# Add statistics
add_stat_annotation(box, x=x, y=np.concatenate((a[:, 0], a[:, 1])),
                    box_pairs=[("Slow", "Fast")],
                    test='Wilcoxon', text_format='simple', loc='inside', verbose=2)

feature_name_space = feature_name.replace("_", " ")
plt.ylabel(f"Fit parameter a of {feature_name_space}", fontsize=12)
# Save figure
plt.savefig(f"../../Plots/curve_fit_{feature_name}_normalize_{normalize}.svg", format="svg", bbox_inches="tight")

plt.show()
