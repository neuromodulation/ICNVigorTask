function [Result, SystemTS] = AO_GetLatestTimeStamp()

% brief  Get the system timestamp.
% param  SystemTS          [OUT] The system timestamp.
% return eAO_OK            Success.
% return eAO_NOT_CONNECTED if the system is not connected.

AO_Functions;
[Result, SystemTS] = MexFileSystemSDK(AO_GetLatestTimeStamp_IDX);
if (Result ~= 0)
	AO_DisplayError();
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Example of using this function
%
% [Result, SystemTS] = AO_GetLatestTimeStamp()
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%