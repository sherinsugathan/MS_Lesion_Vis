import vtk
import enum

class VisType(enum.Enum):
    DEFAULT = 0 # Provides a default visualization of brain data with no processing.
    TRANSPARENT = 1 # Provides a data visualization of subjects with transparency. (Only depth peeling supported currently)
    RAW_LESION_INTENSITY = 2 # Provides a raw visualization of actual surface intensity of lesions.
    RAW_LESION_CONTRAST = 3 # Provides a contrast visualization of lesions where its intensities are compared with surrounding.
    LESION_CLASS_VIEW = 4 # Provides a classification of lesions based on their intensity with respect to the surrounding normal tissue.
    SURFACE_MAPPING = 5 # Provides a visualization of lesion mapping to the surface.

class Settings:
  def __init__(self, lh_pial_enabled, rh_pial_enabled, lh_white_enabled, rh_white_enabled, lesions_enabled, lh_pial_transparency, rh_pial_transparency, lh_white_transparency, rh_white_transparency, depthPeelingEnabled, visType):
    self.lh_pial_enabled = "lh.pial.obj", lh_pial_enabled
    self.rh_pial_enabled = "rh.pial.obj", rh_pial_enabled
    self.lh_white_enabled = "lh.white.obj", lh_white_enabled
    self.rh_white_enabled = "rh.white.obj", rh_white_enabled
    self.lesions_enabled = "lesions.obj", lesions_enabled
    self.lh_pial_transparency = lh_pial_transparency
    self.rh_pial_transparency = rh_pial_transparency
    self.lh_white_transparency = lh_white_transparency
    self.rh_white_transparency = rh_white_transparency
    self.depthPeelingEnabled = depthPeelingEnabled
    self.visType = visType
  def __str__(self):
    return "Lh Pial Enabled:" + str(self.lh_pial_enabled[1]) + ", Rh Pial Enabled:" + str(self.rh_pial_enabled[1]) +  ", Lh White Enabled:" + str(self.lh_white_enabled[1]) + \
      ", Rh White Enabled:" + str(self.rh_white_enabled[1]) + ", Lesions Enabled:" + str(self.lesions_enabled[1]) + ", Lh Pial Transparency:" + str(self.lh_pial_transparency) + ", Rh Pial Transparency:" + str(self.rh_pial_transparency) + \
         ", Lh White Transparency:" + str(self.lh_white_transparency) + ", Rh White Transparency:" + str(self.rh_white_transparency) + \
           ", Depth Peeling Enabled:" + str(self.depthPeelingEnabled) + ", Vis Type:" + str(self.visType) 
  
  def getSurfaceWhiteList(self):
    whiteList = []
    if(self.lh_pial_enabled[1] == True):
      whiteList.append(self.lh_pial_enabled[0])
    if(self.rh_pial_enabled[1] == True):
      whiteList.append(self.rh_pial_enabled[0])
    if(self.lh_white_enabled[1] == True):
      whiteList.append(self.lh_white_enabled[0])
    if(self.rh_white_enabled[1] == True):
      whiteList.append(self.rh_white_enabled[0])
    if(self.lesions_enabled[1] == True):
      whiteList.append(self.lesions_enabled[0])
    return whiteList

# Get view settings for a specific visualization.
def getSettings(visType):
  setting = None
  if(visType == VisType.DEFAULT): # Default View
    setting = Settings(True, True, True, True, True, 1.0, 1.0, 1.0, 1.0, True, VisType.DEFAULT)
  elif(visType == VisType.TRANSPARENT): # Transparent view with few surfaces.
    setting = Settings(True, True, False, False, True, 0.5, 0.5, 0.5, 0.5, True, VisType.TRANSPARENT)
  elif(visType == VisType.RAW_LESION_INTENSITY): # Raw intensity color map on lesions.
    setting = Settings(True, True, False, False, True, 0.5, 0.5, 0.5, 0.5, True, VisType.RAW_LESION_INTENSITY)
  elif(visType == VisType.RAW_LESION_CONTRAST): # Continuous color map of lesion contrast.
    setting = Settings(True, True, True, True, True,  0.5, 0.5, 0.5, 0.5, True, VisType.RAW_LESION_CONTRAST)
  elif(visType == VisType.LESION_CLASS_VIEW): # Class view of lesions based on intensity contrast w.r.t normal white matter.
    setting = Settings(True, True, True, True, True,  0.5, 0.5, 0.5, 0.5, True, VisType.LESION_CLASS_VIEW)
  elif(visType == VisType.SURFACE_MAPPING): # Lesions projected to surface view.
    setting = Settings(True, True, True, True, True, 0.5, 0.5, 0.5, 0.5, True, VisType.SURFACE_MAPPING)
  return setting

# Mapping vis type selection to enums.
def visMapping(selection):
  if(selection=="Default View"):
    return VisType.DEFAULT
  elif(selection=="Transparent Surfaces"):
    return VisType.TRANSPARENT
  elif(selection=="Lesion Intensity Raw Vis."):
    return VisType.RAW_LESION_INTENSITY
  elif(selection=="Lesion Difference With NAWM"):
    return VisType.RAW_LESION_CONTRAST
  elif(selection=="Lesion Classification View"):
    return VisType.LESION_CLASS_VIEW
  elif(selection=="Lesion Surface Mapping"):
    return VisType.SURFACE_MAPPING


class LesionFilterParamSettings:
  def __init__(self, lesionNumberOfPixels, lesionElongation, lesionPerimeter, lesionSphericalRadius, lesionSphericalPerimeter, lesionFlatness, lesionRoundness):
    self.lesionNumberOfPixels = lesionNumberOfPixels
    self.lesionElongation = lesionElongation
    self.lesionPerimeter = lesionPerimeter
    self.lesionSphericalRadius = lesionSphericalRadius
    self.lesionSphericalPerimeter = lesionSphericalPerimeter
    self.lesionFlatness = lesionFlatness
    self.lesionRoundness = lesionRoundness 