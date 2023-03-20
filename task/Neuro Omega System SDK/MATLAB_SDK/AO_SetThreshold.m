function [Result] = AO_SetThreshold(ChannelID, Threshold, Direction)

% brief  Change SEGMENTED channel level line threshold and direction.
% param  ChannelID   [IN] The requested SEGMENTED channel ID.
% param  Threshold   [IN] Level line new threshold in Micro Volts.
% param  Direction   [IN] Level line new direction. 1 - Down, 2 - Up. See EAOLevelLineDirection.
% return eAO_OK            Success. i.e. Request sent successfuly.
% return eAO_BAD_ARG       if Direction different than 1 - Down and 2 - Up. See EAOLevelLineDirection.
% return eAO_BAD_ARG       if Threshold out of range.
% return eAO_BAD_ARG       if the channel is not segmented.
% return eAO_CHANNEL_NOT_EXIST if no channel found with the given ID ChannelID.
% return eAO_NOT_CONNECTED if the system is not connected.

AO_Functions;
[Result] = MexFileSystemSDK(AO_SetChannelThreshold_IDX, ChannelID, Threshold, Direction);
if (Result ~= 0)
	AO_DisplayError();
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Example of using this function
%
% ChannelID = 10256;
% Threshold = 100;
% Direction =  1; 
% [Result]  = AO_SetThreshold(ChannelID, Threshold, Direction);
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%