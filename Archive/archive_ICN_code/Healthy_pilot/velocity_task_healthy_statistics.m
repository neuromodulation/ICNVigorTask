
%% Velocity task healthy statistics
% Visualize the statistics of the behavioural data from the pilot of the velocity task (healthy
% participants) 

% Measures: (same as for the analysis, but not effect is analyzed)
% 1. Peak velocity
% 2. Acceleration
% 3. Trial length (From beginning of movement)
% 4. Tortuosity (directness of path)
% 5. Movement initialization

% The mean values are computed over each block and participants and plotted
% with blocks on the x-axis and shaded areas for variance across
% participants 

% Here we forget about the stimulation and just look at the time course of
% the experiment

% Extra: Visualize mean movement tragectories 

%% Preparation

% Five conditions
n_cond = 5;
n_trials = 32;
blocks = 1:10;
n_blocks = max(blocks,[],'all');
n_par = 8;
all_out_measures_names = {'Peak velocity','Peak acceleration', 'Movement duration', 'Tortuosity', 'Movement initiation'};
all_out_measures_label_names = {'pixel/sec','pixel/sec','sec','path/optimal path','sec'};
n_out_mes = size(all_out_measures_names, 2);

%% Compute and visualize the outcome measures

% Initalize an array to store all the measures for all participants and
% blocks
measures = zeros(n_par,n_out_mes,n_blocks,n_trials);

for i_par=1:n_par
    
    % Load the data from one participant
    load(strcat(pwd,'/Data/',sprintf("%i/Participant_%i.mat",i_par,i_par)));
    load(strcat(pwd,'/Data/',sprintf("%i/Participant_%i_info.mat",i_par,i_par)));
    slow_first = more_info(1);
    
    for i_block=1:n_blocks
        for  i_trial=1:n_trials

            % Get the data from one trial
            mask = data(:,8) == i_block & data(:,9) == i_trial;
            data_trial = data(mask,:);

            % Get the peak velocity
            measures(i_par,1,i_block,i_trial) = max(data_trial(:,4));

            % Get the peak acceleration
            acc = diff(data_trial(:,4));
            measures(i_par,2,i_block,i_trial) = max(acc);

            % Get the movement length (duration)
            data_time_move_start = data_trial(data_trial(:,4)>100,3);
            data_time_move_end = data_trial(data_trial(:,10) == 1,3);
            measures(i_par,3,i_block,i_trial) = data_time_move_end(1)-data_time_move_start(1);

            % Get the tortuosity (directness of path: path length
            % divided by shortest path length)
            path = sum(vecnorm(diff(data_trial(:,1:2)).'));
            min_path = vecnorm(diff(data_trial([1 end],1:2)));
            measures(i_par,4,i_block,i_trial) = path/min_path;

            % Get the time needed for movement initialization
            measures(i_par,5,i_block,i_trial) =  data_time_move_start(1) - data_trial(1,3);
        end
    end
end

% Compute the mean over trials and the mean/std over participants
measures = squeeze(mean(measures,4));
mean_measures = squeeze(mean(measures,1));
std_measures = squeeze(std(measures,0,1));
% Could try the actual value sinstead of std std_measures = max(measures - mean_measures)

% Plot the mean values and stds over blocks
figure;
for i_mes=1:n_out_mes
    tmp_mean = squeeze(mean_measures(i_mes,:));
    tmp_std = squeeze(std_measures(i_mes,:));
    
    subplot(round(n_out_mes/2),2,i_mes);
    
    % Shade the area of the standard deviation
    x = [blocks, fliplr(blocks)];
    y = [tmp_mean-tmp_std ,fliplr(tmp_mean+tmp_std)];
    fill1 = fill(x, y, 'r');
    set(fill1,'facealpha',.3);
    hold on
    % Add labels and the data and the mean
     if i_mes < n_out_mes-1
        set(gca,'xtick',[])
        set(gca,'xticklabel',[])
        yline(mean(tmp_mean),"-",string(round(mean(tmp_mean),2)),"Color","black","LineWidth",2,"FontSize",14);
        plot(tmp_mean,'r','LineWidth',4);
     else
        xlabel("Block Number","FontSize",14);
        plot(tmp_mean,'r','LineWidth',4);
        yline(mean(tmp_mean),"-",string(round(mean(tmp_mean),2)),"Color","black","LineWidth",2,"FontSize",14);
        legend({'Std'});
     end
    ylabel(all_out_measures_label_names(:,i_mes),"FontSize",14);
    title(all_out_measures_names(i_mes))
    xlim([1 10]);
     
end
%sgtitle("Behavioural measures over blocks: Averaged over participants");
% Save the plot
set(gcf, 'Position', get(0, 'Screensize'));
saveas(gcf,strcat(pwd ,"\Plots\mean_par_stats.jpg"));

%% Visualize the mean trajectories
load('unique_moves.mat');
n_moves = length(unique_moves);
n_par=2;
trajectories = zeros(n_par,n_moves, n_blocks, 2,100);
for i_par=1:n_par
    
    % Load the data from one participant
    load(strcat(pwd,'/Data/',sprintf("Participant_%i.mat",i_par)));
    
    for i_block=1:n_blocks
        for i_trial=1:n_trials
            % Get the movement number of a trial
            mask_trial = data(:,8) == i_block & data(:,9) == i_trial;
            mask_trial_prev = data(:,8) == i_block & data(:,9) == i_trial-1;
            pos = [unique(data(mask_trial_prev,12)) unique(data(mask_trial_prev,13)) ...
                                       unique(data(mask_trial,12)) unique(data(mask_trial,13))];
            [~, i_move] = ismember(pos,unique_moves,'rows');
            % Remove data points with duplicate x positions
            x = data(mask_trial,1); y= data(mask_trial,2);
            tmp_x = []; tmp_y = [];
            for i=1:length(x)
                if ~ismember(x(i),tmp_x)
                    tmp_x = cat(1,tmp_x,x(i));
                    tmp_y = cat(1,tmp_y,y(i));
                end
            end
            
            % Interpolate the data such that each trial has the same number of
            % samples (choose high number of sampling points)
            x_interpol = linspace(pos(1),pos(3),100);
            y_interpol = interp1(tmp_x,tmp_y,x_interpol);
            trajectories(i_par,i_move, i_block,:,:) = [x_interpol; y_interpol];
        end
    end
end

% Compute the means over participants and blocks 
trajectories_mean = squeeze(mean(trajectories,[1,3]));
moves_split = reshape(1:n_moves,n_moves/2,2);
directions=["Right","Left"];
% Plot the mean trajectories
for i_plot=1:2
    figure;
     [ha, pos] = tight_subplot(4,4,[.01 .03],[.1 .01],[.01 .01]);
     for i_move=1:n_moves/2
%         h = subplot(n_moves/8,n_moves/8,i_move);
%         p = get(h, 'pos');
%         disp(p);
%         p(1) = p(1) + 0.05;
%         set(h, 'pos', p);
        axes(ha(i_move)); 
        %ha(i_move);
        
        tmp_traj = squeeze(trajectories_mean(moves_split(i_move,i_plot),:,:));
        tmp_traj(isnan(tmp_traj))=0;

        scatter(tmp_traj(1,:),tmp_traj(2,:),4);
        xlabel("X-pixel"); ylabel("Y-pixel");
        ylim([0,1080]);% Set the ylimist to a common value for all plots
        xlim([0,1920]);
        hold on;
%         set(gca,'xtick',[])
%         set(gca,'xticklabel',[])
%         set(gca,'ytick',[])
%         set(gca,'yticklabel',[])
       
        % Add an arrow to indicate the direction of movement 
        p= 6;
        quiver(tmp_traj(1,p),tmp_traj(2,p),tmp_traj(1,end-p)-tmp_traj(1,p),tmp_traj(2,end-p)-tmp_traj(2,p),0,'linewidth',2,'color','r');
    end
    %sgtitle("Mean trajectories (over blocks and participants) for movements to the " + directions(i_plot));
    % Save the plot
    set(gcf, 'Position', get(0, 'Screensize'));
    saveas(gcf,strcat(pwd ,"\Plots\mean_par_traj_",directions(i_plot),".jpg"));
    %set(ha(1:16),'XTickLabel',''); set(ha,'YTickLabel','');
end

