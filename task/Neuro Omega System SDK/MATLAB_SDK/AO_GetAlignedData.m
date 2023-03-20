function [Result, Data, DataCapture, FirstSampleTS] = AO_GetAlignedData(ChannelsIDs)

% brief  Get multiple channels samples starting from same timestamp.
% param  Data          [OUT] The samples buffer.
% param  DataCapture   [OUT] The actual number of samples filled in Data.
% param  ChannelsIDs   [IN ] Requested channels IDs array.
% param  FirstSampleTS [OUT] The first sample timestamp. Common for all channels samples buffer.
% return eAO_OK            Success.
% return eAO_FAIL          if one of the given channels not buffered. i.e. AddBufferChannel was not called for the channel.
% return eAO_FAIL          if one of the given channel buffered but has no data.
% return eAO_BAD_ARG       if one of the given channels not analog input continuous. i.e. SPK/LFP/RAW...
% return eAO_BAD_ARG       if not all the given channels have the same sampling rate.
% return eAO_CHANNEL_NOT_EXIST if one of the given channels not found.
% return eAO_NOT_CONNECTED if the system is not connected.

% The result in Data is as follow:
% The samples count for each channel is (DataCapture/ChannelsCount).
% For the channel at index i the samples in Data starts from index (DataCapture/ChannelsCount)*i. i in range [0..ChannelsCount-1]

% Note: Must call AddBufferChannel ONE TIME for each channel desired to get its data.
% Note: It is forbidden to call GetChannelData and GetAlignedData from different threads in parallel.

% Please advice the SDK Manual for extra information.

if (~isempty(find(isnan(ChannelsIDs)==1)) || ~isreal(ChannelsIDs))
    ChannelsIDs = '';
end

if (isinteger(ChannelsIDs))
	ChannelsIDs = double(ChannelsIDs);
end

AO_Functions;
[Result, Data, DataCapture, FirstSampleTS] = MexFileSystemSDK(AO_GetAlignedData_IDX, ChannelsIDs);
if (Result ~= 0)
	AO_DisplayError();
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Example for using this function
%
%
% ChannelsIDs   = [10000, 10001, 10002];
%
% Get aligned data from channels:10000,10001,10002 save them in the array Data, the aligment is done by timestamp FirstSampleTS
% [Result, Data, DataCapture, FirstSampleTS] = AO_GetAlignedData(ChannelsIDs);
% 
% explination on the returned data:
% Data will contain only samples of data in A/D values including gain for all the channels, the number of valid samples in this array is DataCapture so make sure that you only get DataCapture samples
% The first "DataCapture/ChannelsCount" samples is for the first channel in the array ChannelsIDs ....
%
% FirstSampleTS is the timestamp for the first sample for each one of the channels
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%