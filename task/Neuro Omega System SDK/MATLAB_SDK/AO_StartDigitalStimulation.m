function [Result] = AO_StartDigitalStimulation(ContactID, FirstPhaseDelay_mS, FirstPhaseAmp_mA, FirstPhaseWidth_mS, SecondPhaseDelay_mS, SecondPhaseAmp_mA, SecondPhaseWidth_mS, Freq_Hz, Duration_Sec, ReturnChannel)

% brief  Request to start stimulation on specific analog input contact.
% param  ContactID           [IN] The contact to apply the square wave stimulation parameters.
% param  FirstPhaseDelay_mS  [IN] Square wave first phase delay in Milliseconds.
% param  FirstPhaseAmp_mA    [IN] Square wave first phase amplitude in Milliamps.
% param  FirstPhaseWidth_mS  [IN] Square wave first phase width in Milliseconds.
% param  SecondPhaseDelay_mS [IN] Square wave second phase delay in Milliseconds.
% param  SecondPhaseAmp_mA   [IN] Square wave second phase amplitude in Milliamps.
% param  SecondPhaseWidth_mS [IN] Square wave second phase width in Milliseconds.
% param  Freq_Hz             [IN] Square wave frequency in Hz.
% param  Duration_Sec        [IN] Square wave duration in Seconds.
% param  ReturnChannel       [IN] The stimulation common return channel.

% If succeed to set the given square wave stimulation parameters for the given contact,
% the system will start stimulate the given square wave on the requested stim contact.

% See SetStimulationParameters for return values.
% Please advice the SDK Manual for extra information.

AO_Functions;
Result = MexFileSystemSDK(AO_StartDigitalStimulation_IDX, ContactID, FirstPhaseDelay_mS, FirstPhaseAmp_mA, FirstPhaseWidth_mS, SecondPhaseDelay_mS, SecondPhaseAmp_mA, SecondPhaseWidth_mS, Freq_Hz, Duration_Sec, ReturnChannel);
if (Result ~= 0)
	AO_DisplayError();
end

%% Be aware when stimulation is done with more than one channel,that the set stimulation params refer to the stimulation source

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Example for using this function
%
% ContactID           = 10000; % the contact we want to start stimulation in 
% FirstPhaseDelay_mS  =   0.5; % the delay of the first phase
% FirstPhaseAmp_mA    =  -3.5; % the amplitude of the first phase
% FirstPhaseWidth_mS  =   0.5; % the width of the first phase
% SecondPhaseDelay_mS =   1.0; % the delay of the second phase
% SecondPhaseAmp_mA   =   3.5; % the amplitude of the second phase
% SecondPhaseWidth_mS =   0.2; % the width of the second phase
% Freq_Hz             =    10; % the frequncy of the stimulation
% Duration_Sec        =    30; % the duration of the stimulation
% ReturnChannel       = 10001; % the ID of the channel we want to return the stimulation with
%
% Result = AO_StartDigitalStimulation(ContactID, FirstPhaseDelay_mS, FirstPhaseAmp_mA, FirstPhaseWidth_mS, SecondPhaseDelay_mS, SecondPhaseAmp_mA, SecondPhaseWidth_mS, Freq_Hz, Duration_Sec, ReturnChannel);
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%