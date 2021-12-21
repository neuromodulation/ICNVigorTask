%% Analyze the behavioural data of the task 
% Next week: Find an analysis that can be statistically tested 
% Next week: Test integration with TMSi

%% Z-scores for each condition and dataset 

% Get a list of all datasets 
close all;
filenames = dir(fullfile('..\..\Data\Parkinson\',"*.mat"));
n_files = length(filenames);
n_trials = 33;
n_conds = 2;
n_blocks = 3;
% Save mean changes + std of velocity in each condition for each dataset
changes_vel = zeros(n_files, n_conds); 
changes_vel_after = zeros(n_files, n_conds); 
diffs_stim_peak_mean = zeros(n_files, n_conds); 
changes_vel_no_after = zeros(n_files, n_conds); 

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

    %% Loop over every movement
    changes_vel_after_all = [];
    diffs_stim_peak_all = [];
    for i_cond = 1:n_conds
        peaks = [];
        stim = [];
        diffs_target_stim = [];
        diffs_stim_peak = [];
        for i_block=1:n_blocks
            for i_trial=2:n_trials  
                mask = data(:,8) == blocks_cond(i_cond,i_block) & data(:,9) == i_trial;
                data_trial = data(mask, :);

                % Average the velocity over less samples 
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
                % If stimulated save that 
                if ind_stim 
                    stim = cat(1,stim, 1);
                    diff_stim_peak = data_trial(ind_stim,3)-data_trial(ind_peak,3);
                    diff_target_stim = data_trial(ind_target,3)-data_trial(ind_stim,3);
                else
                    stim = cat(1,stim, 0);
                    diff_stim_peak = 100;
                    diff_target_stim = 100;
                end
                
                % Save distance between peak and stimulation 
                diffs_stim_peak = cat(1,diffs_stim_peak, diff_stim_peak);
                % Save distance between stimulation and time on target 
                diffs_target_stim = cat(1,diffs_target_stim, diff_target_stim);
            end
        end
        % For one condition: 
        % Calculate baseline at start from block (first 10 movements) and
        % substract it
        % remove outliers
        peaks = filloutliers(peaks,"linear");
        peaks = peaks - median(peaks(1:20));
        % Get the average change from baseline in velocity 
        changes_vel(i_file, i_cond) = mean(peaks);
        
        % Save also the mean velocity of movements after stimulation 
        ind_after_stim = find(stim == 1) + 1; 
        ind_after_stim = ind_after_stim(ind_after_stim <= length(peaks));
        changes_vel_after(i_file, i_cond) = mean(peaks(ind_after_stim));
        
        % Plot the difference after stim or no stim
        figure;
        t = peaks(ind_after_stim);
        u = peaks(setdiff(1:length(peaks),ind_after_stim));
        histogram(u); hold on; histogram(t); xline(mean(t), "r", "LineWidth", 2); xline(mean(u),"b", "LineWidth", 2); legend(["No stim","Stim"]);
        conds = ["Slow","Fast"];
        title(conds(i_cond));
        % Save the mean velocity of movements after no stimulation 
        changes_vel_no_after(i_file, i_cond) = mean(peaks(setdiff(1:length(peaks),ind_after_stim)));
        
        % Save the peaks after a stimulation and the time difference between
        % before the stim and peak of the previous trial for correlation analysis
        changes_vel_after_all = cat(1,changes_vel_after_all,peaks(ind_after_stim));
        diffs_stim_peak_all = cat(1,diffs_stim_peak_all, filloutliers(diffs_stim_peak(ind_after_stim-1), "linear"));
        
        % Save the median of the time between stimulation and peak
        diffs_stim_peak = diffs_stim_peak(diffs_stim_peak ~= 100); % delete 
        diffs_stim_peak_mean(i_file, i_cond) = mean(filloutliers(diffs_stim_peak, "center"));
    end
    %% 
%     figure;
%     subplot(1,3,1);
%     bar([1, 2], changes_vel_after(i_file, :)); hold on; 
%     set(gca, 'XTickLabel', {"slow" "fast"});
%     subplot(1,3,2);
%     bar([1, 2], changes_vel_no_after(i_file, :)); hold on; 
%     set(gca, 'XTickLabel', {"slow" "fast"});
%     subplot(1,3,3);
%     scatter(changes_vel_after_all,diffs_stim_peak_all); hold on; 
%     r = corrcoef(changes_vel_after_all,diffs_stim_peak_all);
%     title(sprintf("Corr %.2f",r(1,2)));
end
%% Plot the averagee velocity for each condition as a box plot 
figure;
boxplot(changes_vel(:,:),'colors', 'r');
hold on; 
scatter([ones(1,10),ones(1,10)*2],[changes_vel(:,1);changes_vel(:,2)],"black", "filled");
hold on; 
for i_file=1:n_files
    plot(changes_vel(i_file,:), "black");
    hold on;
end
% Test if the conditions are different
[h,p] = ttest(changes_vel(:,2) - changes_vel(:,1));
set(gca, 'XTickLabel', {"Slow" "Fast"});
title(sprintf("%.4f",p));
ylabel("Normalized peak velocity");
