function [time] = get_target_time(data,block,trial,movement_thres)
    %% Return the time when stimulation is turned on (recorded in the data)
    
    % Get the data from one trial 
    mask = data(:,8) == block & data(:,9) == trial & data(:,4) > movement_thres;
    data_trial = data(mask, :);
    
    % Check if the movement is stimulated
    target = find(data_trial(:,11));
    if target
        % Get the time in relation to movement onset
        times_from_movement_onset = data_trial(:,3) - data_trial(1,3);
        time = times_from_movement_onset(target(1));
    else
        time = [];
    end
end

