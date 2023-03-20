function [Result, ChannelID] = AO_TranslateNameToID(ChannelName)

%brief  Get Channel ID according to Channel Name.
%param  ChannelName [IN]  The requested channel name, i.e. 'SPK 01'.
%param  ChannelID   [Out] The channel ID of the channel ChannelName.
%return eAO_OK            Success.
%return eAO_CHANNEL_NOT_EXIST if no channel found with the given name ChannelName.
%return eAO_NOT_CONNECTED if the system is not connected.

AO_Functions;
[Result, ChannelID] = MexFileSystemSDK(AO_TranslateNameToID_IDX, ChannelName);
if (Result ~= 0)
	AO_DisplayError();
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Example of using this function
%
% [Result, ChannelID] =  AO_TranslateNameToID('LPF_01'); 
% ans--> channelID = 10000
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%