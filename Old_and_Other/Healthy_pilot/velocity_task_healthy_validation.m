
%% Velocity task healthy validation

% Check the performance of the task in regard to several questions: 
% 1. Does the stimulation occur during the movement?
% 2. Do the 16 different movements have different mean velocity? 
% 3. How many fast/slow movements are stimulated?

%% Preparation

% Five conditions
n_par = 8;
n_cond = 5;
n_blocks_cond = 2;
blocks = reshape(1:10,2,5);
train_blocks = 1:2;
n_trials = 32;

%% 1. Does the stimulation occur during the movement? 

mean_dur_all = zeros(1,n_par);
for i_par=1:n_par
    
    % Load the data 
    load(strcat(pwd,'/Data/',sprintf("Participant_%i.mat",i_par)));

    % Compute the duration the stimulation and the time on the target overlap
    % for each trial
    dur_stim_target = [];
    for i_cond=[2 5]
        for i_block=1:n_blocks_cond
            for i_trial=1:n_trials
                mask = data(:,8) == blocks(i_block,i_cond) & data(:,9) == i_trial;
                data_trial = data(mask,:);
                % For trials in which stimulation occured check if on
                % target and stimulation overlapped
                if any(data_trial(:,11)==1)
                    data_stim_during_target = data_trial(data_trial(:,10)==1 & data_trial(:,11)==1,:);
                    if ~isempty(data_stim_during_target)
                        dur_stim_target = [dur_stim_target (data_stim_during_target(end,3) - data_stim_during_target(1,3))];
                    else
                        dur_stim_target = [dur_stim_target 0];
                    end
                end
            end
        end
    end
    
    mean_dur = mean(dur_stim_target);
    fprintf("Participant %i: The stimulation overlaps with the time on the target for a mean of %.2f seconds\n",i_par, mean_dur);
    mean_dur_all(i_par) = mean_dur;
    
end

fprintf("All participants: The stimulation overlaps with the time on the target for %.2f seconds\n", mean(mean_dur_all));

%% 2. Do different movements have different mean velocity?
% Seems as if this is not the case 

i_par = 7;
% Load the data 
load(strcat(pwd,'/Data/',sprintf("Participant_%i.mat",i_par)));
load(strcat(pwd,'/unique_moves.mat'));

% Get the peak velocities for each of the 32 moves
peak_moves = [];
for i_cond=1:n_cond
    for i_block =1:n_blocks_cond
        for i_trial=1:n_trials
            mask_trial = data(:,8) == blocks(i_block,i_cond) & data(:,9) == i_trial;
            peak = max(data(mask_trial,4));
            mask_trial_prev = data(:,8) == blocks(i_block,i_cond) & data(:,9) == i_trial-1;
            pos = [unique(data(mask_trial_prev,12)) unique(data(mask_trial_prev,13)) ...
                                   unique(data(mask_trial,12)) unique(data(mask_trial,13))];
           [~, i_move] = ismember(pos,unique_moves,'rows');
           peak_moves = cat(1,peak_moves,[i_move peak]);
        end
    end
end

% Check for statistically different peak velocity
peak_moves_ordered = zeros(10,32);
for m=1:32
    peak_moves_ordered(:,m) = peak_moves(peak_moves(:,1)==m,2);
end
[p,tbl,stats] = anova1(peak_moves_ordered);
c = multcompare(stats);

disp(cat(2,(1:32)',unique_moves));

%% 3. How many slow/fast movements are stimulated

% Five conditions
n_par = 8;
n_cond = 5;
n_blocks_cond = 2;
blocks = reshape(1:10,2,5);
train_blocks = 1:2;
n_trials = 32;


%subplot_numbers = reshape(1:24,3,8);
subplot_numbers = reshape(1:16,2,8);
conditions = [2 4];
n_bins = n_trials*2;
condition_names_slow_first = ["Stimulation slow", "Stimulation fast"];
condition_names_fast_first = ["Stimulation fast", "Stimulation slow"];
stim_stats = zeros(n_par,4); % Save percent of stimulated movements/misses/false alarms for each subject
for i_par=1:n_par
    
    % Load the data
    load(strcat(pwd,'/Data/',sprintf("%i/Participant_%i.mat",i_par,i_par)));
    load(strcat(pwd,'/Data/',sprintf("%i/Participant_%i_info.mat",i_par,i_par)));
    slow_first = more_info(1);
    threshold_slow = more_info(2);
    threshold_fast = more_info(3);
    
    % Determine the order of the stimulation conditions
    if slow_first
        condition_names = condition_names_slow_first;
    else
        condition_names = condition_names_fast_first;
    end
    
    for i_cond = 1:length(conditions)
        peak_vel = zeros(n_blocks_cond,n_trials);
        stim = zeros(n_blocks_cond,(n_trials));
        for i_block=1:n_blocks_cond
            for i_trial=1:n_trials
                % Save the peak velocity of the trial and whether it was
                % stimulate
                mask = data(:,8)==blocks(i_block,conditions(i_cond)) & data(:,9)==i_trial;
                peak_vel(i_block,i_trial) = max(data(mask,4));
                stim(i_block,i_trial) = logical(any(data(mask,11)));
            end         
        end
        % Plot the movements and the thresholds (different colors for
        % stimulated movements)
        subplot(n_par,2,subplot_numbers(i_cond, i_par));
        stim = logical(stim);
        histogram(peak_vel(~stim),n_bins,'FaceColor','b');
        hold on;
        if slow_first && i_cond == 1 || ~slow_first && i_cond ==2
            histogram(peak_vel(stim),n_bins,'FaceColor','g');
            stim_percent = sum(stim,'all')/n_bins;
            fa_percent = sum(peak_vel >= threshold_slow & stim,'all')/n_bins;
            title(condition_names(i_cond) + sprintf(" stim=%.2f%% FA=%.2f %%",stim_percent,fa_percent));
            % Save the percentages for group analysis
            stim_stats(i_par,1:2) = [stim_percent, fa_percent];
        else
            histogram(peak_vel(stim),n_bins,'FaceColor','r');
            stim_percent = sum(stim,'all')/n_bins;
            misses_percent = sum(peak_vel >= threshold_fast & ~stim,'all')/n_bins;
            title(condition_names(i_cond) + sprintf(" stim=%.2f%% misses=%.2f %%",stim_percent,misses_percent));
             stim_stats(i_par,3:4) = [stim_percent, misses_percent];
        end
        set(gca,'xtick',[])
        set(gca,'xticklabel',[])
        set(gca,'ytick',[])
        set(gca,'yticklabel',[])
        xline(threshold_slow,'black','LineWidth',2);
        xline(threshold_fast, 'black','LineWidth',2);
        xlim([min(min(peak_vel,[],'all'),threshold_slow)-100,max(max(peak_vel,[],'all'),threshold_fast)+100]);
    end
end

% Save the plot
set(gcf, 'Position', get(0, 'Screensize'));
mean_stim_stats = mean(stim_stats,1); % Add group average
sgtitle(sprintf("Group average: Stim slow = %.2f %%, False alarms = %.2f %%, Stim fast = %.2f %%, Misses = %.2f %%",mean_stim_stats));
saveas(gcf,strcat(pwd ,"\Plots\stim_stats_per_par.jpg"));
