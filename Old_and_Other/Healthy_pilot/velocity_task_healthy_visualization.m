
%% Velocity task visualization

% Visualize the the behavioural data:
% 1. The trialwise velocity curves with thresholds, the stimulation period
% and the period on the target

%% Preparation
% Load data 
n_par = 4;
load(strcat(pwd,'/Data/',sprintf("Participant_%i.mat",n_par)));
load(strcat(pwd,'/Data/',sprintf("Participant_%i_info.mat",n_par)));
slow_first = more_info(1);
threshold_slow = more_info(2);
threshold_fast = more_info(3);
time_threshold_slow = more_info(4);
time_threshold_fast = more_info(5);

%% Five conditions
n_cond = 5;
n_blocks_cond = 2;
n_trials = 32;
if slow_first
    cond_titles = ["Training", "Stimulation slow", "Recovery slow", "Stimulation fast", "Recovery fast"];
else
    cond_titles = ["Training", "Stimulation fast", "Recovery fast", "Stimulation slow", "Recovery slow"];
end
blocks = reshape(1:10,2,5);
blocks_plot = reshape(1:4,2,2);
n_blocks = max(blocks,[],'all');
train_blocks = 1:2;

ylim_all = zeros(n_blocks, 2);
count = 0;
for i_cond=1:n_cond
    figure(i_cond);
    for i_block=1:n_blocks_cond
        
        count = count+1;
        
        % Get all the velocity values and times from one block
        mask_1 = data(:,8) == blocks(i_block,i_cond) & data(:,9) <= 16;
        mask_2 = data(:,8) == blocks(i_block,i_cond) & data(:,9) > 16;
        masks = [mask_1 mask_2];
        
        % Split the data from one block into two plots
        for j=1:2
            mask = masks(:,j);
            data_mask  = data(mask,:);
            data_time = data_mask(:, 3);

            % Plot the velocity over time
            subplot(4,1,blocks_plot(j,i_block));
            plot(data_time, data_mask(:,4), 'k');

            % Get the y limits and set the x limits
            ylim_plot = ylim;
            ylim_all(count,:) = ylim_plot;
            xlim([min(data_time) max(data_time)]);

            % Add lines seperating trials 
            indexes = 1:length(data_time);
            trial_switches = data_time(indexes(diff(data_mask(:, 9)) ~= 0) + 1);
            for j=1:length(trial_switches)
                xline(trial_switches(j),'LineWidth',1.5);
            end

            % For stimulation blocks shade area during which stimulation was on
            if ismember(i_cond,[2 4])
                stim_start_times = data_time(indexes(diff(data_mask(:, 11)) == 1) + 1);
                stim_end_times = data_time(indexes(diff(data_mask(:, 11)) == -1) + 1);
                if length(stim_start_times)>length(stim_end_times)
                    stim_end_times = cat(1, stim_end_times,data_time(end));
                end
                for j=1:length(stim_start_times)
                    x1 = stim_start_times(j);
                    x2 = stim_end_times(j);
                    y = 10000;
                    v = [x1 0; x2 0; x2 y; x1 y];
                    f = [1 2 3 4];
                    hold on;
                    patch('Faces',f,'Vertices',v,'FaceColor','red','FaceAlpha',.3, 'EdgeColor', 'none');
                end
            end

            % Add the stimulation thresholds
            yline(threshold_slow, '--r');
            yline(threshold_fast, '--r');

            % Shade the areas during which the participant was on the target
            on_target_start_times = data_time(indexes(diff(data_mask(:, 10)) == 1) + 1);
            on_target_end_times = [data_time(indexes(diff(data_mask(:, 10)) == -1) + 1); data_time(end)];
            for j=1:length(on_target_start_times)
                x1 = on_target_start_times(j);
                x2 = on_target_end_times(j);
                y = 10000;
                v = [x1 0; x2 0; x2 y; x1 y];
                f = [1 2 3 4];
                hold on;
                patch('Faces',f,'Vertices',v,'FaceColor','green','FaceAlpha',.3, 'EdgeColor', 'none');
            end
        end
    end
end

% Set the axis of the plots to the same y limits and save the plots 
ylim_new = [min(ylim_all(:,1)) max(ylim_all(:,2))];
for i_cond=1:n_cond
    figure(i_cond);
    for i_block=1:4
        subplot(4,1,i_block);
        ylim(ylim_new);
        xlabel("sec");
        ylabel("pixel/sec");
    end
    sgtitle(cond_titles(i_cond));
    set(gcf, 'Position', get(0, 'Screensize'));
    saveas(gcf,strcat(pwd ,'\Plots\',  sprintf("Par_%i_Cond_%i_vel.jpg",n_par,i_cond)));
end

%% Visualization of the stimulation criteria for the lab report

figure;
blocks_trials = [[1 11];[1 32];[4,29];[2,27]];
thresholds = [threshold_slow, threshold_slow, threshold_fast, threshold_fast];
time_thresholds = [time_threshold_slow, time_threshold_slow, time_threshold_fast, time_threshold_fast];
titles = ["Stimulation", "No stimulation", "Stimulation", "No stimulation"];
conditions = ["slow","slow","fast","fast"];
for i =1:4
    block = blocks_trials(i,1);
    trial = blocks_trials(i,2);
    mask = data(:,8) == block & data(:,9) == trial;
    vel = data(mask,4);
    times = data(mask,3); 
    times_move = times(vel > 100);
    times = times - times_move(1);

    subplot(1,4,i);
    plot(times,vel,"black", "LineWidth", 2);
    label_time_threshold = "";%strcat(" Time threshold ",conditions(i),": ", string(round(time_thresholds(i),2)));
    x1 = xline(time_thresholds(i),"-",label_time_threshold,"Color","r",'LineWidth',2);
    %x1.LabelVerticalAlignment = 'bottom';
    %x1.LabelHorizontalAlignment = 'left';

    x1.FontSize = 11;
    label_vel_threshold = "";%{"Velocity threshold ",strcat(conditions(i),": ", string(round(thresholds(i),2)))};
    y1 = yline(thresholds(i),"-",label_vel_threshold,"Color","r",'LineWidth',2);
    y1.FontSize = 11;
    ylim([min(vel) 5000]);
    %title(titles(i));
    
    if i == 1
        ylabel("Velocity [Pixel/Second]",'FontSize',14);
        xlabel("Time [Seconds]",'FontSize',14);

    else
        yticks([]);
    end
    
    if mod(i,2)
        x1 = time_thresholds(i);
        x2 = x1 + 0.3;
        y = 10000;
        v = [x1 0; x2 0; x2 y; x1 y];
        f = [1 2 3 4];
        hold on;
        patch('Faces',f,'Vertices',v,'FaceColor','red','FaceAlpha',.3, 'EdgeColor', 'none');
    end
    
    disp(thresholds(i));
end
  set(gcf, 'Position', get(0, 'Screensize'));

%%
xline(time_thresholds(i),':','test','Color','red');

