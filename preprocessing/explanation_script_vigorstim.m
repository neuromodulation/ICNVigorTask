%% VigorStim example script

%% Explanation of dataset
% Struct: 

% Options = Parameters of recording (stim amplitude etc)
% options.cond = Order of conditions, 1 = Slow/Fast, 0 = Fast/Slow

% Data = Matrix with one row for each sample (Sampling rate ~60 Hz)
% Column 1 = Positions of pen on x-axis
% Column 2 = Position of pen on y-axis
% Column 3 = Time from experiment start
% Column 4 = Averaged velocity 
% Participant 1-6 = Average over 7 samples 
% Participant 6-10 = Average over 6 samples
% Column 5 = Raw velocity 
% Column 6,7 = Velocity in x,y direction
% Column 8 = Block ID (1-4)
% 1 & 3 Stim (order of conditions Slow & Fast depends on options.cond)
% 2 & 4 Recovery
% Column 9 = Trial ID (1-96)
% Column 10 = Whether the pen is on the target (0/1)
% Column 11 = Whether stimulation is triggered (0/1)
% Column 12,13 = Position of target on x,y axis
% Column 14-16 = Global time

%% Things to keep in mind about the data
% The collection of datasets (1-15) contains data recorded with different
% task versions (as the task was still under development) 
% Participant 1-6 were measured with the first task version
% Participant 7-10 were measured with the second task version

% The most important difference between the task versions refers to the
% time at which stimulation is applied
% Task version 1: After movement onset there is a set time after which the
% peak is extracted and if the conditions are met, the stimulation is
% applied. The time threshold is determined on the basis of a calibration
% block (in subjects 1-6 Block ID 0) by taking the 80 percentile of the
% peak times during that block. 
% This approach, however, is suboptimal, as there is a high variance between 
% the time of stimulation and time of peak and depending on the speed of
% the movement, the stimulation occurs earlier/later (in my analysis,
% however, I did not find an effect of the timing of the stimulation on
% subsequent movement velocity) --> Hence, the task was changed
% Task version 2: The peak is extracted (and stimulation is applied) if the
% velocity decreases for 3 subsequent samples meaning the peak has passed.
% Like this we can achieve a consistent time delay between peak and
% stimulation for each trial. 

% Minor difference: In the first task version the mean velocity, based on 
% which stimulation is applied is an average of 7 values,
% while in the second task version it is only an average of 6 values. This
% change was made in order to bring the stimulation as close to the real
% movement peak as possible. I recommend to work with the raw velocity
% values (in column 5 and average those over as many samples as needed).

%% Example code snippet to extract peak speed for each trial

% Load data
filenames = dir(fullfile('..\..\Data\Parkinson_Pilot\all_datasets_eric\',"*.mat"));
n_files = length(filenames);
n_trials = 96; % Number of trials in each block
n_conds = 2;  % Number of conditions (slow & fast)
n_blocks = 2;  % Number of blocks in conditions (stim & recovery)
peaks_all = [];  % Array to store the peaks 

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
                [peak, idx_peak] = max(data_vel_av);
                peaks = cat(1, peaks, peak);
                
                % Extract more interesting features like the time between
                % stimulation onset and peak.. 
%                 idx_stim = find(data_trial(:,11) == 1);
%                 if idx_stim
%                    diff_stim_peak = data_trial(idx_stim,3) - data_trial(idx_peak,3);
%                 end

            end
        end
        % Fill outliers (e.g. because pen did not touch tablet)
        peaks = filloutliers(peaks, "linear");
        
        % Concatenate peak values from both conditions
        peaks_cond = cat(2, peaks_cond, peaks);
    end
    % Concatenate peak values from all datasets
    peaks_all = cat(3,peaks_all, peaks_cond);
end