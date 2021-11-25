
%% Velocity task simulate simulation

% Stimulate based on the last two movements 
% Fast: If faster than the last two movements 
% Slow: If slower than the last two movements 
% Time at which is checked based on the second block (mean of times from
% movement onset) 

n_par = 1;
n_blocks = 14;
n_trials = 32;
slow = zeros(n_par, n_blocks-2,n_trials-2);
fast = zeros(n_par, n_blocks-2,n_trials-2);
peak_velocities = zeros(n_par, n_blocks-2,n_trials-2);
peak_velocities_time = zeros(n_par, n_blocks-2,n_trials-2);
for i_par=1:n_par
    
    % Load the data
    load(strcat(pwd,'/Data/Parkinson/',sprintf("Participant_%i.mat",i_par)));
    %load(strcat(pwd,'/Data',sprintf("/%i/Participant_%i.mat",i_par,i_par)));
    
    % Initialize the peak array 
    peaks = [];
    for i_block=2:n_blocks
        
        % Compute the mean time of the peak based on the second block
        peak_times = zeros(n_trials,1);
        peak_vels = zeros(n_trials,1);
        if i_block == 2
             for i_trial=1:n_trials
                % Get the data for one block and trial (when the movement
                % has started --> data(:,4) > 200)
                [peak, peak_time] = get_peak_velocity_and_time(data,i_block,i_trial);
                peak_times(i_trial) = peak_time;
                peak_vels(i_trial) = peak;
             end
             % Compute the threshold for the peak time and the threshold
             % for the velocity outliers
             threshold_time = prctile(peak_times, 80);
             threshold_outlier_max = std(peak_vels,[],'all')*5 + median(peak_vels,'all');
             threshold_outlier_min = median(peak_vels,'all') - std(peak_vels,[],'all')*5 ;
        else
            
             for i_trial=1:n_trials
                 % Get the peak velocity up until the time threshold
                 peak = get_peak_velocity(data, i_block, i_trial, threshold_time); 
                 % Save it together with the actual peak velocity of the trial
                 if i_trial > 2
                     peak_velocities_time(i_par, i_block-2, i_trial-2) = peak;
                     peak_velocities(i_par, i_block-2, i_trial-2) = get_peak_velocity(data, i_block, i_trial, 100);
                 end
                 
                 % Append the peak to the array
                 peaks = cat(1, peaks, peak);
                 
                 % If the peak as well as the last 2 peaks are no outliers
                 % check if the movement is slow or fast
                 if i_trial > 2 && all(peaks(end-2:end) < threshold_outlier_max) && all(peaks(end-2:end) > threshold_outlier_min)
                    peak_diff = peaks(end) - peaks(end-2:end-1);
                     if all(peak_diff > 0)
                         fast(i_par, i_block-2,i_trial-2)= 1;
                     elseif all(peak_diff < 0)
                          slow(i_par, i_block-2,i_trial-2)= 1;
                     end
                 end 
             end
        end
    end
end

%% Visualize the results - Percentage of stimulated movements
slow_percentage = slow * 100; fast_percentage = fast * 100;
mean_slow = mean(slow_percentage, [1, 3]);
mean_fast = mean(fast_percentage, [1, 3]);
std_slow = std(mean(slow_percentage, 3), [], 1);
std_fast = std(mean(fast_percentage, 3), [], 1);

% Plot the mean percentage of stimulated slow/fast trials for each block over participants 
plot(mean_slow, 'b', 'LineWidth',4);
hold on;
plot(mean_fast, 'r', 'LineWidth',4);
legend("Stimulation slow","Stimulation fast");
xlabel("Block"); ylabel("% of stimulated trials");

% Add the standard deviation over participants
x = 1:12;
curve1 = mean_slow + std_slow;
curve2 = mean_slow - std_slow;
x2 = [x, fliplr(x)];
inBetween = [curve1, fliplr(curve2)];
fill(x2, inBetween, 'b', 'facealpha', .3);
hold on;
curve1 = mean_fast + std_fast;
curve2 = mean_fast - std_fast; 
x2 = [x, fliplr(x)];
inBetween = [curve1, fliplr(curve2)];
fill(x2, inBetween, 'r', 'facealpha', .3);
legend("Slow","Fast");    

%% Visualize the results - Velocity of stimulated movements
% Transform the velocity values into z scores for summarizing all
% participants
peak_velocities_z_score = zscore(peak_velocities, [], [2, 3]);
% Get the mean of all, slow and fast movements for each participants and
% block (has to be done in a for loop as the number can be different for
% each block and participant)
mean_slow_par = zeros(n_par, n_blocks - 2);
mean_fast_par = zeros(n_par, n_blocks -2);
for i_par=1:n_par
    for i_block=1:n_blocks-2
        mean_slow_par(i_par, i_block) = mean(peak_velocities_z_score(i_par,i_block,logical(slow(i_par,i_block,:))));
        mean_fast_par(i_par, i_block) = mean(peak_velocities_z_score(i_par,i_block,logical(fast(i_par,i_block,:))));
    end
end
mean_slow = mean(mean_slow_par, 1) ;
mean_fast = mean(mean_fast_par, 1);
mean_all = mean(peak_velocities_z_score, [1, 3]);

% Plot the mean percentage of stimulated slow/fast trials for each block over participants 
figure;
plot(mean_slow, 'b', 'LineWidth',4);
hold on;
plot(mean_fast, 'r', 'LineWidth',4);
hold on;
plot(mean_all, 'g', 'LineWidth',4);
legend("Slow","Fast", "Mean");
xlabel("Block"); ylabel("z-scored mean velocity");