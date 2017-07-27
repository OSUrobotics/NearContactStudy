import numpy as np
from openravepy import *
import sys, os, pdb
# print(sys.version)
# sys.path = sys.path[1:]
# sys.path = [''] + sys.path
# print(sys.path)
# pdb.set_trace()
# import matlab.engine
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

	def loadObject(self, obj_type, h, w, e, a = None):
		result = self.obj.loadObject(obj_type, h, w, e, a)
		return result

	def createObject(self, obj_type, resolution, fnsave, h, w, e, a = None):
		pdb.set_trace()
		eng = matlab.engine.start_matlab()
		if a is not None:
			if obj_type == 'vase':
				a  = a/100.0

			eng.ShapeSTLGenerator(obj_type, resolution, fnsave, h/100.0, w/100.0, e/100.0, a, nargout=0)
		else:
			eng.ShapeSTLGenerator(obj_type, resolution, fnsave, h, w, e,nargout=0)
		self.obj.loadObject(obj_type, h, w, e, a)
		self.obj.changeColor(alpha = 0.5)
		self.vis.drawPoints([0,0,0])
		print("Object Created: %s" %result)


if __name__ == '__main__':
	OC = ObjChecker()
	# OC.loadObject()
	# OC.obj.changeColor(alpha = 0.5)
	# OC.vis.drawPoints([0,0,0])
	# OC.createObject('cube', 10, 'cube_sizetest',12.0, 12.0, 12.0)
	pdb.set_trace()


