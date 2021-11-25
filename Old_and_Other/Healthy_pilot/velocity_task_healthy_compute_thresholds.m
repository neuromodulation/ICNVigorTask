%% Movement velocity task - Compute thresholds

% Version: Healthy subjects with visual stimulaton and EEG recording

% Summary: Compute and visualize the thresholds (as described in the
% calibration script)

%% Load the data 
n_par = 8; 
load(strcat(pwd,'/Data/',sprintf("Calibration_Participant_%i.mat",n_par)));
data = data_calibration;
n_train_blocks = max(data(:,8));
n_trials = max(data(:,9));

% Compute the peak velocity distributions of each training block
peak_vels = zeros(n_train_blocks,n_trials-1);
peak_times = zeros(n_train_blocks,n_trials-1);
for i_b=1:n_train_blocks
    for i_t=1:n_trials
        % Get the data for one block and trial (when the movement
        % has started --> data(:,4) > 100)
        mask = data(:,8) == i_b & data(:,9) == i_t & data(:,4) > 100; 
        data_trial = data(mask, :);
        % Get the peak velocity and its time point in that trial
        % (in respect to the start of the movement)
        [peak, index]  = max(data_trial(:,4));
        peak_vels(i_b, i_t) = peak;
        peak_times(i_b,i_t) = data_trial(index,3)-data_trial(1,3);
    end
end

% Plot the velocity distributions with the thresholds given that blocks -->
% Visual sanity check 
subplots = reshape(1: n_train_blocks*2, 2, n_train_blocks);
xlims_vel = [min(peak_vels,[],"all"), max(peak_vels,[],"all")];
xlims_time = [min(peak_times,[],"all"), max(peak_times,[],"all")];
figure;
for i_block = 1:n_train_blocks
    block_peak_vels = peak_vels(i_block,:);
    block_peak_times = peak_times(i_block,:);
    
    % Compute the threshold for that block
    threshold_slow =  prctile(block_peak_vels,(100/3),'all');
    threshold_fast =  prctile(block_peak_vels,(100/3)*2,'all');
    mean_vel = mean(block_peak_vels);
    % Compute the time window used for threshold crossing detection for
    % fast and slow movements
    peak_times_slow = peak_times(block_peak_vels < threshold_slow);
    peak_times_fast = peak_times(block_peak_vels > threshold_fast);
    threshold_time_slow = prctile(peak_times_slow,85,'all');
    threshold_time_fast = prctile(peak_times_fast,85,'all');
    mean_time = mean(block_peak_times);
    
    % Plot the distributions and the thresholds for the peak velocities
    subplot(n_train_blocks, 2, subplots(1,i_block));
    histogram(block_peak_vels, n_trials, "FaceColor","b");
    xline(threshold_fast, "r", "LineWidth", 2); xline(threshold_slow, "b", "LineWidth", 2);
    xline(mean_vel,"black", "LineWidth", 2);
    xlim(xlims_vel);
    title(sprintf("Training Block %i",i_block));
    xlabel("Peak velocity[Pixel/second]");
    % Plot the distributions and the thresholds for the peak velocity times
    subplot(n_train_blocks, 2, subplots(2,i_block));
    histogram(block_peak_times, n_trials ,"FaceColor","b");
    xline(threshold_time_fast,"r", "LineWidth", 2); xline(threshold_time_slow, "b","LineWidth", 2);
    xline(mean_time,"black", "LineWidth", 2);
    xlim(xlims_time);
    xlabel("Time[Seconds]");
    title(sprintf("Training Block %i",i_block));
end

set(gcf, 'Position', get(0, 'Screensize'));

% Check if the last two distributions are significantly different from each
% other 
% YES: Compute another calibration run 
% NO: Use the last two blocks to compute the final thresholds
p_vel = kruskalwallis(peak_vels(end-1:end,:).');
fprintf("The peak velocity of the last 2 blocks come from different distributions with p-value %.2f \n", p_vel);
p_time = kruskalwallis(peak_times(end-1:end,:).');
fprintf("The peak time velocity from the last 2 blocks come from different distributions with p-value %.2f \n", p_time);

%% Compute the final threshold from the last two blocks

if p_vel > 0.05 && p_time > 0.05 || true
    thres_peak_vels = peak_vels(end-1:end,:);
    thres_peak_times= peak_times(end-1:end,:);
    threshold_slow =  prctile(thres_peak_vels,(100/3),'all');
    threshold_fast =  prctile(thres_peak_vels,(100/3)*2,'all');
    peak_times_slow = peak_times(thres_peak_vels < threshold_slow);
    peak_times_fast = peak_times(thres_peak_vels > threshold_fast);
    threshold_time_slow = prctile(peak_times_slow,85,'all');
    threshold_time_fast = prctile(peak_times_fast,85,'all');

    % Save the data 
    thresholds = [threshold_slow threshold_fast threshold_time_slow threshold_time_fast];
    save(strcat(pwd,'/Data/',sprintf("Thresholds_Participant_%i.mat",n_par)), "thresholds");
end
