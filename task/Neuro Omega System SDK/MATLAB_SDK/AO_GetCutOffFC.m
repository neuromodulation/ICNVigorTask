function [Result, LP_FC, HP_FC] = AO_GetCutOffFC(ChannelID)

% brief  Get contact analog input channel High Pass / Low Pass frequency cutoff.
% param  ChannelID [IN]  The requested channel ID.
% param  LP_FC     [OUT] Channel Low Pass frequency cutoff.
% param  HP_FC     [OUT] Channel High Pass frequency cutoff.
% return eAO_OK            Success.
% return eAO_BAD_ARG       The given channel is not Analog Input channel.
% return eAO_CHANNEL_NOT_EXIST if no channel found with the given ID ChannelID.
% return eAO_NOT_CONNECTED if the system is not connected.

AO_Functions;
[Result, LP_FC, HP_FC] = MexFileSystemSDK(AO_GetCutOffFC_IDX, ChannelID);
if (Result ~= 0)
	AO_DisplayError();
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Example of using this function:
% ChannelID = 10256;
% [Result, LP_FC, HP_FC] = AO_GetCutOffFC(ChannelID)
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%