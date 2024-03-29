function [peak, peak_time] = get_peak_velocity_and_time(data,block,trial,movement_thres,time)
    %% Return the peak velocity of a specific movement and the time of the peak
    % before "time" etc. Important if we want to know teh peak before a
    % specific time point (stimulation time), if you don't want to use
    % time, choose a really high value (e.g. 100)
    % Use "movement_thres" to use only the data after movement onset
    
    % Get the data from one trial 
    mask = data(:,8) == block & data(:,9) == trial & data(:,4) > movement_thres;
    data_trial = data(mask, :);
    
    % Get the data up to the time point
    times_from_movement_onset = data_trial(:,3) - data_trial(1,3);
    data_trial_until_time = data_trial(times_from_movement_onset <= time, :);
    
    % Get the peak and the time point of the peak
    [peak, index] = max(data_trial_until_time(:, 4));
    peak_time = data_trial(index,3) - data_trial(1,3);
end

