%% Analyze the behavioural data of the task 
% Summary plot for each participant to gain insight into effect of
% stimulation 

%% Z-scores for each condition and dataset 

% Get a list of all datasets 
close all;
filenames = dir(fullfile('..\..\Data\Parkinson\',"*.mat"));
n_files = length(filenames);
n_trials = 33;
n_conds = 2;
n_blocks = 3;
conds = ["Slow","Fast"];
subplot_indxs = [1 2; 3 4];

for i_file=1:n_files
    
    % Load the data
    load(strcat('..\..\Data\Parkinson\',filenames(i_file).name));
    data = struct.data; 
    options = struct.options; 
    if ~any(fieldnames(options) == "cond")
        options.cond = options.slow_first;
    end
    
    % Change the block order accordingly such that slow always comes first
    if options.cond
        blocks_cond = [3:5; 9:11];
    else
        blocks_cond = [9:11; 3:5];
    end
    
    % Create a summary plot for each participant
    figure; 
    sgtitle(filenames(i_file).name);
    %% Loop over every movement
    peaks_all = [];
    for i_cond = 1:n_conds
        peaks = [];
        stim = [];
        diffs_target_stim = [];
        diffs_stim_peak = [];
        for i_block=1:n_blocks
            for i_trial=2:n_trials
                
                % Get the data from one trial
                mask = data(:,8) == blocks_cond(i_cond,i_block) & data(:,9) == i_trial;
                data_trial = data(mask, :);
                
                % Get the mean velocity over 4 instead of 7 samples
                data_vel_av = zeros(length(data_trial),1);
                for i=4:length(data_trial)
                    data_vel_av(i) = mean(data_trial(i-3:i,5));
                end
                
                % Find the index of the target
                ind_target = find(data_trial(:,10)==1,1);
            
                % Find the peak 
                [peak,ind_peak] = max(data_vel_av);
                peaks = cat(1,peaks, peak);
                
                % Check if stimulated
                ind_stim = find(data_trial(:,11) == 1, 1);
                
                % Save whether trial was stimulated and the time between
                % peak/stimulation and stimulation/target
                if ind_stim 
                    stim = cat(1,stim, 1);
                    diffs_stim_peak = cat(1,diffs_stim_peak, data_trial(ind_stim,3)-data_trial(ind_peak,3));
                    diffs_target_stim = cat(1,diffs_target_stim, data_trial(ind_target,3)-data_trial(ind_stim,3));
                else
                    stim = cat(1,stim, 0);
                end
            end
        end
        % After all blocks from one condition are processed 
        % Replace outliers with the linear method
        peaks = filloutliers(peaks,"linear");
        diffs_stim_peak = filloutliers(diffs_stim_peak,"linear");
        diffs_target_stim = filloutliers(diffs_target_stim, "linear");
        
        % Get the indexes of the movements after stimulation
        ind_after_stim = find(stim == 1) + 1; 
        % If the last movement was stimulated delete the entry
        if any(ind_after_stim > length(peaks))
            ind_after_stim = ind_after_stim(1:end-1);
            diffs_stim_peak = diffs_stim_peak(1:end-1);
            diffs_target_stim= diffs_target_stim(1:end-1);
        end
        
        % Plot the scatter plot of the velocity of the movement after
        % stimulation and the time between the peak and stimulation
        subplot(2,3,subplot_indxs(i_cond, 1));
        scatter(peaks(ind_after_stim),diffs_stim_peak);
        r = corrcoef(peaks(ind_after_stim),diffs_stim_peak);
        title(conds(i_cond) + " " + string(r(1,2)));
        
        % Plot the difference in peak velocity between consecutive
        % movements for stimulation and no stimulation 
        subplot(2,3,subplot_indxs(i_cond,2));
        diff_after_stim = peaks(ind_after_stim) - peaks(ind_after_stim-1);
        ind_no_stim = setdiff(2:length(peaks),ind_after_stim);
        diff_after_no_stim = peaks(ind_no_stim) - peaks(ind_no_stim-1);
        boxplot([diff_after_stim; diff_after_no_stim],[ones(length(diff_after_stim),1); ones(length(diff_after_no_stim),1)*2], 'Labels',["stim","no stim"]);
        title(conds(i_cond));
        % Plot the peak velocity after stimulation or no stimulation
%         subplot(2,3,subplot_indxs(i_cond,2));
%         peaks_after_stim = peaks(ind_after_stim);
%         peaks_after_no_stim = peaks(setdiff(1:length(peaks),ind_after_stim));
%         boxplot([peaks_after_stim; peaks_after_no_stim],[ones(length(peaks_after_stim),1); ones(length(peaks_after_no_stim),1)*2], 'Labels',["stim","no stim"]);
%         title(conds(i_cond));
        
        % Save the peaks normalized to the first 15 movements 
        peaks = peaks - mean(peaks(1:15)); 
        % Average over 5 consecutive movements
        peaks = mean(reshape(peaks(1:end-mod(length(peaks),5)),5,[]),1);
        peaks_all = cat(1, peaks_all, peaks);
    end
    
    % Plot the normalized change in velocity 
    subplot(2,3,5);
    plot(peaks_all(1,:)); hold on; 
    plot(peaks_all(2,:)); 
    legend(conds);
    
end