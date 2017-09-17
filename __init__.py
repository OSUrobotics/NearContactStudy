from __future__ import division, absolute_import, print_function

##### Survey Analysis ####
from NearContact20Survey.createShapesMatlab import ShapeSTLGeneratorPython


##### Setting Some Path Constants ####
import os
BASE_PATH = os.path.dirname(os.path.realpath(__file__))
print(BASE_PATH)
#### Setting Parametrization Constant #####
HAND_PARAM = 32.0 #maximum finger span
PARAMETERIZE = True #general keyword to know if calculations and stuff should be done with paramaterized version or with absolute size


from InterpolateGrasps.Visualizers import Vis, GenVis, ObjectVis, ObjectGenericVis, HandVis, AddGroundPlane, ArmVis
from InterpolateGrasps.Colors import ColorsDict, bcolors
# from InterpolateGrasps.stl_generator import stl_generator
# from InterpolateGrasps.stlwriter import ASCII_STL_Writer, Binary_STL_Writer
from InterpolateGrasps.obj_dict import grasp_obj_dict, obj_centroid_dict


##### Qualtrics Data Processing #####
from NearContact20Survey.QualtricsDataProcessing.KeyMapper import KeyMapper



#### Qualtrics Data Processing ####
from NearContact20Survey.QualtricsDataProcessing.buildPolytopeFromResponses import BuildPolytope, PolytopeParametric, PolytopeNonparametric
from NearContact20Survey.QualtricsDataProcessing.DiscreteAnalysis import DiscreteAnalysis
from NearContact20Survey.QualtricsDataProcessing.ContinuousAnalysis import ContinuousAnalysis
from NearContact20Survey.QualtricsDataProcessing.Parametric import Parametric
from NearContact20Survey.QualtricsDataProcessing.Nonparametric import Nonparametric

##### Qualtrics Survey Parsing #####
from NearContact20Survey.QualtricsGeneration.QualtricsGen.SurveyParser import SurveyParser, multi_choice,  blockelement, flowelement, randomizerelement, LM_temp

##### Qualtrics Data Processing #####
from NearContact20Survey.QualtricsDataProcessing.DataProcessing import csvReader, dataResults, removeUnfinishedRows, removeUnnecessaryColumns
from NearContact20Survey.QualtricsDataProcessing.SurveyResultsParser import SurveyResultsParser

##### Shape Image Generator #####
from ShapeImageGenerator.HandCenteredCSV import HandCenteredCSV
from ShapeImageGenerator.ShapeImageGeneratorTest import ShapeImageGenerator
from ShapeImageGenerator.ShapeImageManipulator import ShapeImageManipulator