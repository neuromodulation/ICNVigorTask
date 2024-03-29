%% Simulate the task 
% Check for earlier stimulation times

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
    peaks_and_earlier = [];
    diff_times = [];
    stims = [];
    for i_block=1:n_blocks
        for i_trial=2:n_trials  
            mask = data(:,8) == i_block & data(:,9) == i_trial;
            data_trial = data(mask, :);
            
            % Average the velocity over less samples 
            data_vel_av = zeros(length(data_trial),1);
            for i=4:length(data_trial)
                data_vel_av(i) = mean(data_trial(i-3:i,5));
            end
            
            % Find the true peak 
            [peak,ind_peak] = max(data_trial(:,4));
            
            % Find the velocity at a specific distance from the target
            init_x_y = data_trial(1,[1 2]);
            % Calculate the distance from the initial position 
            dis = sqrt(sum((data_trial(:,[1 2]) - init_x_y).^2, 2));
            % Find the index when a distance is passed
            ind_dis = find(dis > 1500,1);
            % Get the velocity at that point 
            vel_before = data_trial(ind_dis,4);
            % Get time distance between true peak and before 
            diff_time = data_trial(ind_peak,3) - data_trial(ind_dis,3);
            diff_times = cat(1,diff_times, diff_time);
            
            % Save together
            peaks_and_earlier = cat(1,peaks_and_earlier,[peak, vel_before]);
            
            % Save whether the movement would be stimulated 
            if length(peaks_and_earlier) > 2
                if all(peaks_and_earlier(end,1) - peaks_and_earlier(end-2:end-1,1) < 0) 
                    stim_true_slow = true;
                else
                    stim_true_slow = false;
                end
                if all(peaks_and_earlier(end,1) - peaks_and_earlier(end-2:end-1,1) > 0)
                    stim_true_fast = true;
                else
                    stim_true_fast = false;
                end
                if all(peaks_and_earlier(end,2) - peaks_and_earlier(end-2:end-1,2) < 0) 
                    stim_before_slow = true;
                else
                    stim_before_slow = false;
                end
                if all(peaks_and_earlier(end,2) - peaks_and_earlier(end-2:end-1,2) > 0)
                    stim_before_fast = true;
                else
                    stim_before_fast = false;
                end
 
            else
                stim_true_slow = false;
                stim_before_slow = false;
                stim_true_fast = false;
                stim_before_fast = false;
            end
            % Save the stimulation decision
            stims = cat(1,stims,[stim_true_slow, stim_true_fast, stim_before_slow, stim_before_fast]);
        end
    end
    % Plot them together
    figure;
    subplot(2,1,1);
    peaks_and_earlier = rmoutliers(peaks_and_earlier);
    plot(peaks_and_earlier(:,1),peaks_and_earlier(:,2),"o");
    subplot(2,1,2);
    diff_times = rmoutliers(diff_times);
    histogram(diff_times); hold on;
    % Calculate the specificity and sensitivity
    sens_slow = sum(stims(:,1) == stims(:,3) & stims(:,1) == 1)/sum(stims(:,1) == 1);
    spec_slow = sum(stims(:,1) == stims(:,3) & stims(:,1) == 0)/sum(stims(:,1) == 0);
    sens_fast = sum(stims(:,2) == stims(:,4) & stims(:,2) == 1)/sum(stims(:,2) == 1);
    spec_fast = sum(stims(:,2) == stims(:,4) & stims(:,2) == 0)/sum(stims(:,2) == 0);
    title(sprintf("Sens Slow %.2f Spec Slow %.2f Sens Fast %.2f Spec Fast %.2f",sens_slow,spec_slow,sens_fast,spec_fast));
end
