function availableChannelsID = init_NO()

%% Connect to NeuroOmega
macNO = 'F4:5E:AB:6B:6D:A1';
nConnectionAttempts = 0;

while (AO_IsConnected() ~= 1) && (nConnectionAttempts < 10)
    nConnectionAttempts = nConnectionAttempts + 1;
    AO_DefaultStartConnection(macNO);
    pause(2)
end

if AO_IsConnected() == 1
    disp('Connection to NeuroOmega established')
else
    warning('Connection to NeuroOmega failed')
end

%% Wait for internal NO init
pause(3)

%% Get channels
[~, tmpChannelsID] = AO_GetAllChannels;
availableChannelsID = tmpChannelsID.channelID;

end