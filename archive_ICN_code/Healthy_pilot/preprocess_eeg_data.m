%% Preprocess the EEG data and save it with the behavioural data 
% Plot the power spectra

%% Preparation

n_par = 8; 
chan_names = ["C3","Fz","Cz","sma","lmc"];
fs = 250;

%% Compute the alpha/beta amplitude of the channels and append it to the matlab data
for i_par = 8:n_par
    
    % Load the eeg data from a participant
    load(strcat(pwd,'/Data/',sprintf("%i/Participant_%i.mat",i_par,i_par)));
    load(strcat(pwd,'/Data/',sprintf("%i/Participant_%i_eeg.mat",i_par,i_par)));
    load(strcat(pwd,'/Data/',sprintf("%i/Participant_%i_eeg_indexes.mat",i_par,i_par)));
    
    % Append bipolar channels
    eeg = cat(2,eeg, eeg(:,3)-eeg(:,2), eeg(:,3)-eeg(:,1));
    eeg = filloutliers(eeg,"linear",1);
    n_chan = size(eeg,2);
    amps = zeros(n_chan,2,length(eeg));
    
    %Filter the data
    lowEnd = 7; highEnd = 30; % Hz
    filterOrder = 6;
    [b, a] = butter(filterOrder, [lowEnd highEnd]/(fs/2)); % Generate filter coefficients
    eeg_filt = filtfilt(b, a, eeg); 
    
     for i_chan=1:n_chan
          
       % Compute the mean beta and alpha amplitude of the channel
       [w,f] = cwt(eeg_filt(:,i_chan),fs);
       mask_beta = f <= 30 & f >= 15;
       mask_alpha = f <= 14 & f >= 7;
       amp_beta = mean(abs(w(mask_beta,:)),1);
       amp_alpha = mean(abs(w(mask_alpha,:)),1);

       % Save it to a matrix which stores all amplitudes
       amps(i_chan,1,:) = amp_beta;
       amps(i_chan,2,:) = amp_alpha;
     end
    
    % Save the amplitudes synchronized with the matlab data 
    data = cat(2,data,squeeze(amps(:,1,eeg_indexes)).',squeeze(amps(:,2,eeg_indexes)).');
    save(strcat(pwd,'/Data/',sprintf("%i/Participant_%i_with_eeg.mat",i_par,i_par)), "data");

end
close all;

%% Plot the power spectra for a sanity check of the data

for i_par = 1:n_par
    
    % Load the eeg data from a participant
    load(strcat(pwd,'/Data/',sprintf("%i/Participant_%i_eeg.mat",i_par,i_par)));
    
    % Append bipolar channels
    eeg = cat(2,eeg, eeg(:,3)-eeg(:,2), eeg(:,3)-eeg(:,1));
    %eeg = filloutliers(eeg,"linear",1);
    n_chan = size(eeg,2);
    lowEnd = 7; highEnd = 30; % Hz
    filterOrder = 6;
    [b, a] = butter(filterOrder, [lowEnd highEnd]/(fs/2)); % Generate filter coefficients
    eeg = filtfilt(b, a, eeg); 
    
    figure;
     for i_chan=1:n_chan
       
       % Plot the power spectrum
        [w,f] = cwt(eeg(:,i_chan),fs);
        amp = mean(abs(w),2);
        subplot(2,3,i_chan);
        mask = f > 1 & f  < 40;
        plot(f(mask),amp(mask));
        title(chan_names(i_chan));
        xlabel("Frequency");
        ylabel('Amplitude');
     end
    
    sgtitle(sprintf("Participant %i",i_par));
    set(gcf, 'Position', get(0, 'Screensize'));
    % Save the plot 
    saveas(gcf,strcat(pwd ,'\Plots\EEG\', sprintf("cwt_abs_%i.jpg",i_par)));

end