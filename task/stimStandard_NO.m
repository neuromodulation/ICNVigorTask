function stimStandard_NO(stimChannel, returnChannel, stimAmp, stimPulseWidth, stimFreq, stimDuration)

% Deliver stimulation
AO_StartDigitalStimulation(stimChannel,... % stimulation channel
                           0,... % first phase delay in ms
                           -stimAmp,... % first phase amplitude (initial negative)
                           stimPulseWidth/1000,... % first phase duration in ms
                           0,... % second phase delay in ms
                           stimAmp,... % second phase amplitude
                           stimPulseWidth/1000,... % second phase duration in ms 
                           stimFreq,... % stimulation frequency in Hz
                           stimDuration,... stimulation duration in s
                           returnChannel); % return channel (-1 = monopolar)
    
end