function [Result, MoveMotorTS] = AO_GetMoveMotorTS()


% brief  Get the system timestamp when the drive start moving.
% param  MotorMoveTS [OUT] The system timestamp when the drive start moving.
% return eAO_OK            Success.
% return eAO_FAIL          if the drive not connected.
% return eAO_NOT_CONNECTED if the system is not connected.

AO_Functions;
[Result, MoveMotorTS] = MexFileSystemSDK(AO_GetMoveMotorTS_IDX);
if (Result ~= 0)
	AO_DisplayError();
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Example
%
% [Result, MoveMotorTS] = AO_GetMoveMotorTS();
% if (Result == 0)
%	display(MoveMotorTS);
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%