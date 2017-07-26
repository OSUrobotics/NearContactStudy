
import sys, os, copy, csv, re, pdb, time, subprocess
import numpy as np 
import math

from openravepy import *
curdir = os.path.dirname(os.path.realpath(__file__))
classdir = curdir +'/../Interpolate Grasps/'
sys.path.insert(0, classdir) # path to helper classes
from Visualizers import Vis, GenVis, HandVis, ObjectGenericVis, AddGroundPlane


class HandView(object):
	def __init__(self, handColor, objColor):
		self.setDefaults(handColor, objColor)
		self.setView()

	def setDefaults(self, handColor, objColor):
		self.fingerOpeningDict = {1:False, 2:False, 3:False}
		self.handMovingForward = {"X": False, "Y": False, "Z":False}
		self.ignoreContact = {"1": True	, "2": True, "3": True, "Palm":True}
		self.grasps = {}
		self.grasps['TWOFER_ANGLES'] = np.array([0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0])
		self.grasps['CLAW_ANGLES'] = np.array([0,0,np.pi/4,0,0,np.pi/4,0,0,0,0])
		self.grasps['PINCH_ANGLES'] = np.array([0,0,np.pi/2,0,0,np.pi/2,0,0,0,0])
		self.grasps['CUP_ANGLES'] = np.array([0,0,np.pi,0,0,np.pi,0,0,0,0])
		self.distJointAngles = {"min":0, "max":.837}
		self.medJointAngles = {"min":0, "max":2.44}
		self.createContactDict()
		self.handColor = handColor
		self.objColor = objColor
	
	def createContactDict(self):
		self.contactLinks = {}
		linkBase = "wam/bhand/"
		self.contactLinks[linkBase+ "bhand_palm_link"] = False
		for i in range(1,4):
			for link in ["dist_link", "med_link", "prox_link"]:
				self.contactLinks[linkBase+"finger_"+str(i)+"/"+link] = False

	def setView(self):
		self.vis = Vis()
		self.vis.setCamera(60,7*np.pi/8,0)
		self.ground = AddGroundPlane(self.vis)
		self.ground.createGroundPlane(.175)

	def addHand(self, grasp):
		self.Hand = HandVis(self.vis)
		self.Hand.loadHand()
		self.Hand.changeColor(self.handColor)
		self.setGrasp(grasp)
		self.setWristRotation('Z',0)

	def addObj(self, objParameters):
		self.Obj = ObjectGenericVis(self.vis)
		self.setHandTranslation('Z',-.075 - (float(objParameters["e"])/100) - .02)
		self.setObject(objParameters)
		self.Obj.changeColor(self.objColor)
	
	def setIgnoreContact(self, value):
		for link in self.ignoreContact:
			self.ignoreContact[link] = value
	def setIgnoreFingerContact(self, value):
		for link in self.ignoreContact:
			if link != "Palm":
				self.ignoreContact[link] = True
	def changeTranslationDirection(self, dimension, newOffset):
		return (newOffset >= 0) ^ (self.handMovingForward[dimension])

	def setHandTranslation(self, dimension, newOffset):
		direction = newOffset/abs(newOffset)
		startInc = .005*direction
		for i in range(1, int(math.ceil((newOffset+startInc)/startInc))):
			if dimension == 'X':
				self.Hand.localTranslation(np.array([startInc, 0, 0]))
			elif dimension == 'Y':
				self.Hand.localTranslation(np.array([0, startInc, 0]))
			elif dimension == 'Z':
				self.Hand.localTranslation(np.array([0,0,startInc]))
			pC = self.palmContact()
			if self.ignoreContact["Palm"]:
				self.ignoreContact["Palm"] = pC
				continue
			else:
				if pC:
					self.setHandTranslation(dimension, -startInc)
					return (i-1)*startInc
		return newOffset

	def setWristRotation(self, direction, rotation):
		angle = float(rotation)/16
		if direction == 'X':
			rot = matrixFromAxisAngle([angle,0,0])
		elif direction == 'Y':
			rot = matrixFromAxisAngle([0,angle,0])
		elif direction == 'Z':
			rot = matrixFromAxisAngle([0,0,angle])
		self.Hand.localRotation(rot)
		self.setIgnoreContact(True)

	def setObjRotation(self, direction, rotation):
		angle = float(rotation)/16
		if direction == 'X':
			rot = matrixFromAxisAngle([angle, 0,0])
		elif direction == 'Y':
			rot = matrixFromAxisAngle([0,angle,0])
		elif direction == 'Z':
			rot = matrixFromAxisAngle([0,0,angle])
		self.Obj.localRotation(rot)
		self.setIgnoreContact(True)

	def setObject(self, newObj):
		#newObj = {"shape":, "h":, "w":, "e":, "a":}
		if newObj["shape"] == 'cone':
			self.Obj.loadObject(newObj["shape"],int(newObj["h"]),int(newObj["w"]),int(newObj["e"]),int(newObj["a"]))
		else:
			self.Obj.loadObject(newObj["shape"],int(newObj["h"]),int(newObj["w"]),int(newObj["e"]),None)
		self.Obj.changeColor(self.objColor)
		self.setIgnoreContact(True)

	def setGrasp(self, newGrasp):
		if newGrasp == "The Two-fer":
			self.grasp = self.grasps["TWOFER_ANGLES"]
		elif newGrasp == "The Claw":
			self.grasp = self.grasps["CLAW_ANGLES"]
		elif newGrasp == "The Pinch":
			self.grasp = self.grasps["PINCH_ANGLES"]
		elif newGrasp == "The Cup":
			self.grasp = self.grasps["CUP_ANGLES"]
		self.showGrasp()
		self.setIgnoreFingerContact(True)
		return self.grasp

	def getMedJointAngle(self, percentClosed):
		return ((self.medJointAngles["max"]-self.medJointAngles["min"])*percentClosed)+self.medJointAngles["min"]
	def getDistJointAngle(self, percentClosed):
		return ((self.distJointAngles["max"]-self.distJointAngles["min"])*percentClosed)+self.distJointAngles["min"]
	def fingerOpening(self, finger, percentClosed):
		if finger == 1:
			return self.getMedJointAngle(percentClosed) < self.grasp[3]
		elif finger == 2:
			return self.getMedJointAngle(percentClosed) < self.grasp[6]
		elif finger == 3:
			return self.getMedJointAngle(percentClosed) < self.grasp[8]
	def anyFingerContact(self):
		for contact in self.Hand.getContact(self.Obj.boj).keys():
			if contact.find("finger_") != -1 and contact[-9:] != "prox_link":
				return True
		return False		

	def fingerContact(self, finger):
		for contact in self.Hand.getContact(self.Obj.obj).keys():
			if contact.find("finger_"+str(finger)) != -1 and contact[-9:] != "prox_link":
				return True
		return False

	def fullFingerContact(self, finger):
		someContact = False
		for contact in self.Hand.getContact(self.Obj.obj).keys():
			if contact.find("finger_"+str(finger)) != -1 and contact[-9:] == "dist_link":
				return 't'
			elif contact.find("finger_"+str(finger)) != -1 and contact[-8:] == "med_link":
				someContact = True
		if someContact:
			return 's'
		else:
			return 'f'

	def palmContact(self):
		for contact in self.Hand.getContact(self.Obj.obj).keys():
			if contact[-9:] == "palm_link":
				return True
		return False

	def fingerChangingDirection(self, finger, percentClosed):
		return self.fingerOpening(finger, percentClosed) != self.fingerOpeningDict[finger]
	
	def changeFingerPosition(self, finger, percentClosed):
		contact = self.fullFingerContact(finger)
		if self.ignoreContact[str(finger)] or self.fingerChangingDirection(finger, percentClosed) or contact != 't':
			self.fingerOpeningDict[finger] = self.fingerOpening(finger, percentClosed)
			if finger == 1:
				if contact == 'f' or self.fingerOpeningDict[finger]:
					self.grasp[3] = self.getMedJointAngle(percentClosed)
				self.grasp[4] = self.getDistJointAngle(percentClosed)
			elif finger == 2:
				if contact == 'f' or self.fingerOpeningDict[finger]:
					self.grasp[6] = self.getMedJointAngle(percentClosed)
				self.grasp[7] = self.getDistJointAngle(percentClosed)
			elif finger ==3:
				if contact == 'f' or self.fingerOpeningDict[finger]:
					self.grasp[8] = self.getMedJointAngle(percentClosed)
				self.grasp[9] = self.getDistJointAngle(percentClosed)
			self.showGrasp()
			if self.ignoreContact[str(finger)]:
				self.ignoreContact[str(finger)] = self.fingerContact(finger)
			print self.grasp
			return True
		return False
	
	def getFingerPositionPercent(self, finger):
		if finger == 1:
			return (self.grasp[3]-self.medJointAngles["min"])/(self.medJointAngles["max"]-self.medJointAngles["min"])
		elif finger == 2:
			return (self.grasp[6]-self.medJointAngles["min"])/(self.medJointAngles["max"]-self.medJointAngles["min"])
		elif finger == 3:
			return (self.grasp[8]-self.medJointAngles["min"])/(self.medJointAngles["max"]-self.medJointAngles["min"])

	def showGrasp (self):
		self.Hand.setJointAngles(self.grasp)