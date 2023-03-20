function [Result] = AO_SetChannelSaveState(ChannelID, SaveState)

% brief  Set channel saving state.
% param  ChannelID [IN] The requested channel ID.
% param  SaveState [IN] Save status. TRUE - channel saved to mpx file when saving in progress, otherwise not saved.
% return eAO_OK            Success.
% return eAO_CHANNEL_NOT_EXIST if no channel found with the given ID ChannelID.
% return eAO_NOT_CONNECTED if the system is not connected.

AO_Functions;
[Result] = MexFileSystemSDK(AO_SetChannelSaveState_IDX, ChannelID, SaveState);
if (Result ~= 0)
	AO_DisplayError();
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Example for using this function
% 
% For SaveState = TRUE we will check the check box in v
% ChannelID = 10256
% SaveState = 1;
% [Result]  = AO_SetChannelSaveState(ChannelID, SaveState)
%
% For SaveState = FALSE we will uncheck the check box
% ChannelID = 10256
% SaveState = 0;
% [Result]  = AO_SetChannelSaveState(ChannelID, SaveState)
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%