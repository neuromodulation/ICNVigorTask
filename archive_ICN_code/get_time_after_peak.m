function diff_time = get_time_after_peak(data,block,trial,movement_thres)
    %% Return the time shortly after the peak based on the negative acceleration
    
    % Get the data from one trial 
    mask = data(:,8) == block & data(:,9) == trial & data(:,4) > movement_thres;
    data_trial = data(mask, :);
    
    % Compute the acceleration
    data_acc = diff(data_trial(:,4));
    for i=5:length(data_acc)
        if all(data_acc(i-2:i) < 0)
            idx_after_peak = i;
            break
        end
    end
    [~, idx_peak] = max(data_trial(:, 4));
    diff_time = data_trial(idx_after_peak,3)-data_trial(idx_peak,3);
end

