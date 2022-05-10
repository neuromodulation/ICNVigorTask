%% Save only the data in a mat file for processing in python 
% --> Final data storage in brain vision file 

filenames = dir(fullfile('..\..\Data\Parkinson_Pilot\',"*.mat"));
n_files = length(filenames);
for i_file=1:n_files
    % Load the data from one recording
    load(strcat('..\..\Data\Parkinson_Pilot\',filenames(i_file).name));
    data = struct.data; 
    save(strcat('..\..\Data\Parkinson_Pilot\data_',filenames(i_file).name));
end