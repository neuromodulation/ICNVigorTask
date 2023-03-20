function [bConnected] = AO_IsConnected()

% brief  Check system connection status.
% return eAO_DISCONNECTED  The SDK is disconnected from the system.
% return eAO_CONNECTED     The SDK is connected to the system.
% return eAO_CONNECTING    The SDK is trying to connect to the system.

AO_Functions;
bConnected = MexFileSystemSDK(AO_IsConnected_IDX);
 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Example for using this function
%
% SystemMAC = '3c:2d:b7:41:0a:54';
% UserMAC   = 'DD:EE:FF:AA:BB:CC';
%
% [bConnected] = AO_StartConnection(SystemMAC, UserMAC, -1);
%
% for j=1:100,
%     pause(1);
%     bConnected=AO_IsConnected;
%     if bConnected==1
%         'The System is Connected'
%         break;
%     end
% end
% 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
