%% Analyze the behavioural data of the task 
% Summary plot for each participant to gain insight into effect of
% stimulation 

%% Get a list of all datasets 
close all;
filenames = dir(fullfile('..\..\Data\Parkinson_Pilot\',"*.mat"));
n_files = length(filenames);
n_trials = 33;
n_conds = 2;
n_blocks = 3;
conds = ["Slow","Fast"];

%% Loop through the datasets and create a summary plot for each 
corrs = [];
three_after_stim_all = [];
start_end_vel = [];
perc_stim_all = [];
for i_file=1:n_files
    
    % Load the data from one recording
    load(strcat('..\..\Data\Parkinson_Pilot\',filenames(i_file).name));
    data = struct.data; 
    options = struct.options; 
    % Between participants the naming of parameters changed --> rename if necessary 
    if ~any(fieldnames(options) == "cond")
        options.cond = options.slow_first;
    end
    
    % Change the block order accordingly such that slow always comes first
    if options.cond % Cond = 1 = Slow/First
        blocks_cond = [3:5; 9:11];
        blocks_cond_recov = [6:8; 12:14];
    else % Cond = 0 = First/Slow
        blocks_cond = [9:11; 3:5];
        blocks_cond_recov = [12:14; 6:8];
    end
    
    % Create a summary plot for each participant
    FigH = figure('Position', get(0, 'Screensize')); 
    sgtitle(filenames(i_file).name);
    perf = [];
    three_after_stim = [];
    diffs_stim_peak_all = [];
    diffs_stim_peak_all_n = [];
    baselines = [];
    
    %% Loop over the conditions Slow/Fast
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
        % Loop over blocks
        for i_block=1:n_blocks
            % Loop over trials 
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
                
                % Check if trial was stimulated
                ind_stim = find(data_trial(:,11) == 1, 1);
                
                % Save whether trial was stimulated and the time between
                % peak and stimulation
                if ind_stim 
                    stim = cat(1,stim, 1);
                    % column 3 = time points
                    diffs_stim_peak = cat(1,diffs_stim_peak, data_trial(ind_stim,3)-data_trial(ind_peak,3));                
                else
                    stim = cat(1,stim, 0);
                end
            end
        end
        
        %% After all blocks from one condition are processed 
        % Replace outliers with the linear method
        peaks = filloutliers(peaks,"linear");
        diffs_stim_peak = filloutliers(diffs_stim_peak,"linear");
        
        %% 
%         figure; 
%         plot(peaks); hold on; 
%         idx_stim = find(stim == 1);
%         for i = 1:size(idx_stim,1)
%             xline(idx_stim(i)); hold on;
%         end

        %% Scatter plot
        
        % Get the indexes of stimulated trials
        inds_stim = find(stim == 1); 
        % If the last movement was stimulated delete the entry
        % as we want to look at the trials after stimulation
        if any(inds_stim == length(peaks))
            inds_stim = inds_stim(1:end-1);
            diffs_stim_peak = diffs_stim_peak(1:end-1);
        end
        % Get the index of trials after stimulation
        inds_after_stim = inds_stim + 1;

        % Plot the scatter plot of the velocity of the movement after
        % stimulation and the time between the peak and stimulation
        subplot(2,4,i_cond);
        % Compute the difference in peak velocity between stimulated and
        % subsequent trial
        diff_stim_after = peaks(inds_after_stim) - peaks(inds_stim);
        % Take the absolute value of the time difference between peak and
        % stimulation
        diffs_stim_peak = abs(diffs_stim_peak);
  
        scatter(diff_stim_after,diffs_stim_peak);
        
        % Compute, save and plot the correlation coefficient
        r = corrcoef(diff_stim_after,abs(diffs_stim_peak));
        corrs = cat(1,corrs,r(1,2));
        title(conds(i_cond) + " " + string(r(1,2)));
        xlabel("Diff Peak velocity next trial-stim");
        ylabel("Time from peak to stimulation (sec)");
        
        % Save the time difference between stim and peak 
        diffs_stim_peak_all = cat(1, diffs_stim_peak_all,diffs_stim_peak);
        % Save the length of the array in order to use boxplot later
        diffs_stim_peak_all_n = cat(1, diffs_stim_peak_all_n,ones(length(diffs_stim_peak),1)*i_cond);

        %%  Velocity-Time plot preparation
        % Compute and save the baseline 
        baseline = mean(peaks(5:15));
        baselines = cat(1,baselines,baseline);
        % Normalize the data
        peaks = peaks - baseline; 
        % Average over 5 consecutive movements
        peaks_mean = mean(reshape(peaks(1:end-mod(length(peaks),5)),5,[]),1);
        x = linspace(1,length(peaks),length(peaks_mean));
        % Save the normalized and averaged data 
        peaks_all = cat(1, peaks_all, peaks_mean);
        % Save the raw peaks 
        peaks_all_raw = cat(2, peaks_all_raw, peaks);

        %% Performance plot preparation
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
        
        %% Next three trials plot preparation
        % Get the index of stimulated movements after which at least 3
        % trials follow
        inds_stim = find(stim == 1); 
        inds_stim = inds_stim(inds_stim <= length(stim) - 3);
        % Get always the three movements after a stimulation 
        peaks_after_stim = [];
        for i=1:length(inds_stim)
            peaks_after_stim = cat(2,peaks_after_stim, peaks(inds_stim(i)+1:inds_stim(i)+3));
        end
        % Average over all trials and substract the peak of the
        % stimulation
        mean_peaks_after_stim = mean(peaks_after_stim - peaks(inds_stim).', 2);
        % Save it 
        three_after_stim = cat(2, three_after_stim, mean_peaks_after_stim);
        
        % Get the index of NOT stimulated fast/slow movements after which at least 3
        % trials follow
        inds_slow_fast = find(other_stim == 1); 
        inds_slow_fast = inds_slow_fast(inds_slow_fast <= length(stim) - 3);
        % Get always the three movements after a stimulation 
        peaks_after_slow_fast = [];
        for i=1:length(inds_slow_fast)
            peaks_after_slow_fast = cat(2,peaks_after_slow_fast, peaks(inds_slow_fast(i)+1:inds_slow_fast(i)+3));
        end
        % Average over all stimulations and substract the peak of the
        % stimulation
        mean_peaks_after_slow_fast = mean(peaks_after_slow_fast - peaks(inds_slow_fast).', 2);
        % Save it 
        three_after_stim = cat(2, three_after_stim, mean_peaks_after_slow_fast);
    end
    perc_stim_all = cat(2,perc_stim_all,perf(:,1));
    
    %% Next three trials plot
    % Plot the difference of peak velocity of the three trials after
    % stimulation to the stimulated trial
    subplot(2,4,3);
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
    three_after_stim_all = cat(3,three_after_stim_all,three_after_stim);

    %% Time difference peak stim box plot
    % Plot the time difference between stim and peak for both conditions
    % in a box plot 
    subplot(2,4,4);
    boxplot(diffs_stim_peak_all, diffs_stim_peak_all_n);
    set(gca, 'XTickLabel', {"Slow" "Fast"});
    ylabel("Time from peak to stim (sec)");
    
    %% Velocity-Time plot
    % Plot the normalized change in velocity 
    subplot(2,4,5);
    plot(x,peaks_all(1,:), "b"); hold on; 
    plot(x,peaks_all(2,:), "r"); 
    legend(conds);
    xlabel("Trial Number");
    ylabel("Normalized peak velocity");
    title("Stimulation");
    
    %% Analyze the recovery blocks
    % Get the peak velocities of the trials in the recovery blocks 
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
        
        % Replace outliers 
        peaks = filloutliers(peaks,"linear");
        % Normalize the peaks to the movements 5-15 of the
        % stimulation condition 
        peaks = peaks - baselines(i_cond); 
        % Average over 5 consecutive movements
        peaks_mean = mean(reshape(peaks(1:end-mod(length(peaks),5)),5,[]),1);
        x = linspace(1,length(peaks),length(peaks_mean));
        % Save the normalized/averaged and raw peaks
        peaks_all_recov = cat(1, peaks_all_recov, peaks_mean);
        peaks_all_raw_recov = cat(2, peaks_all_raw_recov, peaks);
    end
    
    %% Velocity-Time recovery plot
    % Plot the normalized change in velocity for the recovery blocks
    subplot(2,4,6);
    plot(x,peaks_all_recov(1,:), "b"); hold on; 
    plot(x,peaks_all_recov(2,:), "r"); 
    legend(conds);
    xlabel("Trial Number");
    ylabel("Normalized peak velocity");
    title("Recovery - No Stimulation");
    
    %% Velocity Start End stimulation recovery plot
    % Plot average movement velocity at start/end of stimulation/recovery
    % blocks
    subplot(2,4,7);
    % Compute the average velocity at start and end of stimulation and
    % recovery blocks
    means = [mean(peaks_all(:,2:3),2),mean(peaks_all(:,end-1:end),2),...
    mean(peaks_all_recov(:,2:3),2),mean(peaks_all_recov(:,end-1:end),2)];
    plot(means.');
    hold on;
    scatter(1:4,means(1,:),"blue","filled");
    hold on;
    scatter(1:4,means(2,:),"red","filled");
    ylabel("Normalized peak velocity pixel/sec");
    set(gca, 'XTick', 1:4, 'XTickLabels', {'5-15 Stim', '85-95 Stim', 'Recov', 'Recov'})
    % Save for group plots
    start_end_vel = cat(3,start_end_vel,means);
    % Add the unnormalized lines
    hold on;
    plot(means(1,:)+baselines(1),'--','Color','b');
    hold on;
    plot(means(2,:)+baselines(2),'--','Color','r');
    hold on;
    scatter(1:4,means(1,:)+ baselines(1),"blue","filled");
    hold on;
    scatter(1:4,means(2,:)+baselines(2),"red","filled");
    ylabel("Peak velocity pixel/sec");
    set(gca, 'XTick', 1:4, 'XTickLabels', {'5-15 Stim', '90-95 Stim', 'Recov', 'Recov'})
    
    %% Performance plot
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
    %saveas(FigH, sprintf('../../Plots/Dataset%i.png', i_file), 'png');
    close all;
end

%% All datasets Velocity Start End stimulation recovery plot
FigA = figure('Position', get(0, 'Screensize')); 
subplot(1,3,1);
means = mean(start_end_vel,3);
plot(means.');
%legend(["Slow","Fast"]);
hold on;
scatter(1:4,means(1,:),"blue","filled");
hold on;
scatter(1:4,means(2,:),"red","filled");
ylabel("Normalized peak velocity pixel/sec");
set(gca, 'XTick', 1:4, 'XTickLabels', {'5-15 Stim', '85-95 Stim', 'Recov', 'Recov'})


%% All datasets correlation 
subplot(1,3,2);
boxplot([corrs(1:2:end); corrs(2:2:end)],[ones(10,1);ones(10,1)*2]);
set(gca, 'XTickLabel', {"Slow" "Fast"});
ylabel("Correlation coefficient");

%% All datasets Next three trials plot
subplot(1,3,3);
three_after_stim = mean(three_after_stim_all,3);
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
legend(["Slow" "Fast no stim" "Fast" "Slow no stim"]);
ylabel("Av. difference of peak velocity to stim trial");
xlabel("Trial number after stim");
saveas(FigA, '../../Plots/AllDatasets.png');

%%
scatter([ones(1,10), ones(1,10)*2],perc_stim_all(:) ,'red', 'filled'); 
hold on;
boxplot(perc_stim_all.');
set(gca, 'XTick', 1:2, 'XTickLabels', {'Slow' 'Fast'})
ylabel("% Stimulated movements");

