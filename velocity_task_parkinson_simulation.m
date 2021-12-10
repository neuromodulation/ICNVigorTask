%% Simulate the task 
% Check the task changes on the already recorded datasets

% Get a list of all datasets 
close all;
filenames = dir(fullfile('..\..\Data\Parkinson\',"*.mat"));
n_files = length(filenames);
thres_x_move_start = 300;
for i_file=1:n_files
    
    % Load the data
    load(strcat('..\..\Data\Parkinson\',filenames(i_file).name));
    data = struct.data; 

    %% Loop over every movement
    n_trials = 33;
    n_blocks = 14;
    diff_after_target = [];
    diff_peak_after = [];
    diff_peak_after_peak = [];
    peaks = [];
    slow_peaks = [];
    fast_peaks = [];
    for i_block=1:n_blocks
        for i_trial=1:n_trials  
            mask = data(:,8) == i_block & data(:,9) == i_trial;
            data_trial = data(mask, :);
            
            % Average the velocity over less samples 
            data_vel_av = zeros(length(data_trial),1);
            for i=4:length(data_trial)
                data_vel_av(i) = mean(data_trial(i-3:i,5));
            end
            
%             figure; 
%             plot(data_trial(:,[1 4 5]), "LineWidth", 2); 
%             hold on; 
%             plot(data_vel_av,"LineWidth", 2);
%             hold on;
%             [y,x] = max(data_vel_av);
%             plot(x,y,".",'MarkerSize',25);
%             hold on;
%             [y,x] = max(data_trial(:,4));
%             plot(x,y,".",'MarkerSize',25);
%             hold on;
%             [y,x] = max(data_trial(:,5));
%             plot(x,y,".",'MarkerSize',25);
%             legend(["x mouse","mean vel", "vel", "new mean vel"]);
            
            % Find the index of the target
            ind_target = find(data_trial(:,10)==1,1);
            
            % Find the true peak 
            [peak,ind_peak] = max(data_vel_av(1:ind_target));
            
            % Find the moment after the peak
            ind_after_peak = 0;
            for i=3:length(data_trial)
                if all(diff(data_vel_av(i-2:i)) < 0) && abs(data_trial(i,1)-data_trial(1,1)) > thres_x_move_start
                    ind_after_peak = i;
                    break;
                end
            end
            % Get the peak before the index after the peak
            [peak_after,~] = max(data_vel_av(1:ind_after_peak));
            if peak < 20000
                peaks = cat(1,peaks,peak);
            end
            
            % Save the distances in seconds 
            try
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
%     figure;
%     plot(abs(diff(peaks))); hold on;
%     yline(prctile(abs(diff(peaks)),99));
    % Analyse the results
    figure;
    subplot(4,1,1);
    diff_after_target = rmoutliers(diff_after_target,'percentiles',[5 95]);
    histogram(diff_after_target,30);
    title("Time Target - Stimulation time");
    subplot(4,1,2);
    diff_peak_after = rmoutliers(diff_peak_after,'percentiles',[5 95]);
    histogram(diff_peak_after,30);
    title("Stimulation time - Time of peak");
    subplot(4,1,3);
    diff_peak_after_peak = rmoutliers(diff_peak_after_peak,'percentiles',[5 95]);
    histogram(diff_peak_after_peak,30);
    title("Chosen peak - True peak");
    subplot(4,1,4);
    peaks = rmoutliers(peaks,'percentiles',[5 95]);
    slow_peaks = rmoutliers(slow_peaks,'percentiles',[5 95]);
    fast_peaks = rmoutliers(fast_peaks,'percentiles',[5 95]);
    g = [ones(length(slow_peaks),1)*1; ones(length(peaks),1)*2; ones(length(fast_peaks),1)*3];
    x = [slow_peaks; peaks; fast_peaks];
    n_slow = length(slow_peaks)/length(peaks);
    n_fast = length(fast_peaks)/length(peaks);
    boxplot(x,g,'Labels',["slow","all","fast"])
    title(sprintf("peak velocity slow %.2f fast %.2f",n_slow, n_fast));
end
