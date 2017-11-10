import matlab.engine
import pdb
import csv
import numpy as np

from NearContactStudy import Vis, HandVis, ObjectGenericVis, ArmVis





class JointAngleChecker():
	def __init__(self):
		self.V = Vis()
		self.H = HandVis(self.V)
		self.O = ObjectGenericVis(self.V)
		self.H.loadHand()

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

	def loadJAFromFrame(self, fn, frame):
		#loads a specific frame from an extracted set
		with open(fn, 'rb') as csvfile:
			reader = csv.reader(csvfile)
			next(reader) #deal with header row
			for row in reader:
				if int(float(row[0])) == frame:
					JA = np.array(row[1:]).astype(float)
					pdb.set_trace()
					self.H.setJointAngles(JA[-10:])
					return JA


if __name__ == '__main__':
	JAC = JointAngleChecker()
	fn = '/media/kotharia/RGWdata/BagFiles/NRI Data Collection 2/large_part0_2017-10-06-11-52-26/JointAngles.csv'
	frame = 269
	JAC.loadJAFromFrame(fn, frame)
	pdb.set_trace()