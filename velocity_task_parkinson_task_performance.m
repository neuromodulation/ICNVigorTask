%% Measure the task perfromance 
% -> Inclusion criteria for the participants
% 1. Correct amount of movements are stimulated (between 25-40 %)
% 2. Time of stimulation is close to true peak 

%% Load data from one participant
% Load the data
[filename,path] = uigetfile('..\..\Data\Parkinson\');
load(strcat(path,filename));
data = struct.data; 
options = struct.options; 
n_trials = 32;

% First condition = Slow, Second condition = Fast
if options.slow_first
    stim_blocks = [3:5; 9:11];
else
    stim_blocks = [9:11; 3:5];
end

%% Loop through the blocks with stimulation 
% Intialize arrays to store the time difference between peak and
% stimulation and number of stimulated movements per condition
diffs_stim_peak = [];
n_stims = [];
for i_cond=1:size(stim_blocks, 1)
    n_stim = 0;
    for i_block=1:size(stim_blocks,2)
        for i_trial=1:n_trials
            % Get the data from one trial
            mask = data(:,8) == stim_blocks(i_cond,i_block) & data(:,9) == i_trial;
            data_trial = data(mask,:); 
            % Get the peak and peak index
            [peak, ind_peak] = max(data_trial);
            % Check whether movement was stimulated
            inds_stim = find(data_trial(:,11) == 1);
            if inds_stim
                % Get the index of the stimulation 
                ind_stim = inds_stim(1); 
                % Increase the counter of stimulated movements
                n_stim = n_stim + 1;
                % Save the time difference between peak and stimulation 
                diff_stim_peak = data_trial(ind_stim,3) - data_trial(ind_peak,3);
                diffs_stim_peak = cat(1, diffs_stim_peak, diff_stim_peak);
            end
        end
    end
    n_stims = cat(1,n_stims, n_stim);
end

%% Plot the results 
figure; 
histogram(diffs_stim_peak);
n_stims = (n_stims/96) * 100;
title(sprintf("slow %.2f %% fast %.2f %%", n_stims(1), n_stims(2)));
xlabel("Time in sec");

