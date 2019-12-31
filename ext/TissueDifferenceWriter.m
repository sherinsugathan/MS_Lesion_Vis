clc;
clear all;

%maskVolumeFile = 'C:\\DATASET\\MS_dataset_Frank_ProcessReady\\OFAMS00014_DONE\\lesionMask\\test2train_bb2_hard_seg.nii';
%niftyDataFile = 'C:\\DATASET\\MS_dataset_Frank_ProcessReady\\OFAMS00014_DONE\\structural\\T1.nii';
maskVolumeFile = 'D:\\DATASET\\MS_SegmentationChallengeDataset\\01016SACH_DATA\\lesionMask\\Consensus.nii';
niftyDataFile = 'D:\\DATASET\\MS_SegmentationChallengeDataset\\01016SACH_DATA\\structural\\T1.nii';
outputDataFile = 'C:/T1_LesionDifferencePlotted.nii'

origin = [0 0 0]; datatype = 4;
maskVolume = load_untouch_nii(maskVolumeFile);

niftyData = load_untouch_nii(niftyDataFile)

%save_untouch_nii(niftyData,'C:/T12.nii')
%view_nii(niftyData)

mask = maskVolume.img;  % Apply mask from Frank
mask(1,1,1)
mask(mask==255)=1;
pixelData = niftyData.img;  % Read and use nifty data.
outputData = niftyData.img;

l=192;
w=256;
h=256;
windowSize=5;
windowElementCount = windowSize*windowSize*windowSize;
padding = floor(windowSize/2);
maskCount=0;
hotBlockCount=0;
for i=1+padding:l-padding
    for j=1+padding:w-padding
        for k=1+padding:h-padding
           if(mask(k,j,i)==1)
               maskCount = maskCount +1;
               windowMask=mask(k-padding:k+padding,j-padding:j+padding,i-padding:i+padding);
               if(sum(windowMask(:))~=windowElementCount)
                    windowData=pixelData(k-padding:k+padding,j-padding:j+padding,i-padding:i+padding);
                    avgLesion = mean(windowData(windowMask==1));
                    avgTissue = mean(windowData(~windowMask==1));
                    hotBlockCount = hotBlockCount +1;
                    outputData(k,j,i)=abs(avgLesion - avgTissue);
               end
           end
        end
    end
end

fprintf('Number of blocks traversed: %d\n',maskCount);
fprintf('Number of hot blocks: %d\n',hotBlockCount);
% Save output data.
%outputData = niftyData.img;
niftyData.img = outputData;
%nii=make_nii(outputData,[], origin, datatype);
%nii.hdr = niftyData.hdr;
save_untouch_nii(niftyData,outputDataFile)
disp('COMPLETED')