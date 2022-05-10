%% Plot the velocity normalized to only the first stimulation 
addpath ..\wjn_toolbox

%% Get a list of all datasets 
close all; clear all;
filenames = dir(fullfile('..\..\Data\Parkinson_Pilot\',"*.mat"));
n_files = length(filenames);
n_trials = 33;
n_conds = 2;
n_blocks = 14;
conds = ["Slow","Fast"];
block_after_break = [3 6 9 12];
peaks_slow_first = [];
peaks_fast_first = [];

%% Get the peak velocity of all movements (except calibration)
for i_file=1:n_files
    
    % Load the data from one recording
    load(strcat('..\..\Data\Parkinson_Pilot\',filenames(i_file).name));
    data = struct.data; 
    options = struct.options; 
    if ~any(fieldnames(options) == "cond")
        options.cond = options.slow_first;
    end 
    peaks = [];
    for i_block=3:n_blocks
        if ismember(i_block,block_after_break)
            start_trial = 5;
        else
            start_trial = 1;
        end
        % Loop over trials 
        for i_trial=start_trial:n_trials

            % Get the data from one trial
            mask = data(:,8) == i_block & data(:,9) == i_trial;
            data_trial = data(mask, :);

            % Find the peak 
            [peak,ind_peak] = max(data_trial(:,4));
            peaks = cat(1,peaks, peak);
        end
    end
    
    % Remove outlier
    peaks = filloutliers(peaks, 'linear');
    
    % Smoothen the data 
    peaks = smooth(peaks);
    
    % Normalize to the first 5 movements 
    peaks = (peaks - mean(peaks(1:5))) / mean(peaks(1:5)) * 100;
    
    % Save depending on which condition comes first 
    if options.cond == 1
        peaks_slow_first = cat(2, peaks_slow_first, peaks);
    else
        peaks_fast_first = cat(2, peaks_fast_first, peaks);
    end
    
end
%% Figure
close all;
white = [1 1 1];
col_fast = [0.4940, 0.1840, 0.5560];
col_fast_recov = white - 0.5 * (white - col_fast);
col_slow = [0.4660, 0.6740, 0.1880];
col_slow_recov = white - 0.5 * (white - col_slow);
figure;
% Plot the average for slow first
subplot(1,2,1);
one_block = size(peaks_fast_first,1)/4;
x1 = 1:one_block; x2 = one_block+1:one_block*2; 
x3 = (one_block*2)+1:one_block*3; x4 = (one_block*3)+1:one_block*4;
mypower(x1,peaks_fast_first(x1,:),col_fast,'sem'); hold on;
mypower(x2,peaks_fast_first(x2,:),col_fast_recov,'sem'); hold on;
mypower(x3,peaks_fast_first(x3,:),col_slow,'sem'); hold on;
mypower(x4,peaks_fast_first(x4,:),col_slow_recov,'sem'); hold on;
yline(0, "LineWidth", 1.5)
idx_block_end = [1,2,3] * one_block;
for i=1:3
    xline(idx_block_end(i), "LineWidth", 2, "alpha", 0.5); hold on;
end
xlabel("Trial");
ylabel("\Delta Speed %");
title(sprintf("Fast-Slow p=%i (p=3 OFF p=1 ON)",size(peaks_fast_first,2))); 
ylim([-40 40])

% Plot the average for slow first
subplot(1,2,2);
mypower(x1,peaks_slow_first(x1,:),col_slow,'sem'); hold on;
mypower(x2,peaks_slow_first(x2,:),col_slow_recov,'sem'); hold on;
mypower(x3,peaks_slow_first(x3,:),col_fast,'sem'); hold on;
mypower(x4,peaks_slow_first(x4,:),col_fast_recov,'sem'); hold on;
yline(0, "LineWidth", 1.5)
for i=1:3
    xline(idx_block_end(i), "LineWidth", 2, "alpha", 0.5); hold on;
end
xlabel("Trial");
ylabel("\Delta Speed %");
title(sprintf("Slow-Fast p=%i (p=2 OFF)",size(peaks_slow_first,2))); 
ylim([-40 40])
figone(7,40)

