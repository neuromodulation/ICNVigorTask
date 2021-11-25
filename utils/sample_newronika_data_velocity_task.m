%% Sample LFP data continously for the velocity task
% In the velocity task the sampling rate is too low 
% Sample the data here with high smapling rate, save the time and
% synchronize it later 
% Weird thing: always two samples are returned

clear all;

% CHANGE AT BEGINNING OF EXPERIMENT!!
n_par = 8; % Participant number

% Initialize electrophysiology recording

labels = {'LFPR13', 'LFPL13'}; % Define channel names
nwkInterface = newronikaInterface(labels); % Initialize newronika interface
% Get samples until the escape key is pressed
while true
    nwkInterface.sample;
end

%% Close and Save
nwkInterface.closeConnection;
% Extract lfp data
dataLfp = nwkInterface.data;
% Save lfp data
save(strcat(pwd,'/Data/Parkinson/',sprintf("Participant_%i_LFP.mat",n_par)), "dataLfp");