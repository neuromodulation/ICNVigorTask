# Add synchronized behavioral data to brain vision file

import matplotlib.pyplot as plt
import mne
from scipy.io import loadmat, savemat
from scipy.stats import zscore
import numpy as np
import pandas as pd
import os
import json
from ICNVigorTask.utils.utils import norm_0_1

# Get list of all brainvision and matlab datasets
type = "VigorStim"

path = "D:\\rawdata\\rawdata\\"
folder_list = os.listdir(path)
files_raw_list = []
files_mat_list = []
# Loop over every subject
for subject_folder in folder_list:
    # Get the brainvision files for that subject
    for root, dirs, files in os.walk(path+subject_folder):
        for file in files:
            if (file.endswith(".vhdr")) and type in file and "new" not in file:
                files_raw_list.append(os.path.join(root, file))
                # Add matlab file with correct hand
                hand = "R" if "R" in file else "L"
                run = "run-01" if "run-1" in file else "run-02"
                for file in os.listdir(root):
                    if file.endswith(".mat") and hand in file and run in file:
                        files_mat_list.append(os.path.join(root, file))


# Loop through all Vigor Stim datasets and add matlab data to brainvision file
#files_raw_list = files_raw_list[2:]
#files_mat_list = files_mat_list[2:]
for filename_raw, filename_mat in zip(files_raw_list, files_mat_list):

    # Load the TMSi data
    raw_data = mne.io.read_raw_brainvision(filename_raw, preload=True)

    # Load the MATLAB data
    behav_data = loadmat(filename_mat)
    # Extract the behavioral data stored in a matrix
    behav_data = behav_data["struct"][0][0][1]
    # Determine the condition based on the filename
    slow_first = 1 if filename_mat.index("Slow") < filename_mat.index("Fast") else 0

    # Downsample the neuro data to 500 Hz
    new_sfreq = 500
    raw_data.resample(new_sfreq)

    # Get the times of the samples
    time_array_neuro = raw_data.times.flatten()

    # Determine stimulation onset base don LFP channels

    # Filter the data
    raw_data_filt = raw_data.copy().filter(l_freq=2, h_freq=200)
    # Average first 10 channels (cut out the last 100 samples because of end artifact)
    data_mean = np.mean(raw_data_filt._data[:10,:-1000], axis=0)

    # Plot for visual inspection
    plt.figure()
    plt.plot(data_mean)

    # Find the first sample above a threshold
    idx_onset_neuro = np.where(np.abs(zscore(data_mean)) > 2.5)[0][0]

    # Plot for visual inspection
    plt.axvline(idx_onset_neuro, color="red")
    #plt.show()

    # Find the first sample with stimulation in the behavioral data
    behav_data_stim = behav_data[:, 10].flatten()
    idx_onset_behav = np.where(behav_data_stim == 1)[0][0]

    # Get time in sec at which stimulation onsets occur
    time_onset_neuro = time_array_neuro[idx_onset_neuro]
    time_array_behav = behav_data[:, 2].flatten()
    time_onset_behav = time_array_behav[idx_onset_behav]

    # Substract the time difference from the neuro data (neuro recording alsways starts first)
    diff_time = time_onset_neuro - time_onset_behav
    time_array_neuro = time_array_neuro - diff_time

    # Get indexes of stimulation onset in behav data and visually check the alignment
    plt.figure()
    idx_stim = np.where(np.diff(behav_data_stim) == 1)[0]
    plt.plot(time_array_neuro[:len(data_mean)], data_mean)
    for idx in idx_stim:
        plt.axvline(time_array_behav[idx], color="red")
    #plt.show()

    # For every sample in the neuro data find the closest sample in the behav data
    n_cols = np.size(behav_data, 1)
    behav_data_long = np.zeros((len(time_array_neuro), n_cols))
    for i, time_samp in enumerate(time_array_neuro):
        # If neuro sample is before or after onset of behav recording, save zeros
        if time_samp < 0 or time_samp > np.max(time_array_behav):
            behav_data_long[i, :] = np.zeros(16)
        else:
            # Get the sample that is closest in time
            idx_samp_behav = np.argmin(np.abs(time_array_behav - time_samp))
            behav_data_long[i,:] = behav_data[idx_samp_behav,:]

    # Add a channel containing the condition
    cond = [0 if i in [1, 2] and slow_first or i in [3, 4] and not slow_first else 1 for i in behav_data_long[:, 7]]
    behav_data_long = np.hstack((behav_data_long, np.array(cond)[:, np.newaxis]))

    # Select channels that should be saved
    behav_data_long = behav_data_long[:, [0,1,3,4,7,8,9,10,11,12,16]]

    # Add behavioral channels to the raw mne object
    ch_names = ["PEN_X", "PEN_Y", "SPEED_MEAN", "SPEED", "BLOCK", "TRIAL", "TARGET", "STIMULATION", "TARGET_X", "TARGET_Y", "STIM_CONDITION"]
    info = mne.create_info(ch_names, raw_data.info['sfreq'], ["bio"]*len(ch_names))
    behav_raw = mne.io.RawArray(behav_data_long.T, info)
    raw_data.add_channels([behav_raw], force_update_info=True)

    # Final plot for visual inspection
    plt.figure()
    plt.plot(raw_data.get_data(["STIMULATION"]).T)
    plt.plot(norm_0_1(data_mean))

    # Save new brain vision file
    filename_new = filename_raw[:-5] + "_new.vhdr"
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
    tsv_file.sampling_frequency = np.ones(len(tsv_file)) * new_sfreq
    tsv_file.high_cutoff = np.ones(len(tsv_file)) * (new_sfreq / 2)
    # Save updated tsv file
    with open(tsv_filename[:-4]+"_new.tsv",'w') as write_tsv:
        write_tsv.write(tsv_file.to_csv(sep='\t', index=False))

    # Update corresponding json file
    json_filename = filename_raw[:-4] + "json"
    with open(json_filename, 'r') as f:
        json_file = json.load(f)
    # Adjust parameters accordingly
    json_file["ElectricalStimulationParameters"]["CurrentExperimentalSetting"]["StimulationMode"] = "adaptive"
    json_file["ElectricalStimulationParameters"]["CurrentExperimentalSetting"]["StimulationParadigm"] = "adaptive stimulation"
    json_file["SamplingFrequency"] = new_sfreq
    # Save
    with open(json_filename[:-5]+"_new.json", 'w') as f:
        json.dump(json_file, f)

    print(f"Successfully added behavioral data to {filename_raw}")

    plt.show()
    plt.close()
#plt.show()