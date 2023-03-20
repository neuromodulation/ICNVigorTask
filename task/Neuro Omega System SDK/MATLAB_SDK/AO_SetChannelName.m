function [Result] = AO_SetChannelName(ChannelID, NewName)

% brief  Change channel name for the channel with ID ChannelID.
% param  ChannelID [IN] The requested channel ID.
% param  NewName   [IN] The requested channel new name, i.e. 'SPK 01'.
% return eAO_OK            Success. i.e. Request sent successfuly.
% return eAO_BAD_ARG       if length(NewName) <= 0 || length(NewName) > 29.
% return eAO_CHANNEL_NOT_EXIST  if no channel found with the given ID ChannelID.
% return eAO_CHANNEL_NAME_EXIST if there is another channel that have the same name NewName.
% return eAO_NOT_CONNECTED if the system is not connected.
  
AO_Functions;
[Result] = MexFileSystemSDK(AO_SetChannelName_IDX, ChannelID, NewName);
if (Result ~= 0)
	AO_DisplayError();
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Example of using this function:
% ChannelID = 10258; 
% NewName   = 'left Side';
% [Result] = AO_SetChannelName(ChannelID, NewName);
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%