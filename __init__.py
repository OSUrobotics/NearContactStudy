from __future__ import division, absolute_import, print_function
import pdb


##### Setting Some Path Constants ####
import os
BASE_PATH = os.path.dirname(os.path.realpath(__file__))
print(BASE_PATH)


##### Survey Analysis ####
from NearContactStudy.NearContact20Survey.createShapesMatlab import ShapeSTLGeneratorPython


#### Setting Parametrization Constant #####
HAND_PARAM = 32.0 #maximum finger span
PARAMETERIZE = True #general keyword to know if calculations and stuff should be done with paramaterized version or with absolute size

from NearContactStudy.InterpolateGrasps.Visualizers import Vis, GenVis, ObjectVis, ObjectGenericVis, HandVis, AddGroundPlane, ArmVis
from NearContactStudy.InterpolateGrasps.Colors import ColorsDict, bcolors
# from InterpolateGrasps.stl_generator import stl_generator
# from InterpolateGrasps.stlwriter import ASCII_STL_Writer, Binary_STL_Writer
from NearContactStudy.InterpolateGrasps.obj_dict import grasp_obj_dict, obj_centroid_dict


##### Qualtrics Data Processing #####
from NearContactStudy.NearContact20Survey.QualtricsDataProcessing.KeyMapper import KeyMapper



#### Qualtrics Data Processing ####
from NearContactStudy.NearContact20Survey.QualtricsDataProcessing.buildPolytopeFromResponses import BuildPolytope, PolytopeParametric, PolytopeNonparametric
from NearContactStudy.NearContact20Survey.QualtricsDataProcessing.DiscreteAnalysis import DiscreteAnalysis
from NearContactStudy.NearContact20Survey.QualtricsDataProcessing.ContinuousAnalysis import ContinuousAnalysis
from NearContactStudy.NearContact20Survey.QualtricsDataProcessing.Parametric import Parametric
from NearContactStudy.NearContact20Survey.QualtricsDataProcessing.Nonparametric import Nonparametric

##### Qualtrics Survey Parsing #####
from NearContactStudy.NearContact20Survey.QualtricsGeneration.QualtricsGen.SurveyParser import SurveyParser, multi_choice,  blockelement, flowelement, randomizerelement, LM_temp

##### Qualtrics Data Processing #####
from NearContactStudy.NearContact20Survey.QualtricsDataProcessing.DataProcessing import csvReader, dataResults, removeUnfinishedRows, removeUnnecessaryColumns
from NearContactStudy.NearContact20Survey.QualtricsDataProcessing.SurveyResultsParser import SurveyResultsParser

##### Shape Image Generator #####
from NearContactStudy.ShapeImageGenerator.HandCenteredCSV import HandCenteredCSV
from NearContactStudy.ShapeImageGenerator.ShapeImageGeneratorTest import ShapeImageGenerator
from NearContactStudy.ShapeImageGenerator.ShapeImageManipulator import ShapeImageManipulator


##### General Helpful Constants #####
JOINT_ANGLES_NAMES = ['J1', 'J2', 'J3', 'J4', 'J5', 'J6', 'J7', 'Unknown', 'Unknown',
					'FINGER1-ROTATION','FINGER1-BASE','FINGER1-TIP',
					'FINGER2-ROTATION','FINGER2-BASE','FINGER2-TIP', 
					'FINGER3-ROTATION','FINGER3-BASE','FINGER3-TIP']