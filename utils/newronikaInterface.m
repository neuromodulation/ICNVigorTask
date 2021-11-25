classdef newronikaInterface < handle
    
    % Input: 
    % labels:   1x2 cell array, names for each channel, e.g. {'LFPR02',
    %           'LFPL13'};
    
    properties
        
        nwkstation % initialized python object that encapsulates communication to the nwkstation
        data % data in fieldtrip data format
        time % counter to keep track of time
        start_time % global start time
        
    end
    
    methods
        
        function obj = newronikaInterface(labels)
                                                         
            % initialize newronika python interface
            obj.nwkstation = py.nwkstation.interface;
            
            % initialize data
            obj.data = struct();
            obj.data.fsample = 128;
            obj.data.label = labels';
            obj.data.trial{1} = [];
            obj.data.time{1} = [];
            obj.data.sampleExtracted = [];
            obj.data.globaltimeExtracted = [];
            
            % initialize time
            obj.time = 0;
            
        end
        
        function sample(obj)
                                                                
            % sample from newronika
            tmpPythonOutput = obj.nwkstation.sampleFromDevice;

            % convert to matlab arrays
            % newronika outputs samples as python lists, hence the
            % clumpy conversion
            samples = [cell2mat(cell(tmpPythonOutput{1})); cell2mat(cell(tmpPythonOutput{2}))];

            % add samples to data
            obj.data.trial{1} = [obj.data.trial{1}, samples];
            
            for sampleIdx = 1:size(samples, 2)
            
                % add time to data
                obj.data.time{1} = [obj.data.time{1}, obj.time];

                % increment time
                obj.time = obj.time + 1/128;
            
            end
                
            % add time of sample extraction
            obj.data.sampleExtracted = [obj.data.sampleExtracted size(samples, 2)];
            global_time = clock;
            global_time = global_time(4:end);
            obj.data.globaltimeExtracted = [obj.data.globaltimeExtracted; global_time];

            
            
        end
            
        function closeConnection(obj)

            % close port to newronika
            obj.nwkstation.closeConnectionToDevice();

        end
        
    end
    
end

