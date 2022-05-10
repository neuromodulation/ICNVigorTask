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
    if ~any(fieldnames(options) == "cond")
        options.cond = options.slow_first;
    end
    % Change the block order accordingly such that slow always comes first
    if options.cond % Cond = 1 = Slow/First
        blocks = [3:8; 9:14];
    else % Cond = 0 = First/Slow
        blocks = [9:14; 3:8];
    end
    peaks_cond = [];
    for i_cond=1:n_conds
        peaks = [];
        for i_block = 1:n_blocks
            for i_trial = 1:n_trials
                % Extract trial data
                mask = data(:,8) == blocks(i_cond,i_block) & data(:,9) == i_trial;
                data_trial = data(mask, :);
                % Extract peak 
                peak = max(data_trial(:,4));
                % Delete trial after break and trial at the end to match
                % trial number of new task version
                if ~(i_trial == 1 && ismember(i_block, [1 4])) &&...
                   ~(i_trial > 31 && ismember(i_block, [3 6]))
                    peaks = cat(1,peaks,peak);
                end
            end
        end
        peaks = filloutliers(peaks,"linear");
        peaks_cond = cat(2,peaks_cond,peaks);
    end
    peaks_all = cat(3,peaks_all,peaks_cond);
    disp(max(data((data(:,1)<10000),1)));
end

%% Plot for visual inspection 
figure;
for i_file=1:n_files
    subplot(2,5,i_file);
    plot(peaks_all(:,:,i_file));
end

%% Plot for visual inspection 
figure;
load('peak_velocities_raw.mat')
for i_file=1:size(peaks_all_raw,3)
    subplot(2,6,i_file);
    plot(peaks_all_raw(:,:,i_file));
end

%% Load new data
filenames = dir(fullfile('..\..\Data\New task Data\',"*.mat"));
n_files = length(filenames);
n_trials = 96;
n_conds = 2;
n_blocks = 2;
conds = ["Slow","Fast"];
peaks_all_new = [];

for i_file=1:n_files
    % Load the data from one recording
    load(strcat('..\..\Data\New Task Data\',filenames(i_file).name));
    data = struct.data; 
    options = struct.options; 
    % Change the block order accordingly such that slow always comes first
    if options.cond % Cond = 1 = Slow/First
        blocks = [1:2;3:4];
    else % Cond = 0 = First/Slow
        blocks = [3:4;1:2];
    end
    peaks_cond = [];
    for i_cond=1:n_conds
        peaks = [];
        for i_block = 1:n_blocks
            for i_trial = 1:n_trials
                % Extract trial data
                mask = data(:,8) == blocks(i_cond,i_block) & data(:,9) == i_trial;
                data_trial = data(mask, :);
                % Compute mean velocity based on 7 values
                data_vel_av = zeros(1,length(data_trial));
                for i=7:length(data_trial)
                    data_vel_av(i) = mean(data_trial(i-6:i,5));
                end
                % Extract peak 
                peak = max(data_vel_av)*2;
                peaks = cat(1,peaks,peak);
            end
        end
        peaks = filloutliers(peaks,"linear");
        peaks_cond = cat(2,peaks_cond,peaks);
    end
    peaks_all_new = cat(3,peaks_all_new,peaks_cond);
    max(data((data(:,1)<10000),1))
end

%% Plot for visual inspection 
figure;
for i_file=1:size(peaks_all_new,3)
    subplot(2,7,i_file);
    plot(peaks_all_new(:,:,i_file));
end

%% Concatenate old and new dataset
peaks_new = cat(3,peaks_all,peaks_all_new);
% Plot for visual inspection
figure;
for i_file=1:size(peaks_new,3)
    subplot(2,7,i_file);
    plot(peaks_new(:,:,i_file));
end

%% Add filenames
load('filenames.mat')
for i=1:size(peaks_all_new,3)
    tmp = filenames(i).name;
    names{size(peaks_all_raw,3)+i} = tmp(1:4)+"2_"+tmp(5:end);
end

%% Rename arrays
% peaks_all_raw = peaks_new;
