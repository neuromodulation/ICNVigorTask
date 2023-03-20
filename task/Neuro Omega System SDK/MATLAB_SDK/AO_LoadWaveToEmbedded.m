function [Result] = AO_LoadWaveToEmbedded(Samples, SamplesCount, DownSampleFactor, WaveName)

% brief  Set new analog stimulation wave.
% param  Samples          [IN] Analog stimulation wave samples array. Sample in Micro Amp unit.
% param  SamplesCount     [IN] Samples array size. No more than 8 Million.
% param  DownSampleFactor [IN] Define wave samples sampling rate: (System Sampling Rate)/(Down Sample Factor).
% param  WaveName         [IN] Analog stimulation wave name, i.e. 'Stim Wave 1'. No more than 10 characters including the end of string character.
% return eAO_OK            Success. i.e. Request sent successfuly.
% return eAO_BAD_ARG       if nSamples <= 0 or nSamples > 8000000.
% return eAO_BAD_ARG       if Down Sample Factor not one of: [1,2,4,8,16].
% return eAO_BAD_ARG       if Wave name length bigger than 10 characters, including the end of string character.
% return eAO_BAD_ARG       if Wave name empty.
% return eAO_BAD_ARG       if Wave name illegal. Should have only digits and letters.
% return eAO_NOT_CONNECTED if the system is not connected.

% Please advice the SDK Manual for extra information.

intArray = '';
if (isempty(find(isnan(Samples)==1)) && isreal(Samples) && isnumeric(Samples))
    intArray = int16(Samples); %convert the array to short values
end

AO_Functions;
[Result] = MexFileSystemSDK(AO_LoadWaveToEmbedded_IDX, intArray, SamplesCount, DownSampleFactor, WaveName);
if (Result ~= 0)
	AO_DisplayError();
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Example of using this function:
% x=[0:1:180]
% Samples          = sin(x);
% SamplesCount     = 1500;
% DownSampleFactor = 2;
% WaveName         = 'sin_wave';
% [ Result ] = AO_LoadWaveToEmbedded(Samples, SamplesCount, DownSampleFactor, WaveName)
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%