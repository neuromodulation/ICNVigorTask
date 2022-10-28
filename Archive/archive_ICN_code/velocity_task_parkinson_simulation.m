%% Simulate the task 
% Check the task changes on the already recorded datasets

% Get a list of all datasets 
close all;
%filenames = dir(fullfile('..\..\..\Data\Parkinson_Pilot\',"*.mat"));
filenames = dir(fullfile('..\..\..\Data\',"*.mat"));
n_files = length(filenames);
thres_x_move_start = 200;
plot_one_trial = false;
for i_file=1:n_files
    
    % Load the data
    %load(strcat('..\..\..\Data\Parkinson_Pilot\',filenames(i_file).name));
    load(strcat('..\..\..\Data\',filenames(i_file).name));
    data = struct.data; 

    %% Loop over every movement
    n_trials = 96;
    n_blocks = 4;
    diff_peak_after = [];
    time_peak_stim = [];
    peaks = [];
    distance = [];
    for i_block=1:n_blocks
        for i_trial=1:n_trials  
            mask = data(:,8) == i_block & data(:,9) == i_trial;
            data_trial = data(mask, :);
            
            % Average the velocity over less samples 
            data_vel_av = zeros(length(data_trial),1);
            for i=6:length(data_trial)
                data_vel_av(i) = mean(data_trial(i-5:i,5));
            end
            
            % Find the index of the target
            ind_target = find(data_trial(:,10)==1,1);
            
            % Find the true peak 
            [peak,ind_peak] = max(data_vel_av(1:ind_target));
            
            % Find distance from peak in pixel 
            d = sqrt((data_trial(ind_peak,1) - data_trial(ind_peak,12))^2 + (data_trial(ind_peak,2) - data_trial(ind_peak,13))^2);
            distance = cat(1,distance,abs(data_trial(ind_peak,1) - data_trial(ind_peak,12)));
            
            % Find peak time 
            ind_stim = find(data_trial(:,11)==1,1);
            if ind_stim
                time_peak_stim = cat(1, time_peak_stim, data_trial(ind_stim-1, 3) - data_trial(ind_peak, 3));   
            end
            
            % Find the moment after the peak
            ind_after_peak = 0;
            for i=5:length(data_trial)
                if all(diff(data_vel_av(i-3:i)) < 0) && abs(data_trial(i,1)-data_trial(1,1)) > thres_x_move_start
                    ind_after_peak = i;
                    break;
                end
            end
            
            if ind_stim & plot_one_trial
                figure; 
                plot(data_trial(:,[1 4 5]), "LineWidth", 2); 
                hold on; 
                plot(data_vel_av,"LineWidth", 2);
                hold on;
                [y,x] = max(data_vel_av);
                plot(x,y,".",'MarkerSize',25);
                hold on;
                [y,x] = max(data_trial(:,4));
                plot(x,y,".",'MarkerSize',25);
                hold on;
                [y,x] = max(data_trial(:,5));
                plot(x,y,".",'MarkerSize',25);
                legend(["x mouse","mean vel", "vel", "new mean vel"]);
                hold on; 
                plot(ind_after_peak,data_vel_av(ind_after_peak),"*",'MarkerSize',25);
                hold on;
                thres_pos = find(abs(data_trial-data_trial(1,1)) > thres_x_move_start,1);
                xline(thres_pos);
                xline(ind_stim-1);
                x = 0;
            end
            
            % Get the peak before the index after the peak
            [peak_after,~] = max(data_vel_av(1:ind_after_peak));
            if peak < 20000
                peaks = cat(1,peaks,peak);
            end
            
            % Save the distances in seconds 
            if ind_stim
                diff_after_target = cat(1, diff_after_target,data_trial(ind_target,3) - data_trial(ind_after_peak,3));
                diff_peak_after = cat(1, diff_peak_after,data_trial(ind_after_peak,3) - data_trial(ind_peak,3));
                diff_peak_after_peak = cat(1, diff_peak_after_peak,abs(peak-peak_after));
            end
            % Decide whether the movement would be slow or fast
            if length(peaks) > 2
                if all(peaks(end) - peaks(end-2:end-1) < 0)
                    slow_peaks = cat(1,slow_peaks,peak);
                elseif all(peaks(end) - peaks(end-2:end-1) > 0)
                    fast_peaks = cat(1,fast_peaks,peak);
                end
            end
        end
    end
    % Analyse the results
    figure;
    subplot(1,2,1);
    perf_old = sum(time_peak_stim > 0) / length(time_peak_stim);
    perf_new = sum(diff_peak_after > 0) / length(diff_peak_after);
    histogram(time_peak_stim,30); hold on;
    histogram(diff_peak_after,30);
    legend(["Old","New"]);
    title(sprintf("Old: %.2f New: %.2f ",perf_old * 100, perf_new * 100));
    subplot(1,2,2);
    histogram(distance,30); 
end
