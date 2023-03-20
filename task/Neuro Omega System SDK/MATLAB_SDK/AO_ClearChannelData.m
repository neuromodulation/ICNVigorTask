function [Result] = AO_ClearChannelData()


% brief  Reset acquisition for all buffered channels.
% return eAO_OK Success.
%
% Delete the buffered channels CURRENT buffered data.
% Note: The SDK will keep buffering new data for the buffered channels.

AO_Functions;
[Result] = MexFileSystemSDK(AO_ClearChannelsData_IDX);
 if (Result ~= 0)
	AO_DisplayError();
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Example of using this function
%
%  AO_ClearChannelData() 
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 