import sys, os, copy, csv, re, pdb, time, subprocess
from openravepy import *
curdir = os.path.dirname(os.path.realpath(__file__))
classdir = curdir +'/../Interpolate Grasps/'
sys.path.insert(0, classdir) # path to helper classes
from Visualizers import Vis, GenVis, HandVis, ObjectGenericVis, AddGroundPlane
imagegendir = curdir +'/../ShapeImageGenerator/' # path to image, stl generator classes
sys.path.insert(0, imagegendir)
from ShapeImageGeneratorTest import ShapeImageGenerator
import numpy as np 
import matplotlib.pyplot as plt
from PIL import Image
import cv2



class TrainingVideo(object):
	def __init__(self):
		self.vis = Vis()
		self.Hand = HandVis(self.vis)
		self.Hand.loadHand()
		self.Obj = ObjectGenericVis(self.vis)
		self.GP = AddGroundPlane(self.vis)
		self.demoObj = list()
		self.frameCount = 0
		self.start_offset = 0

	def recordFrame(self):
		fn = 'Image%04d.png' %self.frameCount
		self.vis.takeImage(fn, delay = False)
		self.frameCount += 1

	# Kadon Engle - last edited 07/14/17
	def fingerRecord(self, oldJA, newJA): # Records a frame for multiple join angles between the starting array (OldJA) amd the ending array (newJA)
		try:
			frame_rate = 20 # An arbitrary base line for the frames in each hand movement
			frames = int(max(abs(newJA - oldJA)) * frame_rate)
			Angles = []
			self.Hand.setJointAngles(oldJA)
			if len(self.Hand.getContactPoints()) > 0:
				self.Hand.setJointAngles(iP[-1])
			for i in range(frames):
				Angles.append(list())
			for i in range(len(oldJA)):
				current = np.linspace(oldJA[i], newJA[i], frames)
				for k in range(frames):
					Angles[k].append(current[k])
			for n, i in enumerate(Angles): #More work is necessary on detecting finger collision to stop the fingers
				self.Hand.setJointAngles(np.array(i))
				if len(self.Hand.getContactPoints()) > 0:
					self.Hand.setJointAngles(Angles[n-1])
					return Angles[n-1]
				self.recordFrame()
			return Angles[n-1]

		except:
			print "Invalid Joint Angle"

	# Kadon Engle - last edited 07/14/17
	def handRecord(self, x, y, z): # Records frames as hand moves in x, y, and/or z direction
		self.T_current = self.Hand.obj.GetTransform()
		T = copy.deepcopy(self.T_current)
		xyz = [x, y, z]
		frames = 20 # Arbitrary value, needs to be changed so that when x, y, or z moves shorter distances, it records less frames. Should be changed so that it records less frames for shorter movements and more frames for longer movements.
		for idx, i in enumerate(xyz):
			if abs(i - self.T_current[idx,3]) > 0.1e-5:
				V = np.linspace(self.T_current[idx,3], i, frames)
				for n in V:
					T[idx,3] = n
					self.Hand.obj.SetTransform(T)
					self.recordFrame()

	def stationaryRecord(self, frames):
		for i in range(int(frames)):
			self.recordFrame()

	def createVideo(self, fn): # creates a video from images recorded in previous section
		# there is a built in openrave function which would be much better, but doesn't work on all hardware
		
		# uses PIL and cv2. opencv is a pain to setup, so may not be worth the hassle
		try:
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
		except:
			print 'Something went wrong. Maybe you didn\'t record any images'

		# native linux method -- most likely to work
		# subprocess.call(["avconv", "-f", "image2", "-i", "Image%04d.png", "-r", "5", "-s", "800x600", fn+".avi"])

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
		self.Obj.changeColor('purpleI')
		self.Hand.changeColor('mustard')
		self.GP.createGroundPlane(0.175)
		extent_offset = -3.0/100 # offset by thickness of object
		palm_offset = -0.075 #offset so palm is at 0,0,0
		clearance_offset = -1.0/100 # offset to have clearance between palm and object
		self.start_offset = extent_offset + palm_offset + clearance_offset
		self.Hand.localTranslation(np.array([0, 0, self.start_offset]))
		rot = matrixFromAxisAngle([0,0, np.pi/2])
		self.Hand.localRotation(rot) # rotate hand to put stationary finger on one side of object
		self.T_start = self.Hand.obj.GetTransform() # get starting transform so everything can be done relative to this
		oHand = np.array([0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]) # position fingers such that hand can move in x, y, and z without hitting object
		cHand = np.array([0, 0, 0.0, 1.3, 0.4, 0.0, 1.3, 0.4, 1.3, 0.4]) # position fingers such that the hand will be closed around the object without hititng it
		self.Hand.setJointAngles(oHand)
		dist_range_min = -0.1
		dist_range_max = 0.1
		frame_rate = 20/0.1 # frames/cm
		# Different arbitrary camera angles for needed viewpoints
		# self.vis.setCamera(60,3*np.pi/4,-np.pi/4-0.1)
		# self.vis.setCamera(60, np.pi, -np.pi/2) # top view
		# self.vis.setCamera(60, -2.25, -np.pi/2.10)
		self.vis.setCamera(60, -2.25, -0.75) # Numbers are completely arbitrary, gives a good view of object and hand.

		

		# self.handRecord(0,0,-0.15)
		# cHand = self.fingerRecord(oHand, cHand)
		# self.fingerRecord(cHand, oHand)
		# self.handRecord(0,0,-0.115)
		# cHand = np.array([0, 0, 0.0, 1.3, 0.4, 0.0, 1.3, 0.4, 1.3, 0.4])
		# cHand = self.fingerRecord(oHand, cHand)
		# self.fingerRecord(cHand, oHand)
		# pdb.set_trace()




		# Moves the hand and closes the fingers in a suitable manner for this video
		# self.handRecord(0, 0, -0.15)
		# cHand = self.fingerRecord(oHand, cHand)
		# self.stationaryRecord(5)
		# self.fingerRecord(cHand, oHand)
		# self.handRecord(0, -0.13, -0.15)
		# self.handRecord(0, -0.13, -0.115)
		# cHand = np.array([0, 0, 0.0, 1.3, 0.4, 0.0, 1.3, 0.4, 1.3, 0.4])
		# cHand = self.fingerRecord(oHand, cHand)
		# self.stationaryRecord(5)
		# self.fingerRecord(cHand, oHand)
		# self.handRecord(0, -0.13, -0.15)
		# self.handRecord(0, 0.1, -0.15)
		# self.handRecord(0, 0.1, -0.115)
		# cHand = np.array([0, 0, 0.0, 1.3, 0.4, 0.0, 1.3, 0.4, 1.3, 0.4])
		# cHand = self.fingerRecord(oHand, cHand)
		# self.stationaryRecord(5)
		# self.fingerRecord(cHand, oHand)
		# self.handRecord(0, 0.1, -0.15)
		# self.handRecord(0, 0, -0.15)
		# self.handRecord(-0.05, 0, -0.15)
		# self.handRecord(-0.05, 0, -0.115)
		# self.stationaryRecord(5)
		# self.handRecord(-0.05, 0, -0.15)
		# self.handRecord(0.05, 0, -0.15)
		# self.handRecord(0.05, 0, -0.115)
		# self.stationaryRecord(5)
		# self.handRecord(0.05, 0, -0.15)
		# self.handRecord(0, 0, -0.15)






if __name__ == '__main__':
	TV = TrainingVideo()
	TV.Video1()
	TV.createVideo('Video1.avi')
	TV.removeImages()
	TV.VLCPlay('Video1.avi')
	pdb.set_trace()