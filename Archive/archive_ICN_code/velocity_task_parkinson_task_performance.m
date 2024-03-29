%% Measure the task performance 
% -> Inclusion criteria for the participants
% 1. Correct amount of movements are stimulated (between 25-40 %)
% 2. Correct movements are stimulated (sensitivity + specificity)
% 3. Time of stimulation is close to true peak 

%% Load data from one participant
% Load the data
[filename,path] = uigetfile('..\..\Data\Parkinson\');
load(strcat(path,filename));
data = struct.data; 
options = struct.options; 
n_trials = 32;

% First condition = Slow, Second condition = Fast
if ~any(fieldnames(options) == "cond")
        options.cond = options.slow_first;
end
if options.cond
    stim_blocks = [3:5; 9:11];
else
    stim_blocks = [9:11; 3:5];
end

%% Loop through the blocks with stimulation 
% Intialize arrays to store the time difference between peak and
% stimulation and number of stimulated movements per condition
diffs_stim_peak = [];
perf = []; 
for i_cond=1:size(stim_blocks, 1)
    stims = [];
    true_stims = [];
    peaks = [];
    for i_block=1:size(stim_blocks,2)
        for i_trial=1:n_trials
            % Get the data from one trial
            mask = data(:,8) == stim_blocks(i_cond,i_block) & data(:,9) == i_trial;
            data_trial = data(mask,:); 
            % Get the peak and peak index
            [peak, ind_peak] = max(data_trial(:,4));
            peaks = cat(1,peaks, peak);
            % Check whether the movement should have been stimulated 
            if length(peaks)> 2 && (all(peaks(end-2:end-1) > peaks(end)) && i_cond == 1 ||...
                all(peaks(end-2:end-1)< peaks(end)) && i_cond == 2)
                true_stim = 1;
            else
                true_stim = 0;
            end
            % Check whether movement was stimulated
            inds_stim = find(data_trial(:,11) == 1);
            if inds_stim
                stim = 1;
                % Get the index of the stimulation 
                ind_stim = inds_stim(1); 
                % Save the time difference between peak and stimulation 
                diff_stim_peak = data_trial(ind_stim,3) - data_trial(ind_peak,3);
                diffs_stim_peak = cat(1, diffs_stim_peak, diff_stim_peak);
            else
                stim = 0;
            end
            % Save whether the movement was stimulated and should have been
            % stimulated
            stims = cat(1,stims, stim);
            true_stims = cat(1,true_stims, true_stim);
        end
    end
    % Calculate the number of stimulated movements as well as sensitivity
    % and specificity
    perc_stim = sum(stims)/length(stims);
    sens = sum(stims == 1 & true_stims == 1)/sum(true_stims == 1);
    spec = sum(stims == 0 & true_stims == 0)/sum(true_stims == 0);
    perf = cat(1,perf,[perc_stim, sens,spec]*100);
end

%% Plot the results 
figure; 
% Plot the time between true peak and stimulation
subplot(2,1,1);
histogram(diffs_stim_peak);
% Plot the performance values
subplot(2,1,2);
b = bar(perf);
ylabel("%");
set(b, {'DisplayName'}, {'Total %','Sensitivity','Specificity'}')
legend();
set(gca, 'XTick', 1:2, 'XTickLabels', {'Slow','Fast'})
% Add the values 
width = b.BarWidth;
for i=1:length(perf(:, 1))
    row = perf(i, :);
    % 0.5 is approximate net width of white spacings per group
    offset = ((width + 0.5) / length(row)) / 2;
    x = linspace(i-offset, i+offset, length(row));
    text(x,row,num2str(row'),'vert','bottom','horiz','center');
end

