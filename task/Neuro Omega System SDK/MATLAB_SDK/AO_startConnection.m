function [Result] = AO_StartConnection(SystemMAC, UserMAC, AdpaterIndex)
  
% brief  Establish connection to system.
% param  SystemMAC    [IN] System MAC Address, i.e. '00:21:BA:07:AB:9E'.
% param  UserMAC      [IN] User (caller) artificial MAC Address, i.e. '11:1C:7E:6C:7F:BE'.
% param  AdapterIndex [IN] User PC network adapter card index that is connected to the system switch. -1 for auto search.
% return eAO_OK        Success.
% return eAO_BAD_ARG   if AdapterIndex < 0 and not equal to -1.
% return eAO_ALREADY_CONNECTED if connection already in progress.
% return eAO_FAIL      if fail to establish connection.

% Establish connection to the system.

AO_Functions;
[Result] = MexFileSystemSDK(AO_StartConnection_IDX, SystemMAC, UserMAC, AdpaterIndex);
if (Result ~= 0)
	AO_DisplayError();
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Example for using this function
%
%
% SystemMAC    = 'E0:69:95:35:30:99'; % This have to be the mac address of your system
% UserMAC      = '00:21:ba:07:ab:9e'; % MAC address of the pc which run this matlab
% AdpaterIndex = -1; % Auto Search
% 
% Result = AO_startConnection(SystemMAC, UserMAC, AdpaterIndex);
% 
% for j=1:100,
%     pause(1);
%     ret=AO_IsConnected;
%     if ret==1
%         'The System is Connected'
%         break;
%     end
% end

%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%