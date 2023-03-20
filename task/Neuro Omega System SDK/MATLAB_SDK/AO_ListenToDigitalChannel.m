function [Result] = AO_ListenToDigitalChannel(DigitalChannelID, Mask, Time_mS);

%brief  Block application until getting data for the given digital channel.
%param  DigitalChannelID [IN] The requested digital channel ID.
%param  Mask             [IN] The desired relevant bits. Only first 8 bits used. i.e. '0xFF'.
%param  Time_mS          [IN] The time to wait for the given digital channel. -1 - Infinit.
%return eAO_OK            Success. i.e. digital channel DigitalChannelID received.
%return eAO_FAIL          if stop listen before digital channel DigitalChannelID received.
%return eAO_BAD_ARG       if DigitalChannelID not digital input/output.
%return eAO_BAD_ARG       if Mask use bytes other than the first byte.
%return eAO_CHANNEL_NOT_EXIST if no channel found with the given ID DigitalChannelID
%return eAO_NOT_CONNECTED if the system is not connected.

AO_Functions;
[Result] = MexFileSystemSDK(AO_ListenToDigitalChannel_IDX, DigitalChannelID, Mask, Time_mS);
if (Result ~= 0)
	AO_DisplayError();
end
