%% Analyze the behavioural data of the task 
% Summary plot for each participant to gain insight into effect of
% stimulation 

% Get a list of all datasets 
close all;
filenames = dir(fullfile('..\..\Data\Parkinson\',"*.mat"));
n_files = length(filenames);
n_trials = 33;
n_conds = 2;
n_blocks = 3;
conds = ["Slow","Fast"];
subplot_indxs = [1 2; 3 4];

%%
zscores = [];
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
        blocks_cond_recov = [6:8; 12:14];
    else
        blocks_cond = [9:11; 3:5];
        blocks_cond_recov = [12:14; 6:8];
    end
    
    % Create a summary plot for each participant
    FigH = figure('Position', get(0, 'Screensize')); 
    sgtitle(filenames(i_file).name);
    perf = [];
    three_after_stim = [];
    diffs_stim_peak_all = [];
    diffs_stim_peak_all_i = [];
    baselines = [];
    %% Loop over every movement
    peaks_all = [];
    peaks_all_raw = [];
    for i_cond = 1:n_conds
        % Save the peak and whether a move was stimulated
        peaks = [];
        stim = [];
        % save if move was slow/fast
        slow = [];
        fast = [];
        % save sec between peak and stim
        diffs_stim_peak = [];
        for i_block=1:n_blocks
            for i_trial=2:n_trials
                
                % Get the data from one trial
                mask = data(:,8) == blocks_cond(i_cond,i_block) & data(:,9) == i_trial;
                data_trial = data(mask, :);
            
                % Find the peak 
                [peak,ind_peak] = max(data_trial(:,4));
                peaks = cat(1,peaks, peak);
                
                % Check if the trial was fast/slow
                if length(peaks)> 2 && (all(peaks(end-2:end-1) < peaks(end)))
                    fast = cat(1,fast, 1);
                    slow = cat(1,slow,0);
                elseif length(peaks)> 2 && (all(peaks(end-2:end-1) > peaks(end)))
                    slow = cat(1,slow, 1);
                    fast = cat(1,fast, 0);
                else
                    slow = cat(1,slow,0);
                    fast = cat(1,fast,0);
                end
                
                % Check if stimulated
                ind_stim = find(data_trial(:,11) == 1, 1);
                
                % Save whether trial was stimulated and the time between
                % peak/stimulation and stimulation/target
                if ind_stim 
                    stim = cat(1,stim, 1);
                    diffs_stim_peak = cat(1,diffs_stim_peak, data_trial(ind_stim,3)-data_trial(ind_peak,3));                
                else
                    stim = cat(1,stim, 0);
                end
            end
        end
        % After all blocks from one condition are processed 
        % Replace outliers with the linear method
        peaks = filloutliers(peaks,"linear");
        diffs_stim_peak = filloutliers(diffs_stim_peak,"linear");

        % Get the indexes of the movements after stimulation
        inds_stim = find(stim == 1); 
        % If the last movement was stimulated delete the entry
        if any(inds_stim == length(peaks))
            inds_stim = inds_stim(1:end-1);
            diffs_stim_peak = diffs_stim_peak(1:end-1);
        end
        inds_after_stim = inds_stim + 1;

        % Plot the scatter plot of the velocity of the movement after
        % stimulation and the time between the peak and stimulation
        subplot(2,4,i_cond);
        diff_stim_after = peaks(inds_after_stim) - peaks(inds_stim);
        scatter(diff_stim_after,diffs_stim_peak);
        r = corrcoef(diff_stim_after,diffs_stim_peak);
        title(conds(i_cond) + " " + string(r(1,2)));
        xlabel("Diff Peak velocity next trial-stim");
        ylabel("Time from peak to stimulation (sec)");
        % Save the time difference between stim and peak 
        diffs_stim_peak_all = cat(1, diffs_stim_peak_all,diffs_stim_peak);
        diffs_stim_peak_all_i = cat(1, diffs_stim_peak_all_i,ones(length(diffs_stim_peak),1)*i_cond);

        % Save the peaks normalized to the first 15 movements 
        baseline = mean(peaks(5:15));
        baselines = cat(1,baselines,baseline); % Save baseline for recovery plot
        peaks = peaks - baseline; 
        % Average over 5 consecutive movements
        peaks_mean = mean(reshape(peaks(1:end-mod(length(peaks),5)),5,[]),1);
        x = linspace(1,length(peaks),length(peaks_mean));
        peaks_all = cat(1, peaks_all, peaks_mean);
        peaks_all_raw = cat(2, peaks_all_raw, peaks);

        % Calculate the number of stimulated movements as well as sensitivity
        % and specificity
        if i_cond == 1
            true_stim = slow;
            other_stim = fast;
        elseif i_cond == 2
            true_stim = fast;
            other_stim = slow;
        end
        perc_stim = sum(stim)/length(stim);
        sens = sum(stim == 1 & true_stim == 1)/sum(true_stim == 1);
        spec = sum(stim == 0 & true_stim == 0)/sum(true_stim == 0);
        perf = cat(1,perf,[perc_stim, sens,spec]*100);
        
        % Get the index of stimulated movements after which at least 3
        % trials follow
        inds_stim = find(stim == 1); 
        inds_stim = inds_stim(inds_stim <= length(stim) - 3);
        % Get always the three movements after a stimulation 
        peaks_after_stim = [];
        for i=1:length(inds_stim)
            peaks_after_stim = cat(2,peaks_after_stim, peaks(inds_stim(i)+1:inds_stim(i)+3));
        end
        % Average over all stimulations and substract the peak of the
        % stimulation
        mean_peaks_after_stim = mean(peaks_after_stim - peaks(inds_stim).', 2);
        % Save it 
        three_after_stim = cat(2, three_after_stim, mean_peaks_after_stim);
        
        % Get the index of not stimulated fast/slow movements after which at least 3
        % trials follow
        inds_stim = find(other_stim == 1); 
        inds_stim = inds_stim(inds_stim <= length(stim) - 3);
        % Get always the three movements after a stimulation 
        peaks_after_stim = [];
        for i=1:length(inds_stim)
            peaks_after_stim = cat(2,peaks_after_stim, peaks(inds_stim(i)+1:inds_stim(i)+3));
        end
        % Average over all stimulations and substract the peak of the
        % stimulation
        mean_peaks_after_stim = mean(peaks_after_stim - peaks(inds_stim).', 2);
        % Save it 
        three_after_stim = cat(2, three_after_stim, mean_peaks_after_stim);
    end
    subplot(2,4,3);
    % Plot the difference of peak velocity of the three trials after
    % stimulation to the stimulated trial
    for i=1:4
        if i == 1
            plot(three_after_stim(:,i), 'b');
        elseif i == 2
            plot(three_after_stim(:,i),'--','Color','r');
        elseif i == 3
            plot(three_after_stim(:,i), 'r');
        elseif i == 4
            plot(three_after_stim(:,i), '--','Color','b');
        end
        hold on;
    end
    %legend(["Slow" "Fast no stim" "Fast" "Slow no stim"]);
    title("Av. difference of peak velocity to stim trial");
    xlabel("Trial number after stim");
    
    % Compute teh standard deviation of the peaks in the first two blocks
    peaks = [];
    stim = [];
    for i_block=[2]
        for i_trial=2:n_trials
            % Get the data from one trial
            mask = data(:,8) == i_block & data(:,9) == i_trial;
            data_trial = data(mask, :);

            % Find the peak 
            [peak,ind_peak] = max(data_trial(:,4));
            peaks = cat(1,peaks, peak);
        end
    end
    peaks = filloutliers(peaks,"linear");
    standdev = std(peaks);
    
    
    % Plot the time difference between stim and peak for both conditions
    % in a box plot 
    subplot(2,4,4);
    boxplot(diffs_stim_peak_all,diffs_stim_peak_all_i);
    set(gca, 'XTickLabel', {"Slow" "Fast"});
    ylabel("Time from peak to stim (sec)");
    
    % Plot the normalized change in velocity 
    subplot(2,4,5);
    plot(x,peaks_all(1,:), "b"); hold on; 
    plot(x,peaks_all(2,:), "r"); 
    legend(conds);
    xlabel("Trial Number");
    ylabel("Normalized peak velocity");
    title("Stimulation");
    
    % Analyze the recovery blocks
    peaks_all_recov = [];
    peaks_all_raw_recov = [];
    for i_cond = 1:n_conds
        peaks = [];
        for i_block=1:n_blocks
            for i_trial=2:n_trials
                % Get the data from one trial
                mask = data(:,8) == blocks_cond_recov(i_cond,i_block) & data(:,9) == i_trial;
                data_trial = data(mask, :);
            
                % Find the peak 
                [peak,ind_peak] = max(data_trial(:,4));
                peaks = cat(1,peaks, peak);
            end
        end
        % Normalize the peaks
        peaks = filloutliers(peaks,"linear");
        % Save the peaks normalized to the first 15 movements 
        peaks = peaks - baselines(i_cond); 
        % Average over 5 consecutive movements
        peaks_mean = mean(reshape(peaks(1:end-mod(length(peaks),5)),5,[]),1);
        x = linspace(1,length(peaks),length(peaks_mean));
        peaks_all_recov = cat(1, peaks_all_recov, peaks_mean);
        peaks_all_raw_recov = cat(2, peaks_all_raw_recov, peaks);
    end
    % Plot the normalized change in velocity 
    subplot(2,4,6);
    plot(x,peaks_all_recov(1,:), "b"); hold on; 
    plot(x,peaks_all_recov(2,:), "r"); 
    legend(conds);
    xlabel("Trial Number");
    ylabel("Normalized peak velocity");
    title("Recovery - No Stimulation");
    
    % Z-score the peak values using the baseline and the std of the first
    % two blocks
    peaks_all_zscore = (peaks_all_raw)/standdev;
    peaks_all_recov_zscore = (peaks_all_raw_recov)/standdev;
    % Plot the mean z-score
    subplot(2,4,7);
    plot_data = [mean(peaks_all_zscore,1); mean(peaks_all_recov_zscore,1)];
    plot_error = [std(peaks_all_zscore,1); std(peaks_all_recov_zscore,1)];
    b = bar(plot_data);
    hold on;
    ylabel("zscore");
    set(b, {'DisplayName'}, {'Slow','Fast'}')
    legend();
    set(gca, 'XTick', 1:2, 'XTickLabels', {'Stim','Recovery'})
    % Add error bars
    % Calculate the number of groups and number of bars in each group
    [ngroups,nbars] = size(plot_data);
    % Get the x coordinate of the bars
    x = nan(nbars, ngroups);
    for i = 1:nbars
        x(i,:) = b(i).XEndPoints;
    end
    % Plot the errorbars
    errorbar(x',plot_data,plot_error,'k','linestyle','none');
    % Save the zscores for one file 
    zscores = cat(3,zscores,plot_data);
    
    % Plot the performance of the task (Stimulation of correct movements)
    subplot(2,4,8);
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

%% Plot the mean z-scores of all files 
% Z-score the peak values using the baseline and the std of the first
% two blocks
figure;
plot_data = mean(zscores,3);
plot_error = std(zscores,[],3);
b = bar(plot_data);
hold on;
ylabel("zscore");
set(b, {'DisplayName'}, {'Slow','Fast'}')
legend();
set(gca, 'XTick', 1:2, 'XTickLabels', {'Stim','Recovery'})
% Add error bars
% Calculate the number of groups and number of bars in each group
[ngroups,nbars] = size(plot_data);
% Get the x coordinate of the bars
x = nan(nbars, ngroups);
for i = 1:nbars
    x(i,:) = b(i).XEndPoints;
end
% Plot the errorbars
errorbar(x',plot_data,plot_error,'k','linestyle','none');
% Save the zscores for one file 
zscores = cat(3,zscores,plot_data);
