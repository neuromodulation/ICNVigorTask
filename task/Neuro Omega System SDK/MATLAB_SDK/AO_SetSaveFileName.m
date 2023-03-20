function [Result] = AO_SetSaveFileName(FileName)

% brief  Change mpx files saving base name.
% param  FileName [IN] mpx files new saving base name, i.e. 'ExpirementName.mpx'.
% return eAO_OK            Success. i.e. Request sent successfuly.
% return eAO_BAD_ARG       if length(FileName) <= 0 or length(FileName) > 40.
% return eAO_NOT_CONNECTED if the system is not connected.

% if a file exists with the same name in the saving directory, it might be overriden.
% Note: Success does not guarantee that the Neuro Omega UI changed the mpx files base name. Request might fail.

AO_Functions;
[Result] = MexFileSystemSDK(AO_SetSaveFileName_IDX, FileName);
if (Result ~= 0)
	AO_DisplayError();
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Example for using this function
%
% FileName = 'testFile';    
% [Result] = AO_SetSaveFileName(FileName); %set the file name as testFile
%
% AO_StartSave() % start saving, the file name will be testFile
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%