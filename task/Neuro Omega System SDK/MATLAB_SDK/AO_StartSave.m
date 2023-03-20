function [Result] = AO_StartSave()

% brief  Start saving mpx file on the saving PC.
% return eAO_OK            Success. i.e. Request sent successfuly.
% return eAO_NOT_CONNECTED if the system is not connected.
 
AO_Functions;
Result = MexFileSystemSDK(AO_StartSave_IDX);
if (Result ~= 0)
	AO_DisplayError();
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Example for using this Function
%
% AO_StartSave(); % start saving on the Neuro Omega
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%