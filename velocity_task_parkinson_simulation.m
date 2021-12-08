%% Simulate the task 
% Check the task changes on the already recorded datasets

% Get a list of all datasets 
filenames = dir(fullfile('..\..\Data\Parkinson\',"*.mat"));
n_files = length(filenames);
for i_file=1:n_files
    
    % Load the data
    load(strcat('..\..\Data\Parkinson\',filenames(i_file).name));
    data = struct.data; 

    %% Loop over every movement
    figure;
    n_trials = 32;
    n_blocks = 14;
    diff_peaks = [];
    movement_thres = 2000;
    for i_block=1:n_blocks
        for i_trial=1:n_trials  
            % Get the data for one trial 
            mask = data(:,8) == i_block & data(:,9) == i_trial & data(:,4) > movement_thres;
            data_trial = data(mask, :);
            % Get the true peak of the movement
            [peak,true_ind_peak] = max(data_trial(:,4));
            % Get the "peak" following the method
            data_acc = diff(data_trial(:,4));
            for i=n_moves_peak:length(data_acc)
                if all(data_acc(i-(n_moves_peak-1):i) < 0)
                    sim_ind_peak = i+1;
                    try
                       diff_peaks = cat(1,diff_peaks,data_trial(sim_ind_peak,3)-data_trial(true_ind_peak,3));
                     end
                    break
                end
            end
    %         figure;
    %         plot(data_trial(:,4));
    %         hold on;
    %         xline(sim_ind_peak, "red");
    %         hold on;
    %         xline(true_ind_peak, "green");
        end
    end

    % Analyse the results
    subplot(1,6,n_moves_peak);
    histogram(diff_peaks,30);
    title(sprintf("%i Mean %.3f Var %0.3f", n_moves_peak, mean(diff_peaks), var(diff_peaks)));
    %xlim([-0.5,0.5]);
    hold on;
% figure;
% plot(rmoutliers(data(:,4))); 
% hold on; 
% for i=1:length(sim_peaks_ind(1:20))
%     xline(sim_peaks_ind(i), "red");
%     hold on;
%     xline(true_peaks_ind(i), "green");
%     hold on;
% end
end
sgtitle(i_file);
end
