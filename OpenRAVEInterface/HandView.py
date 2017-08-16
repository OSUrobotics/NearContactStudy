import sys, os, copy, csv, re, pdb, time, subprocess
import numpy as np 
import math

from openravepy import *
curdir = os.path.dirname(os.path.realpath(__file__))
classdir = curdir +'/../InterpolateGrasps/'
sys.path.insert(0, classdir) # path to helper classes
from Visualizers import Vis, GenVis, HandVis, ObjectGenericVis, AddGroundPlane

"""
This sets up the simulation view that is paired with the PreShapeChooser GUI
Run starting from PreShapeChooser.py so this should be in the same folder as PreShapeChooser.py
Visualizers should be in the folder ../InterpolateGrasps/
"""
class HandView(object):
	def __init__(self, handColor, objColor, grasps):
		self.setDefaults(handColor, objColor)
		self.setView()
		self.grasps = grasps

	def setDefaults(self, handColor, objColor):
		#handColor and objColor are colors from Colors.py
		#sets any start hardcoded values
		self.fingerOpeningDict = {1:False, 2:False, 3:False}
		self.handMovingForward = {"X": False, "Y": False, "Z":False}
		self.ignoreContact = {"1": True	, "2": True, "3": True, "Palm":True}
		self.distJointAngles = {"min":0, "max":.837}
		self.medJointAngles = {"min":0, "max":2.44}
		self.handColor = handColor
		self.objColor = objColor
	
	def addGroundPlane(self):
		#adds a ground plane to the scene
		self.ground = AddGroundPlane(self.vis)
		self.ground.createGroundPlane(.175)

	def setView(self):
		#creates a scene with a ground plane
		self.vis = Vis()
		self.vis.setCamera(60,7*np.pi/8,0)
		self.addGroundPlane()

	def addHand(self, grasp):
		#grasp is either "The Two-fer", "The Claw", "The Pinch", "The Cup"
		#adds the hand to the scene and sets the grasp and wrist rotation
		self.Hand = HandVis(self.vis)
		self.Hand.loadHand()
		self.Hand.changeColor(self.handColor)
		self.setGrasp(grasp)
		self.setWristRotation('Z',0)

	def addObject(self, objParameters):
		#objParameters = {"shape":,"h":,"w":,"e":,"a":}
		#adds an object to the scene based on the object parameters
		#shifts the hand accordingly
		self.Obj = ObjectGenericVis(self.vis)
		self.setHandTranslation('Z',-.075 - (float(objParameters["e"])/100) - .02)
		self.setObject(objParameters)
		self.Obj.changeColor(self.objColor)
	
	def setIgnoreAllContact(self, value):
		#value is either True or False
		#sets all fingers and palm to ignore or not ignore contact with the object
		for link in self.ignoreContact:
			self.ignoreContact[link] = value

	def setIgnoreFingerContact(self, value):
		#value is either True or False
		#sets all fingers to ignore or not ignore contact with the object
		for link in self.ignoreContact:
			if link != "Palm":
				self.ignoreContact[link] = value

	def totalNumberofTranslationIncrements(self,newOffset, increment):
		#newOffset is a float and increment is a float
		#returns the total number of iterations of the increment to reach the newOffset
		return int(math.ceil((newOffset+increment)/increment))

	def translateHand(self, dimension, amount):
		#direction should be either 'X', 'Y', or 'Z' ;;; amount is a float
		#shifts the hand in relation to the object in the direction of the dimension by the amount
		if dimension == 'X':
			self.Hand.localTranslation(np.array([amount, 0, 0]))
		elif dimension == 'Y':
			self.Hand.localTranslation(np.array([0, amount, 0]))
		elif dimension == 'Z':
			self.Hand.localTranslation(np.array([0,0,amount]))

	def tryTranslateHandByOneIncrement(self, dimension, increment):
		#direction should be either 'X', 'Y', or 'Z' ;;; increment is a float
		#shifts the hand in the direction of dimension by the increment
		#if hand comes into contact with the object and contact is not ignored,
		#hand backs up to where it started and returns False, otherwise returns True
		#if contact is ignored, but the palm is not in contact, it no longer ignores contact
		self.translateHand(dimension, increment)
		pC = self.palmContact()
		if self.ignoreContact["Palm"]:
			self.ignoreContact["Palm"] = pC
			return True
		else:
			if pC:
				self.setHandTranslation(dimension, -increment)
				return False
			else:
				return True

	def setHandTranslation(self, dimension, newOffset):
		#shifts the hand in the direction of dimension by the newOffset
		#if shifting the hand causes a collision between the palm and object,
		#hand is shifted in the opposite direction by one increment so it is no longer touching
		#returns the amount by which the hand was shifted
		direction = newOffset/abs(newOffset)
		increment = .005*direction
		for i in range(1, self.totalNumberofTranslationIncrements(newOffset, increment)):
			if not self.tryTranslateHandByOneIncrement(dimension, increment):
				return (i-1)*increment
		return newOffset

	def setWristRotation(self, direction, rotation):
		#direction should be either 'X', 'Y', or 'Z' ;;; rotation is a float
		#rotates the hand's wrist in the direction specified
		#sets ignore contact for every finger/palm
		if direction == 'X':
			rot = matrixFromAxisAngle([rotation,0,0])
		elif direction == 'Y':
			rot = matrixFromAxisAngle([0,rotation,0])
		elif direction == 'Z':
			rot = matrixFromAxisAngle([0,0,rotation])
		self.Hand.localRotation(rot)
		self.setIgnoreAllContact(True)

	def setObjRotation(self, direction, rotation):
		#direction should be either 'X', 'Y', or 'Z' ;;; rotation is a float
		#rotates the object in the direction specified
		#sets ignore contact for every finger/palm
		if direction == 'X':
			rot = matrixFromAxisAngle([rotation, 0,0])
		elif direction == 'Y':
			rot = matrixFromAxisAngle([0,rotation,0])
		elif direction == 'Z':
			rot = matrixFromAxisAngle([0,0,rotation])
		self.Obj.localRotation(rot)
		self.setIgnoreAllContact(True)

	def setObject(self, newObj):
		#newObj is a dict {"shape":, "h":, "w":, "e":, "a":}
		#assumes an object has already been added with addObject
		#sets ignore contact for every finger/palm
		if newObj["shape"] == 'cone':
			self.Obj.loadObject(newObj["shape"],int(newObj["h"]),int(newObj["w"]),int(newObj["e"]),int(newObj["a"]))
		else:
			self.Obj.loadObject(newObj["shape"],int(newObj["h"]),int(newObj["w"]),int(newObj["e"]),None)
		self.Obj.changeColor(self.objColor)
		self.setIgnoreAllContact(True)

	def setGrasp(self, newGrasp):
		#newGrasp is one of the keys in self.grasps
		#sets the grasp so that it goes to a certain pregrasp
		#sets ignore contact for every finger/palm
		#returns the new grasp array so the finger sliders can be reset
		self.grasp = self.grasps[newGrasp]
		self.showGrasp()
		self.setIgnoreFingerContact(True)
		return self.grasp

	def getMedJointAngle(self, percentClosed):
		#percentClosed is a float 0<>100
		#returns the grasp array value for a med joint given the percent it is closed
		return ((self.medJointAngles["max"]-self.medJointAngles["min"])*percentClosed)+self.medJointAngles["min"]
	def getDistJointAngle(self, percentClosed):
		#percentClosed is a float 0<>100
		#returns the grasp array value for a the dist joint given the percent it is closed
		return ((self.distJointAngles["max"]-self.distJointAngles["min"])*percentClosed)+self.distJointAngles["min"]
	def fingerOpening(self, finger, percentClosed):
		#finger is either 1, 2, or 3
		#percentClosed is a float 0<>100
		#returns a bool
		if finger == 1:
			return self.getMedJointAngle(percentClosed) < self.grasp[3]
		elif finger == 2:
			return self.getMedJointAngle(percentClosed) < self.grasp[6]
		elif finger == 3:
			return self.getMedJointAngle(percentClosed) < self.grasp[8]
	
	def anyFingerContact(self):
		#returns whether any finger is in contact with the object
		for contact in self.Hand.getContact(self.Obj.boj).keys():
			if contact.find("finger_") != -1 and contact[-9:] != "prox_link":
				return True
		return False		

	def fingerContact(self, finger):
		#finger should be either 1, 2, or 3
		#returns whether the provided finger is in contact with the object
		for contact in self.Hand.getContact(self.Obj.obj).keys():
			if contact.find("finger_"+str(finger)) != -1 and contact[-9:] != "prox_link":
				return True
		return False

	def fullFingerContact(self, finger):
		#finger is either 1, 2, or 3
		#if the tip finger link is in contact, returns 't' (finger is fully in contact)
		#if only the lower finger link is in contact, returns 's' (only lower link in contact)
		#if there is no contact return 'f' (nothing is in contact)
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
		#returns whether or not the palm is in contact with the object
		for contact in self.Hand.getContact(self.Obj.obj).keys():
			if contact[-9:] == "palm_link":
				return True
		return False

	def fingerChangingDirection(self, finger, percentClosed):
		#finger is either 1, 2, or 3
		#percentClosed is a float 0<>100
		#determines if the finger's motion has changed (was closing, now opening or was opening, now closing)
		return self.fingerOpening(finger, percentClosed) != self.fingerOpeningDict[finger]
	
	def fingerCanBeMovedThisWay(self, finger, percentClosed, contact):
		#finger is either 1, 2, or 3
		#percentClosed is a float 0<>100
		#contact is either 't', 'f', or 's'
		return self.ignoreContact[str(finger)] or self.fingerChangingDirection(finger, percentClosed) or contact != 't'
	
	def setFingerPosition(self, finger, percentClosed, contact):
		#finger is either 1, 2, or 3
		#percentClosed is a float 0<>100
		#contact is either 't'(rue), 'f'(alse), or 's'(some)
		#sets the new grasp values for the finger joints depending on which fingers have contact
		if finger == 1:
			if contact == 'f':
				self.grasp[3] = self.getMedJointAngle(percentClosed)
			self.grasp[4] = self.getDistJointAngle(percentClosed)
		elif finger == 2:
			if contact == 'f':
				self.grasp[6] = self.getMedJointAngle(percentClosed)
			self.grasp[7] = self.getDistJointAngle(percentClosed)
		elif finger ==3:
			if contact == 'f':
				self.grasp[8] = self.getMedJointAngle(percentClosed)
			self.grasp[9] = self.getDistJointAngle(percentClosed)
		self.showGrasp()
		print self.grasp

	def changeFingerPosition(self, finger, percentClosed):
		#finger is either 1, 2, or 3
		#percentClosed is a float 0<>100
		#changes the finger position to the new percentage if possible
		#checks the ignoreContact safeguard can be removed
		#returns whether or not the finger could be moved as suggested
		contact = self.fullFingerContact(finger)
		if self.fingerCanBeMovedThisWay(finger, percentClosed, contact):
			self.fingerOpeningDict[finger] = self.fingerOpening(finger, percentClosed)
			self.setFingerPosition(finger, percentClosed, contact)
			if self.ignoreContact[str(finger)]:
				self.ignoreContact[str(finger)] = self.fingerContact(finger)
			return True
		return False
	
	def getFingerPositionPercent(self, finger):
		#finger is either 1, 2, or 3
		#returns the percent of the finger closed
		if finger == 1:
			return (self.grasp[3]-self.medJointAngles["min"])/(self.medJointAngles["max"]-self.medJointAngles["min"])
		elif finger == 2:
			return (self.grasp[6]-self.medJointAngles["min"])/(self.medJointAngles["max"]-self.medJointAngles["min"])
		elif finger == 3:
			return (self.grasp[8]-self.medJointAngles["min"])/(self.medJointAngles["max"]-self.medJointAngles["min"])
	
	def showGrasp (self):
		#sets the Hand to the new grasp
		self.Hand.setJointAngles(self.grasp)

	
