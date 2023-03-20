function [Result] = AO_StopSave()

% brief  Stop saving mpx file on the saving PC, if saving in progress...
% return eAO_OK            Success. i.e. Request sent successfuly.
% return eAO_NOT_CONNECTED if the system is not connected.

AO_Functions;
[Result] = MexFileSystemSDK(AO_StopSave_IDX);
if (Result ~= 0)
	AO_DisplayError();
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Example for using this function
%
% AO_StopSave(); % stop saving
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%