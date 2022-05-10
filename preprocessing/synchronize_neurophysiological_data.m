%% Synchronize behavioural and neurophysiological data

clear all;
%% Synchronize TMSi data
% Load the behavioural data
[filename_behav,path_behav] = uigetfile('..\..\Data\Parkinson_Pilot\');
load(strcat(path_behav,filename_behav));
behav_data = struct.data;
%% Load the TMSi data
[filename,path] = uigetfile('..\..\Data\Parkinson_Pilot\');
[~,filename,extension] = fileparts(filename);
neuro_struct = TMSi.Poly5.read([path,'\',filename,extension]);
neuro_data = neuro_struct.samples;
sfreq = neuro_struct.sample_rate;

%% 
figure;
for i= 1:9
    subplot(3,3,i);
    title(i);
    plot(neuro_data(i,:));
end
%%
figure;
for i= 10:19
    subplot(3,3,i-9);
    title(i);
    plot(neuro_data(i,:));
end
%%
figure;
for i= 20:29
    subplot(3,3,i-19);
    title(i);
    plot(neuro_data(i,:));
end

%% Downsample to 250 Hz 
new_sfreq = 250;
down_samp =  sfreq/new_sfreq;
neuro_data = downsample(neuro_data.',down_samp);

%% Create a time array for the neuro data
times = linspace(0,neuro_struct.time,length(neuro_data)).';
neuro_data = cat(2, neuro_data, times);

%% Get the time of the first stim
% Which channel to use for finding stimulation artifact??
stim_onset_time_neuro = neuro_data(find(zscore(neuro_data(:,5)) > 1,1),end);
stim_onset_time_behav = behav_data(find(behav_data(:,11) == 1,1),3);
% Compute the difference 
diff_time = stim_onset_time_neuro - stim_onset_time_behav;
% Substract the difference from the neuro time
neuro_data(:,end) = neuro_data(:,end) - diff_time;

%% Check alignment 
% Delete zero rows from behavioural data
behav_data = upsample(behav_data, 4);
rows_all_zeros = find(all(behav_data == 0,2));
behav_data(rows_all_zeros,:) = [];

%% Plot stim onset and mean neuro data
plot(behav_data(:,3),zscore(behav_data(:,11)));
hold on;
plot(neuro_data(:,end),zscore(detrend(mean(neuro_data(:,5),2))));
% Looks good :)) 

%% Delete the neuro_data before 0 
[min_val,start_idx] = min(abs(neuro_data(:,end)));
neuro_data = neuro_data(start_idx:end,:);

%% Find the behavioural sample that is the nearest in time
i_samps = size(neuro_data,1);
behav_data_aligned = zeros(i_samps,size(behav_data,2));
for i = 1:i_samps
    time = neuro_data(i,end);
    [val,idx] = min(abs(behav_data(:,3) - time));
    behav_data_aligned(i,:) = behav_data(idx,:);
end

%% Attach to neuro data
neuro_behav_data = cat(2, neuro_data,behav_data_aligned);

 %% Save the data
struct.neuro_data = neuro_behav_data;
save(strcat(pwd,'/Data/Parkinson/',filename_behav), "struct");