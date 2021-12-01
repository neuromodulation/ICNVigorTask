%% Analysis of the behavioural data from a parkinson patient 

% TODO: Load and synchroize the neurophysiology data
%% Prepare the environment
 clear all; close all;
 addpath(genpath("utils\"));
 
 %% 1. Visualize the peak velocity during the stimulation and following recovery blocks

% Load the data
[filename,path] = uigetfile('..\Data\Parkinson\');
load(strcat(path,filename));
data = struct.data; 
options = struct.options; 
% Rename field as script changed between participants
if ~any(fieldnames(options) == "slow_first")
    options.slow_first = options.cond;
end

% Set some parameters
n_trials = 32; 
blocks = 3:14;
n_blocks = length(blocks);
block_sets = [3:8;9:14];
movement_thres = options.threshold_vel_move_start;
time = 100;
peaks_mean_all = [];
conditions = [];
close all; figure();
for i=1:size(block_sets,1)
    peaks = []; 
    stim = [];
    for i_block=block_sets(i,:)
        % Get the peak velocity
        for i_trial=1:n_trials
            [peak, ~] = get_peak_velocity_and_time(data,i_block,i_trial,movement_thres, time);
            % Only save teh peak if it is not unrealistically high
            if peak < 160000
                peaks = cat(1,peaks,peak);
                % Stimulated?
                stim = cat(1,stim,any(data(data(:,8) == i_block & data(:,9) == i_trial, 11)));
            else
                peaks = cat(1,peaks,peaks(end-1));
            end
        end
    end
    
    % Plot the peak velocities and mark the stimulated movements
    n_peaks = length(peaks);
    peaks_stim = peaks(logical(stim));
    x = 1:n_peaks;
    x_stim = x(logical(stim));
    subplot(3,1,i);
    plot(x, peaks, "black", 'LineWidth',2);
    hold on;
    plot(x, peaks, "o", 'LineWidth', 0.1, "Color", "black", "MarkerFaceColor", "black");
    hold on; 
    plot(x_stim, peaks_stim, "o", 'LineWidth',2, "Color", "red", "MarkerFaceColor", "red");
    hold on; 
    
    % Add a line that averages the peaks over 10 movements 
    peaks_mean = mean(reshape(peaks(1:end-mod(n_peaks,10)),10,[]),1);
    plot(linspace(1,n_peaks,length(peaks_mean)), peaks_mean,'LineWidth',1, "Color", "black");
    peaks_mean_all = cat(1,peaks_mean_all,peaks_mean);
    % Set the condition depending on the order
    if (i == 1 && options.slow_first == 0) || (i == 2 && options.slow_first == 1)
        condition = "Fast";
    else
        condition = "Slow";
    end
    conditions = cat(1,conditions,condition);
    title(sprintf(condition + " stimulated %.2f", sum(stim)/(length(stim)/2)*100) + " %");
    ylabel("Mean Velocity in pixel/second");
    f=get(gca,'Children');
    legend(f(2),'stimulated trials')
end
subplot(3,1,3);
plot(linspace(1,n_peaks,length(peaks_mean)), peaks_mean_all,'LineWidth',2);
title("Peak velocity averaged over 10 trials");
legend(conditions);
ylabel("Mean Velocity in pixel/second");
xlabel("Trial number");
sgtitle(filename(1:end-15));

%% Plot the running averaged peak velocities for all datasets (normalized to their starting velocity)
close all;

% Set some parameters
n_trials = 32; 
blocks = 3:14;
block_sets = [3:8;9:14];
    
% Get a list of all datasets 
filenames = dir(fullfile('..\..\Data\Parkinson\',"*.mat"));
n_files = length(filenames);
conditions = ["Slow","Fast"];
peaks_all_files = [];
peaks_mean_all_files = [];
for i_file=1:n_files
    
    % Load the data
    load(strcat('..\..\Data\Parkinson\',filenames(i_file).name));
    data = struct.data; 
    options = struct.options; 
    if ~any(fieldnames(options) == "slow_first")
        options.slow_first = options.cond;
    end
    
    movement_thres = options.threshold_vel_move_start;
    time = 100;
    peaks_mean_all = [];
    peaks_all = [];
    
    for i=1:size(block_sets,1)
        peaks = []; 
        for i_block=block_sets(i,:)
            % Get the peak velocity
            for i_trial=1:n_trials
                [peak, ~] = get_peak_velocity_and_time(data,i_block,i_trial,movement_thres, time);
                if peak < 16000
                    peaks = cat(1,peaks,peak);
                else
                    if peaks
                        peaks = cat(1,peaks,peaks(end-1));
                    else
                        peaks = cat(1,peaks,14000);
                    end
                end
            end
        end

        % Averages the peaks over 5 movements 
        n_peaks = length(peaks);
        peaks_mean = mean(reshape(peaks(1:end-mod(n_peaks,5)),5,[]),1);
        % Substract the baseline (first 15 movements)
        peaks_mean = peaks_mean - mean(peaks_mean(:,1:3));
        peaks = peaks - mean(peaks(1:15,:));
        % Append the new data
        peaks_mean_all = cat(1,peaks_mean_all,peaks_mean);
        peaks_all = cat(1,peaks_all,peaks.');
    end
    % Plot the normalized velocity
    subplot(ceil(n_files/2),2,i_file);
    x = linspace(1,n_peaks,length(peaks_mean));
    if options.slow_first == 0
        peaks_mean_all = peaks_mean_all([2 1],:);
        peaks_all = peaks_all([2 1],:);
    end
    plot(x, peaks_mean_all(1,:),'b',x, peaks_mean_all(2,:),'r','LineWidth',2);
    title(filenames(i_file).name(1:end-15));
    %xline(floor(n_peaks/2),"label","Stimulation offset");
    xline(floor(n_peaks/2));
    f=get(gca,'Children');
    if i_file == 1
        %legend([f(3),f(2)],conditions);
        xlabel("Trial number");
    end
    hold on;
    peaks_mean_all_files = cat(3,peaks_mean_all_files,peaks_mean_all);
    peaks_all_files = cat(3,peaks_all_files,peaks_all);
end
sgtitle("Normalized difference in peak velocity to the start of the block");

%% Plot the average over all participants
subplot(2,1,1);
mean_par = mean(peaks_mean_all_files,3);
x = linspace(1,n_peaks,length(mean_par));
plot(x, mean_par(1,:),'b',x, mean_par(2,:),'r','LineWidth',2);
title("Averaged over 5 movements");
legend(conditions);
subplot(2,1,2);
mean_par = mean(peaks_all_files,3);
x = 1:size(mean_par,2);
plot(x, mean_par(1,:),'b',x, mean_par(2,:),'r','LineWidth',2);
sgtitle("Averaged datasets");


%% Plot the peak velocities over the whole experiment
close all;
% Get a list of all datasets 
filenames = dir(fullfile('..\Data/Parkinson\',"*.mat"));
n_files = length(filenames);
figure();
for i_file=1:n_files
    
    % Load the data
    load(strcat('..\Data\Parkinson\',filenames(i_file).name));
    data = struct.data; 
    options = struct.options; 
    
    % Set some parameters
    n_trials = 32; 
    n_blocks = 14;
    movement_thres = options.threshold_vel_move_start-500;
    time = 100;
    peaks_all = [];
    
    for i_block=1:n_blocks
        % Get the peak velocity
        for i_trial=1:n_trials
            [peak, ~] = get_peak_velocity_and_time(data,i_block,i_trial,movement_thres, time);
            if peak < 20000
                peaks_all = cat(1,peaks_all,peak);
            end
        end
    end
    subplot(ceil(n_files/2),2,i_file);
    plot(peaks_all); hold on;
    % Plot the mean over 10 movements
    peaks_mean = mean(reshape(peaks_all(1:end-mod(length(peaks_all),10)),10,[]),1);
    % Mark where the changes are too high --> The movement was not
    % performed correctly -> Find a better solution for this in the task
    over_thres = find(abs(diff(peaks_all)) > 7000);
    for i=1:length(over_thres)
        xline(over_thres(i));
    end
    x = linspace(1,length(peaks_all),length(peaks_mean));
    plot(x, peaks_mean, 'LineWidth',2);
    title(filenames(i_file).name(1:end-15));
    ylabel("Velocity in pixel/second");
    xlabel("Trial number");
    ylim([0,20000])
end
sgtitle("Peak velocities over the whole experiment");

%% Stimulation times 
% Get the time of the peak velocity for each movement 
% Get a list of all datasets 
filenames = dir(fullfile('..\Data/Parkinson\',"*.mat"));
n_files = length(filenames);
n_trials = 32; 
n_blocks = 14;
stim_diff_all = [];
g=[];
figure();
for i_file=1:n_files
    
    % Load the data
    load(strcat('..\Data\Parkinson\',filenames(i_file).name));
    data = struct.data; 
    options = struct.options; 
    stim_time = options.threshold_time_stim;
    
    peak_times_all = [];
    stim_times_all = [];   
    diff_time_after_peak_all = [];
    for i_block=1:n_blocks
        % Get the time of the peak, stim and target
        for i_trial=1:n_trials
            try
                [peak, time_peak] = get_peak_velocity_and_time(data,i_block,i_trial,options.threshold_vel_move_start,100);
                time_stim = get_stim_time(data,i_block,i_trial,options.threshold_vel_move_start);
                diff_time_after_peak = get_time_after_peak(data,i_block,i_trial,options.threshold_vel_move_start);
                % If stimulation was applied save the times
                if time_stim
                    peak_times_all = cat(1,peak_times_all,time_peak);
                    stim_times_all = cat(1,stim_times_all,time_stim);
                    diff_time_after_peak_all = cat(1,diff_time_after_peak_all,diff_time_after_peak);
                end
            end
                     
        end
    end
    subplot(ceil(n_files/2),2,i_file);
    stim_diff = rmoutliers(stim_times_all - peak_times_all);
    stim_diff_all = cat(1,stim_diff_all,stim_diff);
    g = cat(1,g,ones(length(stim_diff),1)*i_file);
    histogram(rmoutliers(stim_times_all - peak_times_all),10); hold on;
    title(sprintf("Dataset %i",i_file));
end
sgtitle("Time difference between peak and stimulation");
figure();
boxplot(stim_diff_all, g);
ylabel("Time in sec");
title("Time of Stimulation - Time of peak");

