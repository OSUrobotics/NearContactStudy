import sys, os, copy, csv, re, pdb, time, subprocess
import numpy as np 
import matplotlib.pyplot as plt
from PIL import Image
import cv2
from openravepy import *
curdir = os.path.dirname(os.path.realpath(__file__))
classdir = curdir +'/../InterpolateGrasps/'
sys.path.insert(0, classdir) # path to helper classes
from Visualizers import Vis, GenVis, HandVis, ObjectGenericVis
imagegendir = curdir +'/../ShapeImageGenerator/' # path to image, stl generator classes
sys.path.insert(0, imagegendir)
from ShapeImageGeneratorTest import ShapeImageGenerator



class TrainingVideo(object):
	def __init__(self):
		self.vis = Vis()
		self.Hand = HandVis(self.vis)
		self.Hand.loadHand()
		self.Obj = ObjectGenericVis(self.vis)
		self.demoObj = list()
		self.frameCount = 0
		self.start_offset = 0

	def recordFrame(self):
		fn = 'Image%04d.png' %self.frameCount
		self.vis.takeImage(fn, delay = False)
		self.frameCount += 1


	def handRecord(self, positions, dim):
		if dim == 'z':
			idx = 2
		elif dim == 'x':
			idx = 0
		elif dim == 'y':
			idx = 1
		else:
			print('Not a valid Dimension')
			return
		T = copy.deepcopy(self.T_start)
		for i in positions:
			T[idx,3] = i + self.T_start[idx,3]
			self.Hand.obj.SetTransform(T)
			self.recordFrame()
			

	def stationaryRecord(self, frames):
		for i in range(int(frames)):
			self.recordFrame()

	def createVideo(self, fn): # creates a video from images recorded in previous section
		#there is a built in openrave function which would be much better, but doesn't work on all hardware
		
		# uses PIL and cv2. opencv is a pain to setup, so may not be worth the hassle
		if os.path.splitext(fn)[1] != '.avi':
			print("Did not save Video: Invalid File Name")
			return
		initImage = Image.open('Image0001.png')
		height, width, layers = np.array(initImage).shape
		fourcc = cv2.VideoWriter_fourcc(*'XVID')
		video = cv2.VideoWriter(fn, fourcc, 24, (width, height))
		Files = os.listdir(curdir)
		for file in np.sort(Files):
			if os.path.splitext(file)[1] == '.png':
				image = Image.open(file)
				video.write(cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR))
		video.release()


		# native linux method -- most likely to work
		#subprocess.call(["avconv", "-f", "image2", "-i", "Image%04d.png", "-r", "5", "-s", "800x600", fn+".avi"])

	def removeImages(self): # remove image files that were created
		Files = os.listdir(curdir)
		for file in Files:
			if os.path.splitext(file)[1] == '.png':
				os.remove(file)

	def VLCPlay(self, fn):
		subprocess.call(["vlc", fn])

	def Video1(self):
		# setup
		self.Obj.loadObject('cube',36,18,3,None)  # TODO: Object with larger extent!
		self.Obj.changeColor('greenI')
		self.Hand.changeColor('blueI')
		extent_offset = -3.0/100 # offset by thickness of object
		palm_offset = -0.075 #offset so palm is at 0,0,0
		clearance_offset = -1.0/100 # offset to have clearance between palm and object
		self.start_offset = extent_offset + palm_offset + clearance_offset
		self.Hand.localTranslation(np.array([0, 0, self.start_offset]))
		rot = matrixFromAxisAngle([0,0, np.pi/2])
		self.Hand.localRotation(rot) # rotate hand to put stationary finger on one side of object
		self.T_start = self.Hand.obj.GetTransform() # get starting transform so everything can be done relative to this
		JA = np.array([0, 0, 0.2, 0.8, 0.0, 0.2, 0.8, 0.0, 0.8, 0.0]) # position fingers such that hand can move in x, y, and z without hitting object
		self.Hand.setJointAngles(JA)
		dist_range_min = -0.1
		dist_range_max = 0.1
		frame_rate = 20/0.1 # frames/cm
		# TODO: **************
		# fix camera angle so it is easier to see
		self.vis.setCamera(60,3*np.pi/4,-np.pi/4-0.1)
		# movement in z direction
		d_max = 0.01
		d_min = -0.1
		frames = abs(d_max - d_min) * frame_rate
		self.handRecord(np.linspace(d_max,d_min,frames), 'z')

		# camera rotation between each scene?
		# pdb.set_trace()


		# movement in x direction
		d_max = 0.02
		d_min = -0.03
		frames = abs(d_max - d_min) * frame_rate
		self.handRecord(np.linspace(d_max,d_min,frames), 'x')
		self.stationaryRecord(10)
		# movement in y direction
		d_max = 0.2
		d_min = -0.2
		frames = abs(d_max - d_min) * frame_rate
		self.handRecord(np.linspace(d_max,d_min,frames), 'y')


if __name__ == '__main__':
	TV = TrainingVideo()
	TV.Video1()
	TV.createVideo('Video1.avi')
	TV.VLCPlay('Video1.avi')
	TV.removeImages()
	pdb.set_trace()