function [Result, Data, DataCapture] = AO_GetChannelData(ChannelID)

% brief  Get channel data.
% param  ChannelID   [IN]  The requested channel ID.
% param  Data        [OUT] Array to fill the returned channel data.
% param  DataCapture [OUT] The actual returned channel data size in Data.
% return eAO_OK            Success.
% return eAO_FAIL          if the given channel not buffered. i.e. AddBufferChannel was not called for the given channel.
% return eAO_CHANNEL_NOT_EXIST if no channel found with the given ID ChannelID.
% return eAO_NOT_CONNECTED if the system is not connected.

% Note: Must call AddBufferChannel ONE TIME for each channel desired to get its data.
% Note: It is forbidden to call GetChannelData and GetAlignedData from different threads in parallel.

% Please advice the SDK Manual for extra information.

AO_Functions;
[Result, Data, DataCapture] = MexFileSystemSDK(AO_GetChannelData_IDX, ChannelID);
if (Result ~= 0)
	AO_DisplayError();
end

 
 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
 %Example for using this function
 %
 %
 %[Result, Data, DataCapture] = AO_GetChannelData(10000);
 %
 %
 %explanation of the data in the pData:
 %the pData will contain StreamDataBlock block of data
 %the format of the StreamDataBlock is as follow
 %		byte 1-2  SizeOFtheBlock in words (1 word ==2Byte) including the samples in this block so in order to calculate the number of sample in this channel do the following
 %samplescount=SizeOFtheBlock-headerSizeWord=SizeOFtheBlock-14/7
 %		byte 3    BlockType  (in our case alwayes will be 'd' or 100)
 %		byte 4    notused
 %		byte 5-6  ChannelNumber  the id of the chanel this block belong to
 %		byte 7		unit number ,this value valid only for segmented data
 %		byte 8    notused
 %		byte 9-12 TimeStamp of the first sample of the block you will have to reorder them [byte10 byte9 byte12 byte11]
 %		byte 13-14 uOverFlowCount the over flow of the time stamp
 %		byte 15-16 first sample
 %		byte 17-18 second sample
 %...
 %
 %the total data in the pData is DataCapture the rest of the data is not valid
 %%%%%%%%%%%%%%%%