%% Load and synchronize EEG data
% Save it in the full form and syncronized to the behavioural matlab data

n_par = 8; 

% Load the data manually and copy the name of the openbci dataset here
openbci = OpenBCIRAW20210201150719; 
eeg = table2array(openbci(:,[2 3 9])); % Get the three channels and the time stamps
eeg_time = table2array(openbci(:,end)); % Get the time stamps

% Get the matrix of time points for each sample in the eeg data
eeg_time_matrix = zeros(length(eeg_time),3);
for line=1:length(eeg_time)
    char_time = char(eeg_time(line));
    char_hour = char_time(12:end);
    char_hour_split = split(char_hour,':');
    for i=1:3
        eeg_time_matrix(line,i)= str2num(cell2mat(char_hour_split(i,1)));
    end
end

% Load matlab data 
load(strcat(pwd,'/Data/',sprintf("%i/Participant_%i.mat",n_par,n_par)));

% Delete the rows with all 0 
rows_all_zeros = find(all(data == 0,2));
data(rows_all_zeros,:) = [];

% Generate a matrix with the sample time points 
times_matlab = data(:,end-2:end);

% Get the indexes of the eeg data that are closest to the samples in the
% matlab data
eeg_indexes = zeros(length(times_matlab),1);
for line=1:length(times_matlab)
    mask_hour = times_matlab(line,1) == eeg_time_matrix(:,1);
    mask_min = times_matlab(line,2) == eeg_time_matrix(:,2);
    eeg_time_hour_min = eeg_time_matrix(mask_hour & mask_min,:);
    [~,i] = min(abs(times_matlab(line,3) - eeg_time_hour_min(:,3)));
    sec = eeg_time_hour_min(i,3);
    mask = mask_hour & mask_min & eeg_time_matrix(:,3)== sec;
    if sum(mask) > 1
        indexes = find(mask);
        index = indexes(1); % Just choose the first one if there are eeg samples with equal time stamp
    else
        index = find(mask);
    end
    eeg_indexes(line) = index;
end
% Check the times 
diff_time = mean(times_matlab - eeg_time_matrix(eeg_indexes,:));
disp(diff_time);

%% Save the full eeg data during the experiment
eeg = eeg(eeg_indexes(1):eeg_indexes(end),:);
save(strcat(pwd,'/Data/',sprintf("%i/Participant_%i_eeg.mat",n_par,n_par)), "eeg");

% Save the indexes of the eeg data in order to synchronize it to the matlab
% data
eeg_indexes = eeg_indexes - eeg_indexes(1)+1;
save(strcat(pwd,'/Data/',sprintf("%i/Participant_%i_eeg_indexes.mat",n_par,n_par)), "eeg_indexes");

% Save matlab data (with deleted 0 rows)
save(strcat(pwd,'/Data/',sprintf("%i/Participant_%i.mat",n_par,n_par)), "data");

