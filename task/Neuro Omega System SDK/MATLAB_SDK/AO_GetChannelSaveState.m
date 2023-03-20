function [Result, SaveState] = AO_GetChannelSaveState(ChannelID)

% brief  Get channel saving state.
% param  ChannelID [IN]  The requested channel ID.
% param  SaveState [OUT] Save status. TRUE - channel saved to mpx file when saving in progress, otherwise not saved.
% return eAO_OK            Success.
% return eAO_CHANNEL_NOT_EXIST if no channel found with the given ID ChannelID.
% return eAO_NOT_CONNECTED if the system is not connected.

AO_Functions;
[Result, SaveState] = MexFileSystemSDK(AO_GetChannelSaveState_IDX , ChannelID);
if (Result ~= 0)
	AO_DisplayError();
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Example for using this function
% ChannelID = 10256;
% [Result, SaveState] = AO_GetChannelSaveState(ChannelID)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%