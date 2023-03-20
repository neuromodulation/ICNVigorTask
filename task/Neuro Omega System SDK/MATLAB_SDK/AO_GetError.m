function [Result, ErrorCount, LastError] = AO_GetError()

% brief  Get total errors count and the last error occur.
% param  ErrorCount  [OUT] Total errors count since app start running.
% param  LastError   [OUT] The last error occur.
% return eAO_OK       Success.

AO_Functions;
[Result, ErrorCount, LastError] = MexFileSystemSDK(AO_GetError_IDX);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Example for using this function
%
% [Result, ErrorCount, LastError] = AO_GetError();
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%