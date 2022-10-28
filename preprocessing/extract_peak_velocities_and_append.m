%% Append new peak data to matrix

clear all; 

% Load the data from one participant
[filename,path] = uigetfile('..\..\..\Data\new task data');
load(strcat(path,filename));
data = struct.data; 
options = struct.options;

% Set the parameters 
n_trials = 96;
n_blocks = 2; % number of blocks per condition 
n_cond = 2; % number of conditions
% Change the order in which the blocks are processed such that the order is
% always slow - first (cond=1)
if options.cond
    stim_blocks = [1:2; 3:4];
else
    stim_blocks = [3:4; 1:2];
end

% Initialize the arrays
peaks_all = [];

% Loop over stimulation conditions(slow-fast)
for i_cond=1:n_cond
    
    peaks = []; % array to store the peak
    
    % Loop over the blocks (stimulation-recovery)
    for i_block=1:n_blocks
            
        % Loop over every movement
        for i_trial=1:n_trials
            % Get the data from one trial
            mask = data(:,8) == stim_blocks(i_cond,i_block) & data(:,9) == i_trial;
            data_trial = data(mask,:); 
            % Get the peak and peak index
            [peak, ind_peak] = max(data_trial(:,4));
            peaks = cat(1,peaks, peak);
        end
    end
    % If needed, fill the outliers of the data
    peaks = filloutliers(peaks,"linear");
    
    % Save the peak velocities for one condition 
    peaks_all = cat(2,peaks_all, peaks);
end

% Append to old data 
% Load the data from one participant
[filename,path] = uigetfile('..\..\..\Data');
load(strcat(path,filename));
peaks_all_raw = cat(3, peaks_all_raw, peaks_all); 

% Plot for visual inspection 
figure;
for i_file=1:size(peaks_all_raw,3)
    subplot(2,11,i_file);
    plot(peaks_all_raw(:,:,i_file));
end

% Save matrix of peaks
save(strcat(path,filename), 'peaks_all_raw');
