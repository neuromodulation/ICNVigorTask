function [Result, Data, ActualDataSize] = AO_GetNextBlock(DataSize)

% brief  Get last received Stream Base blocks from the system.
% param  DataSize       [IN]  Requested Data Stream Base buffer size.
% param  Data           [OUT] Stream Base buffer.
% param  ActualDataSize [OUT] The actual number of data filled in Data in words unit.
% return eAO_OK            Success.
% return eAO_BAD_ARG       if DataSize <= 0.
% return eAO_NOT_CONNECTED if the system is not connected.

AO_Functions;
[Result, Data, ActualDataSize] = MexFileSystemSDK(AO_GetNextBlock_IDX, DataSize);
if (Result ~= 0)
	AO_DisplayError();
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Example of using this function
%
% [Result, Data, ActualDataSize] = AO_GetNextBlock(50000);
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%