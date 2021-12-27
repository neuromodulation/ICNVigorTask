%% Analyze the behavioural data of the task 
% Summary plot for each participant to gain insight into effect of
% stimulation 

% Get a list of all datasets 
close all;
filenames = dir(fullfile('..\..\Data\Parkinson\',"*.mat"));
n_files = length(filenames);
n_trials = 33;
n_conds = 3;
n_blocks_all = [2,3,3];
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
        blocks_cond = {1:2; 3:5; 9:11};
    else
        blocks_cond = {1:2 ; 9:11; 3:5};
    end
    
    % Create a summary plot for each participant
    FigH = figure('Position', get(0, 'Screensize')); 
    sgtitle(filenames(i_file).name);
    perf = [];
    %% Loop over every movement
    peaks_all = [];
    for i_cond = 1:n_conds
        peaks = [];
        stim = [];
        true_stim = [];
        diffs_target_stim = [];
        diffs_stim_peak = [];
        n_blocks = n_blocks_all(i_cond);
        block_number = cell2mat(blocks_cond(i_cond));
        for i_block=1:n_blocks
            for i_trial=2:n_trials
                
                % Get the data from one trial
                mask = data(:,8) == block_number(i_block) & data(:,9) == i_trial;
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
                
                % Check if the trial should be simulated (based on true
                % peak)
                if length(peaks)> 2 && (all(peaks(end-2:end-1) > peaks(end)) && i_cond-1 == 1 ||...
                    all(peaks(end-2:end-1)< peaks(end)) && i_cond-1 == 2)
                    true_stim = cat(1,true_stim, 1);
                else
                    true_stim = cat(1,true_stim, 0);
                end
                
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
        % For the first two blocks (without stimulation) get the difference
        % between sonsecutive peaks after slow/fast peaks
        if i_cond == 1
            % Get the index of slow and fast peaks 
            slow_ind = []; fast_ind = [];
            for i=3:length(peaks)-1
                if all(peaks(i-2:i-1) > peaks(i)) 
                    slow_ind = cat(1,slow_ind,i);
                elseif all(peaks(i-2:i-1) < peaks(i))
                    fast_ind = cat(1,fast_ind,i);
                end
            end
            % Get the difference in peak velocity between consecutive
            % trials
            diff_slow = peaks(slow_ind) - peaks(slow_ind+1);
            diff_fast = peaks(fast_ind) - peaks(fast_ind+1);
            diffs_baseline = {diff_slow, diff_fast};
        else
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
            subplot(2,3,subplot_indxs(i_cond-1, 1));
            scatter(peaks(ind_after_stim),diffs_stim_peak);
            r = corrcoef(peaks(ind_after_stim),diffs_stim_peak);
            title(conds(i_cond-1) + " " + string(r(1,2)));
            xlabel("Peak velocity of next trial");
            ylabel("Time from peak to stimulation (sec)");

            % Plot the difference in peak velocity for movements after a 
            % a slow/fast movement for stimulated and not stimulated
            % movements
            subplot(2,3,subplot_indxs(i_cond-1,2));
            diff_peak_after_stim = peaks(ind_after_stim-1) - peaks(ind_after_stim);
            diff_peak_no_stim = cell2mat(diffs_baseline(i_cond-1));
            boxplot([diff_peak_after_stim; diff_peak_no_stim],...
                    [ones(length(diff_peak_after_stim),1); ones(length(diff_peak_no_stim),1)*2],...
                    'Labels',["stim","no stim"]);
            title(conds(i_cond-1));
            ylabel("Difference of peak velocity to next trial");

            % Save the peaks normalized to the first 15 movements 
            peaks = peaks - mean(peaks(1:15)); 
            % Average over 5 consecutive movements
            peaks_mean = mean(reshape(peaks(1:end-mod(length(peaks),5)),5,[]),1);
            x = linspace(1,length(peaks),length(peaks_mean));
            peaks_all = cat(1, peaks_all, peaks_mean);

            % Calculate the number of stimulated movements as well as sensitivity
            % and specificity
            perc_stim = sum(stim)/length(stim);
            sens = sum(stim == 1 & true_stim == 1)/sum(true_stim == 1);
            spec = sum(stim == 0 & true_stim == 0)/sum(true_stim == 0);
            perf = cat(1,perf,[perc_stim, sens,spec]*100);
        end
    end
    
    % Plot the normalized change in velocity 
    subplot(2,3,5);
    plot(x,peaks_all(1,:)); hold on; 
    plot(x,peaks_all(2,:)); 
    legend(conds);
    xlabel("Trial Number");
    ylabel("Normalized peak velocity");
    
    % Plot the performance of the task (Stimulation of correct movements)
    subplot(2,3,6);
    perf = round(perf,0);
    b = bar(perf);
    ylabel("Percentage");
    set(b, {'DisplayName'}, {'Stimulated','Sensitivity','Specificity'}')
    legend();
    set(gca, 'XTick', 1:2, 'XTickLabels', {'Slow','Fast'})
    % Add the values 
    width = b.BarWidth;
    for i=1:length(perf(:, 1))
        row = perf(i, :);
        % 0.5 is approximate net width of white spacings per group
        offset = ((width + 0.5) / length(row)) / 2;
        x = linspace(i-offset, i+offset, length(row));
        text(x,max(row-40,10),num2str(row'),'vert','bottom','horiz','center');
    end
    % Save the figure 
    saveas(FigH, sprintf('../../Plots/Dataset%i.png', i_file), 'png');

end