%% Velocity task healthy analysis - EEG
% Analyse the EEG data from the pilot of the velocity task (healthy
% participants) 

% Given are the mean alpha and beta amplitudes of the channels Cz, C3, Fz
% as well as the bipolar Cz-C3 (left motor cortex-lmc) and bipolar Cz-Fz
% (supplementary motor area-sma) --> 10 columns that are appended to the
% end of the data

% Compute the following outcome measures:
% 1. Mean correlation between velocity/acceleration and each eeg(amplitude) channel
% 2. Difference between slow/fast peak and no movement 
% (in form of z-scores --> then combined across participants)
% 3. Plot the amplitues locked to the onset/peak/offset of the movements

%% Preparation

% Five conditions
n_cond = 5;
n_blocks_cond = 2;
n_trials = 32;
blocks = reshape(1:10,2,5);
n_par = 8;
channel_names = ["Left motor cortex Beta", "Supplementary motor cortex Beta", "Cz Beta", "Fz Beta", "C3 Beta",...
                            "Left motor cortex Alpha", "Supplementary motor cortex Alpha", "Cz Alpha", "Fz Alpha", "C3 Alpha"];
chan_names = ["LMC Beta", "SMA Beta", "Cz Beta", "Fz Beta", "C3 Beta",...
    "LMC Alpha", "SMA Alpha", "Cz Alpha", "Fz Alpha", "C3 Alpha"];
n_chan = length(channel_names);

%% 1. Mean correlation
close all;
corr_vel = zeros(n_par-1,10);
corr_acc = zeros(n_par-1,10);
n = zeros(n_par-1,1); 
for i_par=2:n_par
    
    % Load the data from one participant
    load(strcat(pwd,'/Data/',sprintf("%i/Participant_%i_with_eeg.mat",i_par,i_par)));
    
    % Compute the acceleration 
    acc = [0; diff(data(:,4))];
    
    % Compute the correlation between velocity/acceleration and amplitude
  
    %fprintf("Participant %i \n", i_par);
    for chan =0:9
        [r,p] = corrcoef(data(:,[4 end-chan]));
        corr_vel(i_par-1,chan+1) = r(1,2);
        %fprintf(strcat('The correlation of velocity and ', channel_names(chan+1),' is %.3f with p-value %.3f \n'),r(1,2),p(1,2));
        [r,p] = corrcoef(data(:,end-chan),acc);
        corr_acc(i_par-1,chan+1) = r(1,2);
        %fprintf(strcat('The correlation of acceleration and ', channel_names(chan+1),' is %.3f with p-value %.3f \n'),r(1,2),p(1,2));
    end
    % Save the number of samples for the combination of the correlation
    % coeffieicents across participants
    n(i_par-1) = length(data);
end

% Compute the average correlation for each channel and
% velocity/acceleration using hunter-schmidth method
mean_corr_vel = sum(n .* corr_vel, 1) / sum(n);
mean_corr_acc = sum(n .* corr_acc, 1) / sum(n);
mean_corr = cat(1,mean_corr_vel,mean_corr_acc);

% Calculate the z-score to determine significance
z_vel = mean_corr_vel ./ ((sqrt(sum(n .* (corr_vel - mean_corr_vel), 1).^2 / sum(n)))...
                                                            / sqrt(n_par-1));
z_acc = mean_corr_acc ./ ((sqrt(sum(n .* (corr_acc - mean_corr_acc), 1).^2 / sum(n)))...
    / sqrt(n_par-1));

% Plot it 
figure;
bar(mean_corr.')
legend("Velocity","Acceleration");
set(gca,'xticklabel',chan_names,'FontSize', 18);
ylabel("Correlation");
title("Average population correlation");
set(gcf, 'Position', get(0, 'Screensize'));
saveas(gcf,strcat(pwd ,'\Plots\EEG\', sprintf("mean_corr_%i.jpg",i_par)));

%% Plot the histograms of the correlation values 
close all;
measures = ["Velocity","Acceleration"];
corr_all = cat(3,corr_vel,corr_acc);
for i=1:2
    figure;
    for i_chan=1:n_chan
        subplot(n_chan/2,2,i_chan);
        histogram(corr_all(:,i_chan,i),5);
        xlabel("Correlation");
        title(chan_names(i_chan));
    end
    sgtitle(measures(i));
end

%% 2. Difference between no movement, around a slow and a fast peak 
close all;
before_after_peak = 5; % Get 10 Samples around the peak 
z_scores_all= zeros(n_par-1,2,n_chan);

for i_par=2:n_par
     
    % Load the data from one participant
    load(strcat(pwd,'/Data/',sprintf("%i/Participant_%i_with_eeg.mat",i_par,i_par)));
    load(strcat(pwd,'/Data/',sprintf("%i/Participant_%i_info.mat",i_par,i_par)));
    threshold_slow = more_info(2);
    threshold_fast = more_info(3);

    % Get the velocity/acceleration from no movement 
    mask_no_move = data(:,4) < 100;
    no_move_data = data(mask_no_move,end-n_chan+1:end);
    slow_data = [];
    fast_data = [];
    for i_cond=1:n_cond
        for i_block=1:n_blocks_cond  
            for  i_trial=1:n_trials
                
                % Get the trial data
                mask = data(:,8) == blocks(i_block,i_cond) & data(:,9) == i_trial;
                data_trial = data(mask,:);
                
                % Get whether this trial was fast or slow
                [peak_move,peak_index] = max(data_trial(:,4)); 
                slow = peak_move < threshold_slow; 
                fast = peak_move > threshold_fast;
                
                if slow
                    slow_data = cat(1,slow_data,data_trial(peak_index - before_after_peak:before_after_peak + peak_index,end-n_chan+1:end));
                elseif fast
                    fast_data = cat(1,fast_data,data_trial(peak_index - before_after_peak:before_after_peak + peak_index,end-n_chan+1:end));
                end
            end
        end
    end
    
    % Compute the z-scores 
    stat_train = [mean(no_move_data,1); std(no_move_data,0,1)];
    slow_z_scores = mean((slow_data- stat_train(1,:)) ./ stat_train(2,:),1);
    fast_z_scores = mean((fast_data- stat_train(1,:)) ./ stat_train(2,:),1);
    z_scores = cat(1,slow_z_scores,fast_z_scores);
    z_scores_all(i_par-1,:,:) = z_scores;

    % Plot the z-scores for each participant 
    figure;
    bar(z_scores.');
    legend("Slow","Fast");
    set(gca,'xticklabel',chan_names,'FontSize', 18);
    ylabel("Z-score");
    title(sprintf("Difference of amplitude around peak to no movement: Participant %i",i_par));
    set(gcf, 'Position', get(0, 'Screensize'));
    saveas(gcf,strcat(pwd ,'\Plots\EEG\', sprintf("z_score_eeg_%i.jpg",i_par)));

end

% Compute and plot the mean z-scores 
mean_z_scores = squeeze(mean(z_scores_all,1));
figure;
bar(mean_z_scores.');
legend("Slow","Fast");
set(gca,'xticklabel',chan_names,'FontSize', 18);
ylabel("Z-score");
title("Difference of amplitude around peak to no movement: Mean Participants");
set(gcf, 'Position', get(0, 'Screensize'));
saveas(gcf,strcat(pwd ,'\Plots\EEG\mean_z_score_eeg.jp'));


%% 3. Amplitudes locked to movement onset/offset/peak (each participant)

close all; 
% Set the number of samples to plot around the events
before_onset =10; after_onset = 10;
before_peak = 10; after_peak = 10;
before_offset = 10; after_offset = 10;
all_mean_erd = [];

for i_par = 2:n_par
    
    % Initialize the arrays
    onset = [];offset =[];peak = [];
    slow_all = []; fast_all = [];
    discarded_trial = 0;
    
    % Load the data from one participant
    load(strcat(pwd,'/Data/',sprintf("%i/Participant_%i_with_eeg.mat",i_par,i_par)));
    load(strcat(pwd,'/Data/',sprintf("%i/Participant_%i_info.mat",i_par,i_par)));
    threshold_slow = more_info(2);
    threshold_fast = more_info(3);

    for i_cond=1:n_cond
        for i_block=1:n_blocks_cond  
            for  i_trial=1:n_trials
                
                % Get the trial data
                mask = data(:,8) == blocks(i_block,i_cond) & data(:,9) == i_trial;
                data_trial = data(mask,:);
                
                % Get whether this trial was fast or slow
                [peak_move,peak_index] = max(data_trial(:,4)); 
                slow = peak_move < threshold_slow; 
                fast = peak_move > threshold_fast;
                
                % Only get the beta amplitudes if either slow or fast
                if slow || fast

                    % Use only the trials that have enough samples before
                    % movement onset
                    onset_indexes = find(data_trial(:,4) >= 100,4);
                    onset_index = onset_indexes(1);
                    if onset_index - before_onset > 0
                        
                        % Save the amplitude relative to the movement onset
                        onset = cat(3,onset,data_trial(onset_index - before_onset:onset_index + after_onset, end-n_chans+1:end));
                    
                        % Save the amplitude relative to the peak
                        peak = cat(3,peak, data_trial(peak_index - before_peak:peak_index + after_peak, end-n_chans+1:end));
                    
                        % Save the amplitude relative to the movement offset
                        offset_indexes = find(data_trial(:,10) == 1,10);
                        offset_index = offset_indexes(1);
                        offset = cat(3,offset,data_trial(offset_index - before_offset:offset_index + after_offset, end-n_chans+1:end));

                        % Save whether the trial is slow or fast 
                        slow_all = cat(1,slow_all,slow);
                        fast_all = cat(1,fast_all,fast);               
                    else
                        discarded_trial = discarded_trial +1; % Increase counter if not enough samples before movement onset
                    end   
                end
            end
        end
    end
    
    % Reformat some variables
    slow_all = logical(slow_all);
    fast_all = logical(fast_all);
    all_amps = cat(4,onset,peak,offset);
    
    % Compute the (de)synchronization in relation to the time before
    % the movement onset
    baseline = mean(all_amps(1:before_onset,:,:,1),1);
    all_erd = ((all_amps - baseline) ./ baseline) * 100;
    
    % Compute the mean and std over the slow/fast trials
    slow_mean = squeeze(mean(all_erd(:,:,slow_all,:),3));
    fast_mean = squeeze(mean(all_erd(:,:,fast_all,:),3));
    
    % Save the mean trial erd for each channel and participant
    erd = cat(4,slow_mean,fast_mean);
    all_mean_erd = cat(5,all_mean_erd, erd);
    
    % Plot the erd for each channel and participant
    for i_chan=1:n_chans
     
         figure; 
         ylims =[ min(erd(:,i_chan,:,:),[],"all"), max(erd(:,i_chan,:,:),[],"all")];

        % Plot the movement onset
        subplot(1,3,1);
        x = [0-before_onset:after_onset]*(1/60);
        plot(x,erd(:,i_chan,1,1),"LineWidth",2);
        %errorbar(x,slow_mean_onset,slow_std_onset);
        hold on; 
        plot(x,erd(:,i_chan,1,2),"LineWidth",2);
        %errorbar(x,fast_mean_onset,fast_std_onset);
        legend('Slow','Fast')
        title("Movement onset");
        ylim(ylims);
        xline(0);
        ylabel("ERD/ERD [%]");
        xlabel("Time [ms]");

        % Plot the movement peak 
        subplot(1,3,2);
        x = [0-before_peak:after_peak]*(1/60);
        plot(x,erd(:,i_chan,2,1),"LineWidth",2);
        %errorbar(x,slow_mean_peak,slow_std_peak);
        hold on; 
        plot(x,erd(:,i_chan,2,2),"LineWidth",2);
        %errorbar(x,fast_mean_peak,fast_std_peak);
        legend('Slow','Fast')
        title("Movement peak");
        ylim(ylims);
        xline(0);
        h = gca; h.YAxis.Visible = 'off';
        xlabel("Time [ms]");

        % Plot the movement offset
        subplot(1,3,3);
        x = [0-before_offset:after_offset]*(1/60);
        plot(x,erd(:,i_chan,3,1),"LineWidth",2);
        %errorbar(x,slow_mean_offset,slow_std_offset);
        hold on; 
        plot(x,erd(:,i_chan,3,2),"LineWidth",2);
        %errorbar(x,fast_mean_offset,fast_std_offset);
        legend('Slow','Fast')
        title("Movement offset");
        ylim(ylims);
        xline(0);
        h = gca; h.YAxis.Visible = 'off';
        xlabel("Time [ms]");

        set(gcf, 'Position', get(0, 'Screensize'));
        sgtitle(strcat("Participant: ", string(i_par), " Channel: ", channel_names(i_chan)));
        saveas(gcf,strcat(pwd ,"\Plots\EEG\locked_amps_chan_",chan_names(i_chan),"_par_",string(i_par),".jpg"));
        close all;
     end
end

%% Compute the mean erd over participants 
erd = mean(all_mean_erd,5);
close all;
% Plot the mean erd for each channel
 for i_chan=1:n_chans
     
     figure; 
     ylims =[ min(erd(:,i_chan,:,:),[],"all"), max(erd(:,i_chan,:,:),[],"all")];
        
    % Plot the movement onset
    subplot(1,3,1);
    x = [0-before_onset:after_onset]*(1/60);
    plot(x,erd(:,i_chan,1,1),"LineWidth",2);
    %errorbar(x,slow_mean_onset,slow_std_onset);
    hold on; 
    plot(x,erd(:,i_chan,1,2),"LineWidth",2);
    %errorbar(x,fast_mean_onset,fast_std_onset);
    legend('Slow','Fast')
    title("Movement onset");
    ylim(ylims);
    xline(0);
    ylabel("ERD/ERD [%]");
    xlabel("Time [ms]");

    % Plot the movement peak 
    subplot(1,3,2);
    x = [0-before_peak:after_peak]*(1/60);
    plot(x,erd(:,i_chan,2,1),"LineWidth",2);
    %errorbar(x,slow_mean_peak,slow_std_peak);
    hold on; 
    plot(x,erd(:,i_chan,2,2),"LineWidth",2);
    %errorbar(x,fast_mean_peak,fast_std_peak);
    legend('Slow','Fast')
    title("Movement peak");
    ylim(ylims);
    xline(0);
   % h = gca; h.YAxis.Visible = 'off';
    xlabel("Time [ms]");

    % Plot the movement offset
    subplot(1,3,3);
    x = [0-before_offset:after_offset]*(1/60);
    plot(x,erd(:,i_chan,3,1),"LineWidth",2);
    %errorbar(x,slow_mean_offset,slow_std_offset);
    hold on; 
    plot(x,erd(:,i_chan,3,2),"LineWidth",2);
    %errorbar(x,fast_mean_offset,fast_std_offset);
    legend('Slow','Fast')
    title("Movement offset");
    ylim(ylims);
    xline(0);
    %h = gca; h.YAxis.Visible = 'off';
    xlabel("Time [ms]");

    set(gcf, 'Position', get(0, 'Screensize'));
    sgtitle(strcat("Channel: ", channel_names(i_chan)));
    saveas(gcf,strcat(pwd ,"\Plots\EEG\locked_amps_chan_",chan_names(i_chan),"_mean.jpg"));

 end

%% Extra: Effect of visual stimulation 

for i_par = 2:n_par
    % Load the data from one participant
    load(strcat(pwd,'/Data/',sprintf("%i/Participant_%i_with_eeg.mat",i_par,i_par)));
    
    data_stim = data(data(:,11) == 1, end-n_chan+1:end);
    data_no_stim = data(data(:,11) == 0, end-n_chan+1:end);
    % Get the same number of values
    data_no_stim = data_no_stim(randi(length(data_no_stim),length(data_stim),1),:);
    
    for i_chan=1:n_chan
        p = kruskalwallis([data_stim(:,i_chan),data_no_stim(:,i_chan)])
    end
end