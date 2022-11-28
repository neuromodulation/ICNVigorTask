# Create brain vision file with behavioral data

import matplotlib.pyplot as plt
import mne
from scipy.io import loadmat, savemat
from scipy.stats import zscore
import numpy as np
import pandas as pd
import os
import json
from ICNVigorTask.utils.utils import norm_0_1


# Load template TMSi data
filename_raw =  "D:\\rawdata\\rawdata\\sub-EL011\\ses-EcogLfpMedOff01\\ieeg\\sub-EL011_ses-EcogLfpMedOff01_task-VigorStimR_acq-StimOnB_run-1_ieeg.vhdr"
raw_data = mne.io.read_raw_brainvision(filename_raw, preload=True)

# Load the MATLAB data
filename_mat = "D:\\rawdata\\rawdata\\sub-L003\\ses-LfpMedOff01\\ieeg\\sub-05-MedOff-task-VigorStim-R-Slow-Fast-StimOn-run-01_behavioral.mat"
behav_data = loadmat(filename_mat)
# Extract the behavioral data stored in a matrix
behav_data = behav_data["struct"][0][0][1]
# Determine the condition based on the filename
slow_first = 1 if filename_mat.index("Slow") < filename_mat.index("Fast") else 0

raw_data._data = []
behav_data = behav_data[:, [0,1,3,4,7,8,9,10,11,12,16]]

# add behavioral data
ch_names = ["PEN_X", "PEN_Y", "SPEED_MEAN", "SPEED", "BLOCK", "TRIAL", "TARGET", "STIMULATION", "TARGET_X", "TARGET_Y", "STIM_CONDITION"]
info = mne.create_info(ch_names, raw_data.info['sfreq'], ["bio"]*len(ch_names))
behav_raw = mne.io.RawArray(behav_data.T, info)
raw_data.add_channels([behav_raw], force_update_info=True)

# Save new brain vision file
filename_new = "D:\\rawdata\\rawdata\\sub-L003\\ses-LfpMedOff01\\ieeg\\sub-L003_ses-EcogLfpMedOff01_task-VigorStimR_acq-StimOnB_run-1_ieeg.vhdr"
mne.export.export_raw(fname=filename_new, raw=raw_data, fmt="brainvision", overwrite=True)

# Add channels to corresponding tsv file
tsv_filename = filename_raw[:-9]+"channels.tsv"
tsv_file = pd.read_csv(tsv_filename, sep='\t')
template = tsv_file.loc[len(tsv_file)-1]
template[-1] = "Task"
template[-2] = "Task"
for ch_name in ch_names:
    new_row = template.copy()
    new_row[0] = ch_name
    tsv_file = tsv_file.append(new_row)
# Update the sampling frequency
tsv_file.sampling_frequency = np.ones(len(tsv_file)) * 62
tsv_file.high_cutoff = np.ones(len(tsv_file)) * 62
# Save updated tsv file
tsv_filename_new = "D:\\rawdata\\rawdata\\sub-L003\\ses-LfpMedOff01\\ieeg\\sub-L003_ses-EcogLfpMedOff01_task-VigorStimR_acq-StimOnB_run-1_channels.tsv"

with open(tsv_filename_new,'w') as write_tsv:
    write_tsv.write(tsv_file.to_csv(sep='\t', index=False))

# Update corresponding json file
json_filename = filename_raw[:-4] + "json"
with open(json_filename, 'r') as f:
    json_file = json.load(f)
# Adjust parameters accordingly
json_file["ElectricalStimulationParameters"]["CurrentExperimentalSetting"]["StimulationMode"] = "adaptive"
json_file["ElectricalStimulationParameters"]["CurrentExperimentalSetting"]["StimulationParadigm"] = "adaptive stimulation"
json_file["SamplingFrequency"] = 62
# Save
json_filename_new = "D:\\rawdata\\rawdata\\sub-L003\\ses-LfpMedOff01\\ieeg\\sub-L003_ses-EcogLfpMedOff01_task-VigorStimR_acq-StimOnB_run-1_ieeg.json"
with open(json_filename_new, 'w') as f:
    json.dump(json_file, f)

print(f"Successfully added behavioral data to {filename_raw}")

plt.show()
plt.close()
#plt.show()