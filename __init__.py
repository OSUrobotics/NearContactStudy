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


# Visualization Stuff
from NearContactStudy.InterpolateGrasps.Visualizers import Vis, GenVis, ObjectVis, ObjectGenericVis, HandVis, AddGroundPlane, ArmVis, ArmVis_OR
from NearContactStudy.InterpolateGrasps.Colors import ColorsDict, bcolors
from NearContactStudy.InterpolateGrasps.stlwriter import ASCII_STL_Writer, Binary_STL_Writer
from NearContactStudy.InterpolateGrasps.obj_dict import grasp_obj_dict, obj_centroid_dict

##### Extracting Data from Saurabh's Study #####
from NearContactStudy.InterpolateGrasps.ParseGraspData import ParseGraspData


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

#### Generating Noisy Grasps ####
from NearContactStudy.NoiseyMovements.noisy_finger_stl_gen import noiseJoints

#### Extracting Data from Bag Files
from NearContactStudy.VideoProcessing.ObjectEstimation import BagReader


##### General Helpful Constants #####
JOINT_ANGLES_NAMES = ['J1', 'J2', 'J3', 'J4', 'J5', 'J6', 'J7', 'Unknown', 'Unknown',
					'FINGER1-ROTATION','FINGER1-BASE','FINGER1-TIP',
					'FINGER2-ROTATION','FINGER2-BASE','FINGER2-TIP', 
										'FINGER3-BASE','FINGER3-TIP']

# indices of robot JA to build OpenRAVE JA
ROBOT_TO_OR_MAPPING = [0, 1, 2, 3, 4, 5, 6, -1, -1, 10, 7, 11, 10, 8, 12, 9, 13]