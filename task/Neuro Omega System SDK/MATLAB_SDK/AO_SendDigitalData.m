function [Result] = AO_SendDigitalData(DigitalChannelID, Mask, Value)

% brief  Generate Digital output on digital output socket.
% param  DigitalChannelID [IN] The digital channel ID. Please advice the SDK Manual appendix.
% param  Mask             [IN] Bitwise mask. Only the first byte used.
% param  Value            [IN] Bitwise value. Only the first byte used.
% return eAO_OK                Success. i.e. Request sent successfuly.
% return eAO_BAD_ARG           if DigitalChannelID not digital output channel.
% return eAO_BAD_ARG           if Mask use bytes other than the first byte.
% return eAO_BAD_ARG           if Value use bytes other than the first byte.
% return eAO_CHANNEL_NOT_EXIST if no channel found with the given ID DigitalChannelID.
% return eAO_NOT_CONNECTED     if the system is not connected.

% To generate digital output on DigitalChannelID bit i (in range [0..7]):
% Mask  bit i should be set.
% Value bit i should be set/clear.

AO_Functions;
[Result] = MexFileSystemSDK(AO_SendDigitalData_IDX, DigitalChannelID, Mask, Value);
if (Result ~= 0)
	AO_DisplayError();
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Example for using this function
%
%   DigitalChannelID = 11707;
%   Mask  = '0x00';
%   Value = 0;
%
%   Result = AO_SendDigitalData(DigitalChannelID, Mask, Value); % Initialize port 11707 to 0

%   Mask  = '0x05';
%   Value = 3;
%
%   Result = AO_SendDigitalData(DigitalChannelID, Mask, Value); % Set port 11707 
%
%   %====> The output of the bits on port 11707 will be '0000 0001'
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%