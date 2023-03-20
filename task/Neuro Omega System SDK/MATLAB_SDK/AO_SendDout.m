function [Result] = AO_SendDout(Mask, Value)

% brief  Generate Digital output on DIG-OUT sockets.
% param  Mask  [IN] Bitwise mask. Only the first byte used.
% param  Value [IN] Bitwise value. Only the first byte used.
% return eAO_OK                Success. i.e. Request sent successfuly.
% return eAO_BAD_ARG           if Mask use bytes other than the first byte.
% return eAO_BAD_ARG           if Value use bytes other than the first byte.
% return eAO_CHANNEL_NOT_EXIST if DIG-OUT socket not exist.
% return eAO_NOT_CONNECTED     if the system is not connected.

% To generate digital output on DIG-OUT socket i (in range [0..7]):
% Mask  bit i should be set.
% Value bit i should be set/clear.

AO_Functions;
[Result] = MexFileSystemSDK(AO_SendDout_IDX, Mask, Value); 
if (Result ~= 0)
	AO_DisplayError();
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Example for using this function
%
% Mask  = '0x00';
% Value = 0;
%
% Result = AO_SendDout(Mask, Value); %Initialize port 11701 to 0
%
% Mask  = '0x05';
% Value = 3;
%
% Result = AO_SendDout(Mask, Value); %set port 11701 
%
% %====> The output of the bits on port 11701 will be '0000 0001'
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%