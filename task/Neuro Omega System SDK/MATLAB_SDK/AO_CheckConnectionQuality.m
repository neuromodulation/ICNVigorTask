function [Result, QualityType, QualityPercent] = AO_CheckConnectionQuality()

% brief  Check system connection quality.
% param  QualityType      [OUT] 'POOR' - Poor connection, 'MEDIUM' - Medium connection, 'HIGH' - High connection
% param  QualityPercent   [OUT] System throughput in percent.
% return eAO_OK            Success.
% return eAO_ARG_NULL      One or more of the input arguments is NULL.
% return eAO_NOT_CONNECTED if the system is not connected.

AO_Functions;
[Result, QualityType, QualityPercent] = MexFileSystemSDK(AO_CheckConnectionQuality_IDX);
if (Result ~= 0)
	AO_DisplayError();
else
	if (QualityType == 1) 
		QualityType = 'POOR';
	elseif (QualityType == 2) 
		QualityType = 'MEDIUM';
	elseif (QualityType == 3) 
		QualityType = 'HIGH';
	end
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Example of using this function
%
% [Result, QualityType, QualityPercent] = AO_CheckConnectionQuality();
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 