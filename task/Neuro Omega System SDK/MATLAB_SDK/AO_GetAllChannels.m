function [Result, ChannelsInfo] = AO_GetAllChannels()

% brief  Get channel information for each defined channel.
% param  ChannelsInfo  [OUT] The channels information buffer.
% return eAO_OK            Success.
% return eAO_NOT_CONNECTED if the system is not connected.

AO_Functions;
[Result, ChannelsInfo] = MexFileSystemSDK(AO_GetAllChannels_IDX);
if (Result ~= 0)
	AO_DisplayError();
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Example for using this function
%[Result, ChannelsInfo] = AO_GetAllChannels()
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%