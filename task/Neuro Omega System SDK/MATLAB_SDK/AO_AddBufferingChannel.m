function [Result] = AO_AddBufferingChannel(ChannelID, BufferingTime_mSec)

% brief  Request to buffer (store) specific channel data.
% param  ChannelID          [IN] The requested channel ID, i.e. 10000, 10001 ...
% param  BufferingTime_mSec [IN] Channel data acquisition window in mSec.
% return eAO_OK            Success.
% return eAO_BAD_ARG       if nBufferingTime_mSec not in range [5000..20000] mSec.
% return eAO_CHANNEL_NOT_EXIST if no channel found with the given ID nChannelID.
% return eAO_NOT_CONNECTED if the system is not connected.

% Start data acquisition to channel ChannelID.
% Buffer the last BufferingTime_mSec data.

AO_Functions;
[Result] = MexFileSystemSDK(AO_AddBufferChannel_IDX, ChannelID, BufferingTime_mSec);
if (Result ~= 0)
	AO_DisplayError();
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Example for using this function
%
% ChannelID          = 10256; Set the channel number 
% BufferingTime_mSec = 10000; Set the size of the buffer in mSec
% AO_AddBufferingChannel(ChannelID, BufferingTime_mSec)
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 