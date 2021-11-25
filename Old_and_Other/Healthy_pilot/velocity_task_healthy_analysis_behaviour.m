
%% Velocity task healthy analysis - Behaviour
% Analyse the behavioural data from the pilot of the velocity task (healthy
% participants) 

% Outcome measures: 
% 1. Peak velocity
% 2. Acceleration
% 3. Trial length (From beginning of movement)
% 4. Tortuosity (directness of path)
% 5. Movement initialization

% Mean training vs. mean stimulation/block peak velocity/trial
% length/acceleration/tortuisity --> Multiple comparison tests to get a statistical result

% Visualization of the difference by plotting the difference between mean
% training and trial vice peak velocity/trial length/acceleration/tortuisity over trials 


%% Preparation

% Five conditions
n_cond = 5;
n_blocks_cond = 2;
n_trials = 32;
blocks = reshape(1:10,2,5);
n_blocks = max(blocks,[],'all');
train_blocks = 1:2;
n_par = 7;
all_out_measures_names = ["Peak velocity", "peak acceleration", "movement duration", "tortuosity", "movement initiation"];
n_out_mes = size(all_out_measures_names, 2);
conditions_names = {'Stimulation slow', 'Recovery slow', 'Stimulation fast', 'Recovery fast'};

%% Compute and visualize the outcome measures (z-score)

% Initalize an array to store all the outcome measures for all participants
outcome_measures = zeros(n_par,n_out_mes,n_cond,n_blocks_cond,n_trials);
    
% Initialize the matrix that will store the z-scores for all participants
z_scores_mes = zeros(n_par,n_out_mes,n_cond-1);

for i_par=1:n_par
    
    % Load the data from one participant
    load(strcat(pwd,'/Data/',sprintf("Participant_%i.mat",i_par)));
    load(strcat(pwd,'/Data/',sprintf("Participant_%i_info.mat",i_par)));
    slow_first = more_info(1);
    
    for i_cond=1:n_cond
        for i_block=1:n_blocks_cond  
            for  i_trial=1:n_trials
                
                % Get the data from one trial
                mask = data(:,8) == blocks(i_block,i_cond) & data(:,9) == i_trial;
                data_trial = data(mask,:);
                
                % Get the peak velocity
                outcome_measures(i_par,1,i_cond,i_block,i_trial) = max(data_trial(:,4));
                
                % Get the peak acceleration
                acc = diff(data_trial(:,4));
                outcome_measures(i_par,2,i_cond,i_block,i_trial) = max(acc);
                
                % Get the movement length (duration)
                data_time_move_start = data_trial(data_trial(:,4)>100,3);
                data_time_move_end = data_trial(data_trial(:,10) == 1,3);
                outcome_measures(i_par,3,i_cond,i_block,i_trial) = data_time_move_end(1)-data_time_move_start(1);
                
                % Get the tortuosity (directness of path: path length
                % divided by shortest path length)
                pos_trial_prev = unique(data(data(:,8) == blocks(i_block,i_cond) & data(:,9) == i_trial-1, 12:13), 'rows');
                pos_trial = unique(data_trial(:,12:13),'rows');
                min_path = sqrt((pos_trial_prev(:,1)-pos_trial(:,1)).^2 + (pos_trial_prev(:,2)-pos_trial(:,2)).^2);
                x_path = sum(diff(data_trial(data_trial(:,4)>20 & data_trial(:,10)==0,1)));
                y_path = sum(diff(data_trial(data_trial(:,4)>20 & data_trial(:,10)==0,2)));
                path = sqrt(x_path.^2 + y_path.^2);
                outcome_measures(i_par,4,i_cond,i_block,i_trial) = path/min_path;
                
                % Get the time needed for movement initialization
                outcome_measures(i_par,5,i_cond,i_block,i_trial) =  data_time_move_start(1) - data_trial(1,3);
            end
        end
    end
end
    
% If the first stimulation was fast change the order of the conditions
if ~slow_first 
    outcome_measures = outcome_measures(:,:,[1 4 5 2 3],:,:);
end

% Flatten the two blocks of one condition to 1 long block 
outcome_measures_re = reshape(permute(outcome_measures,[1,2,3,5,4]),n_par,n_out_mes,n_cond,n_blocks_cond*n_trials);

for i_par=1:n_par
    
    % For each outcome measure compute the z-score of each condition
    
    for i_mes=1:n_out_mes

        % Compute the mean and standard deviation of the training
        % trials
        stat_train = [mean(outcome_measures_re(i_par,i_mes,1,:)) std(outcome_measures_re(i_par,i_mes,1,:))];

        % Compute the mean z-score for each condition (deviation from the
        % training mean in units of the standard deviation)
        z_scores_mes(i_par,i_mes,:) = mean((squeeze(outcome_measures_re(i_par,i_mes,2:end,:)) - stat_train(1)) / stat_train(2),2);
    end
    
    % Compute the p-values to the z-scores (use a two-tailed test)
    p_values = normcdf(squeeze(z_scores_mes(i_par,:,:)),'upper');
    
    % For each participant plot the z-scores for each measure grouped by the condition
    fig = bar(squeeze(z_scores_mes(i_par,:,:)));
    set(gca,'xticklabel',all_out_measures_names,'FontSize', 18);
    legend( conditions_names{:});
    ylabel("Z-score",'FontSize', 18);
    title(sprintf("Participant %i",i_par));
    % Add stars if the p-value is below 0.05
    for i_cond = 1:n_cond-1
        xtips = fig(i_cond).XEndPoints;
        ytips = fig(i_cond).YEndPoints;
        labels = strings(n_out_mes,1);
        labels(p_values(:,i_cond) < 0.05) = "*";
        labels(p_values(:,i_cond) >= 0.05) = "";
        text(xtips,ytips,labels,'HorizontalAlignment','center',...
        'VerticalAlignment','bottom','FontSize', 18)
    end
    % Save the figure for each participant
    set(gcf, 'Position', get(0, 'Screensize'));
    saveas(gcf,strcat(pwd ,'\Plots\',  sprintf("Par_%i_z_score.jpg",i_par)));

end

% Compute the mean z scores and the according p values over all participants 
z_scores_mean_par = squeeze(mean(z_scores_mes,1));
p_values_mean_par = 2*normcdf(z_scores_mean_par,'upper');
    
% For each participant plot the z-scores for each measure grouped by the condition
figure;
fig = bar(z_scores_mean_par);
set(gca,'xticklabel',all_out_measures_names,'FontSize', 18);
legend( conditions_names{:});
ylabel("Z-score",'FontSize', 18);
title("Mean Participants");
% Add stars if the p-value is below 0.05
for i_cond = 1:n_cond-1
    xtips = fig(i_cond).XEndPoints;
    ytips = fig(i_cond).YEndPoints;
    labels = strings(n_out_mes,1);
    labels(p_values_mean_par(:,i_cond) < 0.05) = "*";
    labels(p_values_mean_par(:,i_cond) >= 0.05) = "";
    text(xtips,ytips,labels,'HorizontalAlignment','center',...
    'VerticalAlignment','bottom','FontSize', 18)
end

% Save the figure
set(gcf, 'Position', get(0, 'Screensize'));
saveas(gcf,strcat(pwd ,"\Plots\mean_par_z_score.jpg"));

%% Visualize the trial vice outcome measures 

% For each participant generate a figure showing the difference between the
% training mean and the outcome measure of the trial 
subplot_indexes = reshape(1:10,2,5);
trials = 1:n_trials*2;
cond_names = ["Stimulation","Recovery"];
diff_outcome_measures = zeros(n_par,n_out_mes,n_cond-1,n_trials*2);
for i_par=1:n_par
    figure;
    for i_mes=1:n_out_mes
        % Compute the difference of the outcome measure to the training
        % mean
        par_mes_data = squeeze(outcome_measures_re(i_par,i_mes,:,:));
        diff = par_mes_data(2:end,:) - mean(par_mes_data(1,:));
        % Save it to later visualize the group trial vice difference
        diff_outcome_measures(i_par,i_mes,:,:) = diff;
        % Plot the trial vice difference for the stimulation and recovery
        % blocks in two plots
        for j=1:2
            subplot(n_out_mes,2,subplot_indexes(j,i_mes));
            plot(trials,diff(1+j-1,:),trials,diff(3+j-1,:),'LineWidth',4);
            xlim([min(trials),max(trials)]);
            % Add legend and labels (not for all to have minimal redundance
            % in the figure)
            if j==1
                ylabel(all_out_measures_names(i_mes),"FontSize",12);
            end
            if i_mes < n_out_mes
                set(gca,'xtick',[])
                set(gca,'xticklabel',[])
                if i_mes == 1
                    legend("Stimulation slow","Stimulation fast");
                    title(cond_names(j));
                end
            else
                xlabel("Trial number");
            end
        end
    end
    sgtitle(sprintf("Participant %i: Difference to mean training",i_par));
    % Save the plot
    set(gcf, 'Position', get(0, 'Screensize'));
    saveas(gcf,strcat(pwd ,'\Plots\',  sprintf("Par_%i_trial_vice.jpg",i_par)));

end

% Plot the trial vice difference of outcome measures for the average
% population
figure;
mean_diff = squeeze(mean(diff_outcome_measures,1));
for i_mes=1:n_out_mes
    for j=1:2
        subplot(n_out_mes,2,subplot_indexes(j,i_mes));
        diff = squeeze(mean_diff(i_mes,:,:));
        plot(trials,diff(1+j-1,:),trials,diff(3+j-1,:),'LineWidth',4);
        hold on
        xlim([min(trials),max(trials)]);
        % Add the min and max value of all participants in one trial as a
        % shaded area
        diff_mes_all = squeeze(diff_outcome_measures(:,i_mes,:,:));
        min_max_shaded_slow = [min(squeeze(diff_mes_all(:,1+j-1,:)),[],1); max(squeeze(diff_mes_all(:,1+j-1,:)),[],1)];
        min_max_shaded_fast = [min(squeeze(diff_mes_all(:,3+j-1,:)),[],1); max(squeeze(diff_mes_all(:,3+j-1,:)),[],1)];
        x = [trials, fliplr(trials)];
        y_slow = [min_max_shaded_slow(1,:), fliplr(min_max_shaded_slow(2,:))];
        y_fast = [min_max_shaded_fast(1,:), fliplr(min_max_shaded_fast(2,:))];
        fill1 = fill(x, y_slow, 'b');
        set(fill1,'facealpha',.3);
        fill2 =fill(x, y_fast, 'r');
        set(fill2,'facealpha',.3);
        % Add legend and labels (not for all to have minimal redundance)
        % in the figure)
        if j==1
            ylabel(all_out_measures_names(i_mes),"FontSize",12);
        end
        if i_mes < n_out_mes
            set(gca,'xtick',[])
            set(gca,'xticklabel',[])
            if i_mes == 1
                legend("Stimulation slow","Stimulation fast");
                title(cond_names(j));
            end
        else
            xlabel("Trial number");
        end
    end
end
sgtitle("Average Participants: Difference to mean training");
% Save the plot
set(gcf, 'Position', get(0, 'Screensize'));
saveas(gcf,strcat(pwd ,"\Plots\mean_par_trial_vice.jpg"));

