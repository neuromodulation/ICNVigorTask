# Script for computing average age and updrs

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
import matplotlib
matplotlib.use('TkAgg')
import warnings
warnings.filterwarnings("ignore")

# Set analysis parameters
age = np.array([69, 57, 55, 55, 55, 72, 45, 45, 66, 66, 67,  65, 65,   71 , 54,  69,  53 ,
       52,  60  ,73 , 73 , 73, 73,  53,  64 , 52,  50,  64,  62 , 62, 50])
UPDRS = np.array([np.nan, 26, 31, 22, 22, 27, 14, 14, 25, 18, 33, np.nan,
                  30, 12, 28, 13, 27, 35, 28, 32, 23, 15, 14, np.nan, 48,
                  np.nan, 35, 37, 36, np.nan, 13])

med = "off"  # "on", "off", "all"
if med == "all":
    datasets = np.arange(26)
elif med == "off":
    datasets = [1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20, 26, 27, 28, 30]
else:
    datasets = [3, 4, 5, 7, 9, 10, 12, 18, 21, 22, 23, 24, 25]

mean_age = np.mean(age[datasets])
mean_UPDRS = np.nanmean(UPDRS[datasets])
std_age = np.std(age[datasets])
std_UPDRS = np.nanstd(UPDRS[datasets])
print("END")