function [Result] = AO_SetSavePath(SavePath)

% brief  Change mpx files saving directory.
% param  SavePath [IN] mpx files new saving directory path, i.e. 'C:\\Surgeries_Data\\Patient_X\\'.
% return eAO_OK            Success. i.e. Request sent successfuly.
% return eAO_BAD_ARG       if length(SavePath) < 0 or length(SavePath) > 100.
% return eAO_NOT_CONNECTED if the system is not connected.

% Path must exist on the saving PC.
% Note: Success does not guarantee that the Neuro Omega UI changed the path. Request might fail.

AO_Functions;
[Result] = MexFileSystemSDK(AO_SetSavePath_IDX, SavePath);
if (Result ~= 0)
	AO_DisplayError();
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% example of using this function
%
% SavePath = 'c:\logging_data\'; % The path of the directory to save in
%
% AO_SetSavePath(SavePath); %set the path of the saving to 'c:\logging_data\'
%
% AO_StartSave(); %start saving, the file will be saved at 'c:\logging_data\'
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%