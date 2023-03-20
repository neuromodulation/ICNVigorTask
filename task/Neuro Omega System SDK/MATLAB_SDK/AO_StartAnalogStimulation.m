function [Result] = AO_StartAnalogStimulation(ContactID, WaveID, Freq_Hz, Duration_Sec, ReturnChannel)

% brief  Request to start stimulation on specific analog input contact.
% param  ContactID          [IN] The contact to apply on the analog stimulation wave.
% param  WaveID             [IN] The analog stimulation wave ID.
% param  Freq_Hz            [IN] The analog stimulation wave frequency in Hz.
% param  Duration_Sec       [IN] The analog stimulation wave duration in Seconds.
% param  ReturnChannel      [IN] The stimulation common return channel.
% return eAO_OK                Success. i.e. Request sent successfuly.
% return eAO_BAD_ARG           if Freq_Hz != -1 (Repeat without delay) and Freq_Hz < 1.
% return eAO_BAD_ARG           if Duration_Sec < 0.005 or Duration_Sec > 30000.
% return eAO_BAD_ARG           if Stim. Contact and Return channel contact are the same.
% return eAO_NO_STIMULATION    if the given contact stim type is eStimType_NoStim.
% return eAO_CONTACT_NOT_EXIST if no contact found with the given ID ContactID.
% return eAO_CONTACT_NOT_EXIST if no contact found with the given ID ReturnChannel, in case ReturnChannel not Global Return.
% return eAO_NOT_CONNECTED     if the system is not connected.

% Please advice the SDK Manual for extra information.

AO_Functions;
Result = MexFileSystemSDK(AO_StartAnalogStimulation_IDX, ContactID, WaveID, Freq_Hz, Duration_Sec, ReturnChannel);
if (Result ~= 0)
	AO_DisplayError();
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Example for using this function
%
% ContactID     = 10005;
% WaveID        =     0; % not used for now
% Freq_Hz       =    10; % the frequncy of the stimulation
% Duration_Sec  =    30; % duration of the stimulation
% ReturnChannel =    -1;
%
% [Result] = AO_StartAnalogStimulation(ContactID, WaveID, Freq_Hz, Duration_Sec, ReturnChannel)
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%