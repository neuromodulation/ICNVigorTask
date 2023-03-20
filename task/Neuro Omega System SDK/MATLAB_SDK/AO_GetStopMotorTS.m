function [Result, StopMotorTS] = AO_GetStopMotorTS()

%brief  Get the system timestamp when the drive stopped after the last drive movement.
%param  MotorStopTS [OUT] The system timestamp when the drive stopped after the last drive movement.
%return eAO_OK            Success.
%return eAO_FAIL          if the drive not connected.
%return eAO_NOT_CONNECTED if the system is not connected.

AO_Functions;
[Result, StopMotorTS] = MexFileSystemSDK(AO_GetStopMotorTS_IDX);
if (Result ~= 0)
	AO_DisplayError();
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Example
%
% [Result, StopMotorTS] = AO_GetDriveStopTS();
% if (Result == 0)
%	display(StopMotorTS);
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%