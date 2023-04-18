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

# Save off and on as json files as well as UPDRS scores
datasets_off = [0, 1, 2, 6, 8, 11, 13, 14, 15, 16, 17, 19, 20, 26, 27]
datasets_on = [3, 4, 5, 7, 9, 10, 12, 18, 21, 22, 23, 24, 25]
UPDRS = [None, 26, 31, 22, 22, 27, 14, 14, 25, 18, 33, None, 30, 12, 28, 13, 27, 35, 28, 32, 23, 15, 14, None, 48, None, 35, 37]
information = {}
information['datasets_off'] = datasets_off
information['datasets_on'] = datasets_on
information['UPDRS scores'] = UPDRS
import json

with open('data_information.json', 'w') as fp:
    json.dump(information, fp)
    fp.write("\n")