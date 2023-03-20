function [Result] = AO_DefaultStartConnection(SystemMAC)

% brief  Establish connection to system.
% param  SystemMAC    [IN] System MAC Address, i.e. '00:21:BA:07:AB:9E'.
% return eAO_OK        Success.
% return eAO_ALREADY_CONNECTED if connection already in progress.
% return eAO_FAIL      if fail to establish connection.

% Establish connection to the system.
% Auto search for user PC network adapter card index that is connected to the system switch.
% Sets user MAC address to 'AA:BB:CC:DD:EE:FF'.

AO_Functions;
[Result] = MexFileSystemSDK(AO_DefaultStartConnection_IDX, SystemMAC);
if (Result ~= 0)
	AO_DisplayError();
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Example for using this function
% SystemMAC = 'c8:a0:30:27:21:bf';
% Result = AO_DefaultStartConnection(SystemMAC)
% 
% for j=1:100
%     pause(1);
%     ret = AO_IsConnected;
%     if ret == 1 
%        fprintf('connected')
%         break;
%     end
% end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%