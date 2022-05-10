% Extract velocity values for each dataset

%% Get a list of all datasets 
close all;
filenames = dir(fullfile('..\..\Data\Parkinson_Pilot\all_datasets\',"*.mat"));
n_files = length(filenames);
n_trials = 33;
n_conds = 2;
n_blocks = 6;
conds = ["Slow","Fast"];
peaks_all = [];

for i_file=1:n_files
    % Load the data from one recording
    load(strcat('..\..\Data\Parkinson_Pilot\all_datasets\',filenames(i_file).name));
    data = struct.data; 
    options = struct.options; 
    
    % Add condition field im missing
    if ~any(fieldnames(options) == "cond")
        options.cond = options.slow_first;
        struct.options = options;
    end
        
    % Delete rows only with nulls
    rows_all_zeros = find(all(data == 0,2));
    data(rows_all_zeros,:) = [];
    
    % Change block numbers in order to match the new task structure 
    data(ismember(data(:,8),[1,2]),8) = 0;
    data(ismember(data(:,8),[3:5]),8) = 1;
    data(ismember(data(:,8),[6:8]),8) = 2;
    data(ismember(data(:,8),[9:11]),8) = 3;
    data(ismember(data(:,8),[12:14]),8) = 4;
    
    % Change trial numbers 
    for i_block=0:4
        tmp = data(data(:,8) == i_block,9);
        new_trial_number = [];
        trial_counter = 1;
        old_trial_number = 1;
        for i=1:length(tmp)
            if tmp(i) ~= old_trial_number
                trial_counter = trial_counter + 1;
                old_trial_number = tmp(i);
            end
            new_trial_number = cat(1, new_trial_number,trial_counter);
        end
        disp(max(new_trial_number));
        data(data(:,8) == i_block,9) = new_trial_number;
    end
    
    % Delete trials at start and end to match trial number of new task
    data(ismember(data(:,9), [1 98:99]), :) = [];
    data(:,9) = data(:,9) - 1;
    
    % Scale down to match screen resolution of new task (half) 
    data(:,[1,2,4,5,6,7,12,13]) = data(:,[1,2,4,5,6,7,12,13])/2;

    % Save data
    struct.data = data;
    save(strcat('..\..\Data\Parkinson_Pilot\all_datasets_eric\',filenames(i_file).name), 'struct');
end

%% Test data Eric - Script to extract peaks

% Load adapted data
filenames = dir(fullfile('..\..\Data\Parkinson_Pilot\all_datasets_eric\',"*.mat"));
n_files = length(filenames);
n_trials = 96; % Number of trials in each block
n_conds = 2;  % Number of conditions (slow & fast)
n_blocks = 2;  % Number of blocks in conditions (stim & recovery)
conds = ["Slow","Fast"];
peaks_all = [];

for i_file=1:n_files
    % Load the data from one recording
    load(strcat('..\..\Data\Parkinson_Pilot\all_datasets_eric\',filenames(i_file).name));
    data = struct.data; 
    options = struct.options; 
    
    % Change the block order accordingly such that slow always comes first
    if options.cond % Cond = 1 = Slow/First
        blocks = [1:2;3:4];
    else % Cond = 0 = First/Slow
        blocks = [3:4;1:2];
    end
    
    % Extract the peak of each trial
    peaks_cond = [];
    for i_cond=1:n_conds
        peaks = [];
        for i_block = 1:n_blocks
            for i_trial = 1:n_trials
                
                % Extract trial data
                mask = data(:,8) == blocks(i_cond,i_block) & data(:,9) == i_trial;
                data_trial = data(mask, :);
                
                % Compute mean velocity based on 7 values 
                % Raw velocity values stored in column 5 for all datasets
                data_vel_av = zeros(1,length(data_trial));
                for i=7:length(data_trial)
                    data_vel_av(i) = mean(data_trial(i-6:i,5));
                end
                
                % Extract peak 
                peak = max(data_vel_av);
                peaks = cat(1, peaks, peak);
            end
        end
        % Fill outliers (pen did not touch tablet, velocity value extremly
        % high)
        peaks = filloutliers(peaks, "linear");
        
        % Concatenate peak values from both conditions
        peaks_cond = cat(2, peaks_cond, peaks);
    end
    % Concatenate peak values from all datasets
    peaks_all = cat(3,peaks_all, peaks_cond);
end

%% Plot peak values 
figure;
for i_file=1:size(peaks_all,3)
    subplot(2,8,i_file);
    plot(peaks_all(:,:,i_file));
end

