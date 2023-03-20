function [Result, Depth] = AO_GetDriveDepth()

% brief  Get the current drive depth.
% param  Depth [OUT] The current drive depth in uM.
% return eAO_OK            Success.
% return eAO_FAIL          if the drive not connected.
% return eAO_NOT_CONNECTED if the system is not connected.

AO_Functions;
[Result, Depth] = MexFileSystemSDK(AO_GetDriveDepth_IDX);
if (Result ~= 0)
	AO_DisplayError();
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Example of using this function:
%
% [Result, Depth] =  AO_GetDriveDepth();
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%