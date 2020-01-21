import vtk
import enum

class VisType(enum.Enum):
    DEFAULT_FULL_DATA = 0 # Provides a default visualization of all the available brain data with no processing.
    LESION_COLORED_CONTINUOUS = 1 # Provides a data visualization of lesions probed over volume to show the intensity difference with respect to the immediate surrounding normal tissue.
    LESION_COLORED_DISCRETE = 2 # Provides a raw visualization of actual surface intensity of lesions.
    LESION_COLORED_DISTANCE = 3 # Provides a contrast visualization of lesions where its intensities are compared with surrounding.
    LESION_SURFACE_MAPPING = 4 # Provides a visualization of lesion mapping to the surface.

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
  if(visType == VisType.DEFAULT_FULL_DATA): # Default View
    setting = Settings(True, True, True, True, True, 1.0, 1.0, 1.0, 1.0, True, VisType.DEFAULT_FULL_DATA)
  elif(visType == VisType.LESION_COLORED_CONTINUOUS): # Transparent view with few surfaces.
    setting = Settings(False, False, True, True, True, 0.5, 0.5, 0.5, 0.5, True, VisType.LESION_COLORED_CONTINUOUS)
  elif(visType == VisType.LESION_COLORED_DISCRETE): # Raw intensity color map on lesions.
    setting = Settings(True, True, False, False, True, 0.5, 0.5, 0.5, 0.5, True, VisType.LESION_COLORED_DISCRETE)
  elif(visType == VisType.LESION_COLORED_DISTANCE): # Continuous color map of lesion contrast.
    setting = Settings(False, False, True, True, True,  0.5, 0.5, 0.5, 0.5, True, VisType.LESION_COLORED_DISTANCE)
  elif(visType == VisType.LESION_SURFACE_MAPPING): # Lesions projected to surface view.
    setting = Settings(False, False, True, True, True, 0.5, 0.5, 0.5, 0.5, True, VisType.LESION_SURFACE_MAPPING)
  return setting

# Mapping vis type selection to enums.
def visMapping(selection):
  if(selection=="Full Data View - Raw"):
    return VisType.DEFAULT_FULL_DATA
  elif(selection=="Lesion Colored - Continuous"):
    return VisType.LESION_COLORED_CONTINUOUS
  elif(selection=="Lesion Colored - Discrete"):
    return VisType.LESION_COLORED_DISCRETE
  elif(selection=="Lesion Colored - Distance"):
    return VisType.LESION_COLORED_DISTANCE
  elif(selection=="Lesion Surface Mapping"):
    return VisType.LESION_SURFACE_MAPPING


class LesionFilterParamSettings:
  def __init__(self, lesionNumberOfPixels, lesionElongation, lesionPerimeter, lesionSphericalRadius, lesionSphericalPerimeter, lesionFlatness, lesionRoundness):
    self.lesionNumberOfPixels = lesionNumberOfPixels
    self.lesionElongation = lesionElongation
    self.lesionPerimeter = lesionPerimeter
    self.lesionSphericalRadius = lesionSphericalRadius
    self.lesionSphericalPerimeter = lesionSphericalPerimeter
    self.lesionFlatness = lesionFlatness
    self.lesionRoundness = lesionRoundness 