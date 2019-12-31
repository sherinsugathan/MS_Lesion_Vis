import SimpleITK as sitk
import vtk
import numpy as np
import sys, os

subjectString = "08037ROGU_DATA"
fileNameT1 = "D:\\DATASET\\MS_SegmentationChallengeDataset\\"+subjectString+"\\structural\\T1.nii"
fileNameMask = "D:\\DATASET\\MS_SegmentationChallengeDataset\\"+subjectString+"\\lesionMask\\Consensus.nii"
fileNameResampledMask = "D:\\DATASET\\MS_SegmentationChallengeDataset\\"+subjectString+"\\lesionMask\\ConsensusResampled.nii"

readerT1 = sitk.ImageFileReader()
readerT1.SetFileName(fileNameT1)
readerT1.LoadPrivateTagsOn()
readerT1.ReadImageInformation()
readerT1.LoadPrivateTagsOn()
imageT1 = sitk.ReadImage(fileNameT1)

#for k in readerT1.GetMetaDataKeys():
#    v = readerT1.GetMetaData(k)
#    print("({0}) = = \"{1}\"".format(k,v))


#print(readerT1.GetMetaData("srow_x").split()[:3])
#print#(readerT1.GetMetaData("srow_y").split()[:3])
#print(readerT1.GetMetaData("srow_z").split()[:3])
#print(directionMatrix)

#print(readerT1.GetTransform())
#quit()

readerMask = sitk.ImageFileReader()
readerMask.SetFileName(fileNameMask)
readerMask.LoadPrivateTagsOn()
readerMask.ReadImageInformation()
imageMask = sitk.ReadImage(fileNameMask)

origin = (float(readerMask.GetMetaData("qoffset_x")), float(readerMask.GetMetaData("qoffset_y")), float(readerMask.GetMetaData("qoffset_z")))

directionMatrix = readerMask.GetMetaData("srow_x").split()[:3]
directionMatrix.extend(readerMask.GetMetaData("srow_y").split()[:3])
directionMatrix.extend(readerMask.GetMetaData("srow_z").split()[:3])
directionMatrix = tuple(list(map(float, directionMatrix)))

targetSpacingX = readerT1.GetSpacing()[0]
targetSpacingY = readerT1.GetSpacing()[1]
targetSpacingZ = readerT1.GetSpacing()[2]


# Resample Mask data.
resampleMask = sitk.ResampleImageFilter()
resampleMask.SetInterpolator(sitk.sitkLinear)
resampleMask.SetOutputDirection(imageMask.GetDirection())
resampleMask.SetOutputOrigin(imageMask.GetOrigin())
new_spacingMask = [targetSpacingX, targetSpacingY, targetSpacingZ]
new_spacingMasktuple = np.array([targetSpacingX, targetSpacingY, targetSpacingZ], dtype=np.float)
orig_sizeMask = np.array(readerMask.GetSize(), dtype=np.int)
orig_spacingMask = np.array(readerMask.GetSpacing(), dtype=np.float)
print("New spacing")
print(new_spacingMask)
new_size = orig_sizeMask*(orig_spacingMask/new_spacingMask)
new_size = np.ceil(new_size).astype(np.int) #  Image dimensions are in integers
new_size = [int(s) for s in new_size]
print("New size")
print(new_size)
resampleMask.SetSize(new_size)
resampleMask.SetOutputSpacing(new_spacingMask)
resampleMask.SetOutputPixelType(readerMask.GetPixelID())
newImageMask = resampleMask.Execute(imageMask)
# Write resampled data.
writerMask = sitk.ImageFileWriter()
writerMask.SetFileName(fileNameResampledMask)
writerMask.Execute(newImageMask)


print("#################################################")
print("T1 Image Size: {0}".format(readerT1.GetSize()))
print("T1 Image Spacing: {0}".format(readerT1.GetSpacing()))
print("T1 GetOrigin(): {0}".format(readerT1.GetOrigin()))
print("T1 Direction: {0}".format(readerT1.GetDirection()))
print("T1 Image PixelType: {0}".format(sitk.GetPixelIDValueAsString(readerT1.GetPixelID())))
print("#################################################")
print("Mask Image Size: {0}".format(readerMask.GetSize()))
print("Mask Image Spacing: {0}".format(readerMask.GetSpacing()))
print("Mask GetOrigin(): {0}".format(readerMask.GetOrigin()))
print("Mask Direction: {0}".format(readerMask.GetDirection()))
print("Mask Image PixelType: {0}".format(sitk.GetPixelIDValueAsString(readerMask.GetPixelID())))
print("#################################################")

# pt = (-79.18413543701172, -127.30085754394531, -127.94029235839844)
# idx = (176, 256, 256)

# print("Voxel {} is point {}.".format(idx, imageT1.TransformIndexToPhysicalPoint(idx)))
# print("Voxel {} is point {}.".format(idx, imageMask.TransformIndexToPhysicalPoint(idx)))
# print("Point {} is voxel {}.".format(pt, imageMask.TransformPhysicalPointToIndex(pt)))
# print("Point {} is voxel {}.".format(pt, imageT1.TransformPhysicalPointToIndex(pt)))



print("DONE")

# euler3DTransform = sitk.Euler3DTransform()
# euler3DTransform.SetMatrix([-1, 0, 0, 0, -1, 0, 0, 0, 1,0,0,0])

#rotation3 = sitk.VersorRigid3DTransform()
#rotation3.SetTranslation([5,5,5])
#print(rotation3.GetMatrix())
#rotation3.SetMatrix([-1, 0, 0, 0, -1, 0, 0, 0, 1,0,0,0]);
