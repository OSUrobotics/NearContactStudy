import sys, os, copy, csv, re
from openravepy import *
import pdb
curdir = os.path.dirname(os.path.realpath(__file__))
classdir = curdir +'/../InterpolateGrasps/'
classdir2 = curdir + '/../ShapeImageGenerator/'
sys.path.insert(0, classdir) # path to helper classes
from Visualizers import Vis, GenVis, ArmVis, ObjectGenericVis, AddGroundPlane
sys.path.insert(0, classdir2) # path to helper classes
from ShapeImageGeneratorTest import ShapeImageGenerator
import numpy as np 
import time
import matplotlib.pyplot as plt
import subprocess


class cagingTest(object):
	def __init__(self):
		i = 1
		self.SIG = ShapeImageGenerator()
		# getting an example grasp -- could be anything. these were already present, so i am using them
		self.SIG.readParameterFile(curdir +'/../ShapeImageGenerator' + '/HandCenteredImageGeneratorParameters.csv')
		param = self.SIG.getParameterFromFeatures('cube', 9, 9, 9, 'h', 'equidistant', 'side', 'up', '0')
		self.SIG.Hand.remove()

		self.SIG.vis.viewer.SetSize(640, 480)
		self.arm = ArmVis(self.SIG.vis)
		self.arm.loadArm()
		move_to_zero = np.array([[ 0.   , -1.   ,  0.   ,  0.089],
						       [ 0.   ,  0.   , -1.   ,  0.001],
						       [ 1.   ,  0.   ,  0.   , -0.379],
						       [ 0.   ,  0.   ,  0.   ,  1.   ]])
		self.arm.obj.SetTransform(move_to_zero)
		self.SIG.loadSceneFromParameters(param, False)
		self.gmodel = databases.grasping.GraspingModel(self.arm.obj,self.SIG.Obj.obj)
		pdb.set_trace()
		optparser = self.gmodel.CreateOptionParser()
		optparser.add_option('--preshapes %s' %param['Joint Angles'])
		optparser.add_option('--manipulatordirections %s' %[0, 0, 1])

		self.gmodel.autogenerate(optparser)
		



if __name__ == '__main__':
	ct = cagingTest()
