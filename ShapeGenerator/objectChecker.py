import numpy as np
from openravepy import *
import sys, os, pdb

curdir = os.path.dirname(os.path.realpath(__file__))
classdir = curdir +'/../InterpolateGrasps/'
sys.path.insert(0, classdir) # path to helper classes
from Visualizers import Vis, HandVis, ObjectGenericVis




# check if the features of an object is good relative to hand



class ObjChecker(object):
	def __init__(self):
		self.i = 1
		self.vis = Vis()
		self.obj = ObjectGenericVis(self.vis)
		self.hand = HandVis(self.vis)
		self.hand.loadHand()

	def loadObject(self):
		result = self.obj.loadObject('handle', 27, 30, 12, 45)
		return result


if __name__ == '__main__':
	OC = ObjChecker()
	OC.loadObject()
	OC.obj.changeColor(alpha = 0.5)
	OC.vis.drawPoints([0,0,0])
	pdb.set_trace()


