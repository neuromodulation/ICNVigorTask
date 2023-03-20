function [Result] = AO_SendTextEvent(Text)

% brief  Save text to mpx file while saving in progress.
% param  Text [IN] The text to save, i.e. 'Expirement Start'.
% return eAO_OK            Success. i.e. Request sent successfuly.
% return eAO_BAD_ARG       if length(Text) <= 0 or length(Text) > 100.
% return eAO_NOT_CONNECTED if the system is not connected.

% The text event timestamped with the latest system timestamp.

AO_Functions;
[Result] = MexFileSystemSDK(AO_SendTextEvent_IDX, Text);
if (Result ~= 0)
	AO_DisplayError();
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Example of using this function:
%
% [Result] = AO_SendTextEvent('the text is in the mpx file');
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%