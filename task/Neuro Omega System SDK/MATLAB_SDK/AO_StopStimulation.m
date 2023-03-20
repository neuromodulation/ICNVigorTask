function [Result] = AO_StopStimulation(ContactID)

% brief  Request to stop stimulation on specific analog input contact.
% param  ContactID [IN] The requested analog input contact ID. -1 if request to stop all current stimulating contacts.
% return eAO_OK                Success. i.e. Request sent successfuly.
% return eAO_NO_STIMULATION    if the given contact stim type is eStimType_NoStim.
% return eAO_CONTACT_NOT_EXIST if no contact found with the given ID ContactID.
% return eAO_NOT_CONNECTED     if the system is not connected.

% On success, the system will stop stimulate on the specific contact.

AO_Functions;
[Result] = MexFileSystemSDK(AO_StopStimulation_IDX, ContactID);
if (Result ~= 0)
	AO_DisplayError();
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Example of using this function
%
% AO_StopStimulation(10000) % stop stimulation on contact 10000 
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%