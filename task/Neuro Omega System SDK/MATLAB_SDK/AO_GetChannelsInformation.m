function information = AO_GetChannelsInformation()

%% This function return array of structs that contain information for all the 
%  channels: the name of the channel, the id , LP frequency , HP frequency 
%  and the save state of the channel.

    information = struct('channelName' , {} , 'channelID' , {} ,'LPFreq' , {}, 'HPFreq' , {} ,'SaveState' , {});
    [ Result(1) , channelsData ] = AO_GetAllChannels();
    for i=1:length(channelsData)
        information(i).channelName = channelsData(i).channelName;
        information(i).channelID = channelsData(i).channelID;
        [ Result(i+1), FCLP , FCHP ] = AO_GetCutOffFC( channelsData(i).channelID );
        information(i).LPFreq = FCLP;
        information(i).HPFreq = FCHP;
        [ Result2(i) , status ] = AO_GetChannelSaveState( channelsData(i).channelID );
        information(i).SaveState = status;
    end

end

 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
 %Example for using this function
 %
 %information = AO_GetChannelsInformation( )
 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%