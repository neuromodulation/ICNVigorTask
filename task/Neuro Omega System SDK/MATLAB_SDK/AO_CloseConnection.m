function [Result] = AO_CloseConnection()

% brief  Disconnect system connection.
% return eAO_OK Success.

AO_Functions;
[Result] = MexFileSystemSDK(AO_CloseConnection_IDX);
if (Result ~= 0)
	AO_DisplayError();
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Example for using this function
% Results = AO_CloseConnection();
% if (Results == 0)
%     display('Connection closed successfully');
% else
%     display('Connection close error');
% end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%