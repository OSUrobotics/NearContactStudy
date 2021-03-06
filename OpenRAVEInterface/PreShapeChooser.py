import wx, pdb
import HandView
import sys, os
import math
from openravepy import *
import numpy as np
curdir = os.path.dirname(os.path.realpath(__file__))
classdir = curdir +'/../InterpolateGrasps/'
sys.path.insert(0, classdir)
from Colors import ColorsDict, bcolors

"""
This creates a GUI with which to affect an OpenRAVE Simulation
This runs a HandView class (as the simulation) so HandView.py must be in the same folder
All shape models must be in ../ShapeGenerator/Shapes/
Visualizers.py and Colors.py must be in ../InterpolateGrasps/
"""

class ChooserGUI(wx.Frame):
	def __init__(self, app):
		self.setDefaults()
		self.findAllShapeSizeOptions()
		self.currentShapeSize = {"shape":self.shapeList.keys()[0], 
			"h":self.sizeOptions['h'][0], "w":self.sizeOptions['w'][0], 
			"e":self.sizeOptions['e'][0], "a":self.sizeOptions['a'][0]}
		self.createSimulation()
		self.createGUI()

	def setDefaults(self):
		#sets default hard coded values
		self.grasps = {'Pinch 3' : np.array([0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]),
						'Equidistant' : np.array([0,0,np.pi/4,0,0,np.pi/4,0,0,0,0]),
						'Pinch 2' : np.array([0,0,np.pi/2,0,0,np.pi/2,0,0,0,0]),
						'Hook' : np.array([0,0,np.pi,0,0,np.pi,0,0,0,0])}
		self.wristAngle = {'X':0, 'Y':0, 'Z':0}
		self.objAngle = {'X':0, 'Y':0, 'Z':0}
		self.translation = {'X':100, 'Y':100, 'Z':100}
		self.handColor = 'yellowI'
		self.objColor = 'purpleI'
		self.handPnlBackground = self.setColor(self.handColor)
		self.objPnlBackground = self.setColor(self.objColor)
		self.imageFiles = os.listdir(curdir + "/../ShapeGenerator/Shapes")
		self.fingerSliderRange = {"min": 0, "max": 200}
		self.rotationSliderRange = {"min":0, "max":360}

	def setColor(self, colorName):
		#colorName is a string that corresponds to an array in ColorsDict.colors
		#returns the tuple of color values by taking a color (usually hand and obj)
		#and lightening it to be a background for panels in the GUI
		color = list(ColorsDict.colors[colorName]*255*1.67)
		maxCE = max(color)
		minCE = min(color)
		for i in range(0,3):
			if color.count(maxCE) == 1:
				color[color.index(maxCE)] = 255
			if color.count(minCE) == 1:
				color[color.index(minCE)] = 200
		color[color.index(max(color))] = 255
		return color

	def tryAddDimensionValue(self, dimension, value):
		#dimension is a string, value is a string representing an int
		if int(value) not in self.sizeOptions[dimension]:
			self.sizeOptions[dimension].append(int(value))

	def getDimensionValue(self, name, dimension, shape):
		#name is the file name (it contains all the dimension values and shape)
		#dimension and shape is a string
		#determines if any of the values in name have not been dded to self.sizeOptions
		#and if so, adds them
		value = ""
		for c in name:
			if c == '.':
				self.tryAddDimensionValue(dimension, value)
				break
			elif c == '_':
				self.tryAddDimensionValue(dimension, value)
				self.getDimension(name[len(value)+1:], shape)
				break
			elif c.isdigit():
				value += c
	def getDimension(self, name, shape=None):
		#name is a string that is the file name
		#if passed, shape is a string
		#finds the next dimension in the file name and passes that
		dimension = name[0]
		if shape:
			self.shapeList[shape].append(dimension)
		if dimension not in self.sizeOptions:
			self.sizeOptions[dimension] = []
		self.getDimensionValue(name[1:], dimension, shape)

	def parseImageFileName(self, name):
		#name is a string that is the file name
		#takes the shape and dimensions in the file name and determines if anything
		#has not yet been added to self.sizeOptions and adds them
		underscore = name.find("_")
		shape = name[0:underscore]
		if shape not in self.shapeList:
			self.shapeList[shape] = []
			self.getDimension(name[underscore+1:], shape)
		else:
			self.getDimension(name[underscore+1:])
	def findAllShapeSizeOptions(self):
		#looks through all the files in self.imageFiles to determine
		#what dimensions and sizes need to be added to self.sizeOptions
		self.sizeOptions = {}
		self.shapeList = {}
		for image in self.imageFiles:
			self.parseImageFileName(image)
		for dimension in self.sizeOptions:
			self.sizeOptions[dimension] = [str(value) for value in sorted(self.sizeOptions[dimension])]

	def createSimulation(self):
		#adds the Hand and Object to the view
		self.view = HandView.HandView(self.handColor, self.objColor, self.grasps)
		self.view.addHand(self.grasps.keys()[0])
		self.view.addObject(self.currentShapeSize)		
	
	def createGUI(self):
		#creates a frame and adds all the GUI elements to it
		wx.Frame.__init__(self, parent=None, title="PreGrasp Chooser", pos=(-1, -1));
		self.sizer = wx.FlexGridSizer(8, 2, 20)
		self.TitleFont = wx.Font(10,wx.DEFAULT, wx.NORMAL, wx.BOLD)
		self.addPreGraspInterface()
		self.addShapeInterface()
		self.addTranslationInterface()
		self.addShapeSizeInterface()
		self.addWristRotationInterface()
		self.addObjRotationInterface()
		self.addFingerInterface()
		self.sizer.Fit(self)
		self.SetSizer(self.sizer)
		self.Show()
	
	def addShapeInterface(self):
		#Adds a button for every shape 
		shapePnl = wx.Panel(self)
		shapePnl.SetBackgroundColour(self.objPnlBackground)
		shapeButtonSizer = wx.FlexGridSizer(math.ceil(len(self.shapeList)/3), 3, 10)
		self.shape_buttons = []
		for shape in self.shapeList:
			current_button = wx.Button(shapePnl, -1, shape)
			self.shape_buttons.append(current_button)
			current_button.Bind(wx.EVT_BUTTON, self.onObjectChosen)
			shapeButtonSizer.Add(current_button, 1, wx.EXPAND)
		shapePnl.SetSizer(shapeButtonSizer)
		self.sizer.Add(shapePnl, 0, wx.EXPAND)

	def addPreGraspInterface(self):
		#adds a button for every grasp in self.grasps
		pgPnl = wx.Panel(self)
		pgPnl.SetBackgroundColour(self.handPnlBackground)
		pgButtonSizer = wx.FlexGridSizer(math.ceil(len(self.grasps)/3), 3, 10)
		self.pg_buttons = []
		for pg in self.grasps:
			current_button = wx.Button(pgPnl, -1, pg)
			self.pg_buttons.append(current_button)
			current_button.Bind(wx.EVT_BUTTON, self.onGraspChosen)
			pgButtonSizer.Add(current_button, 1, wx.EXPAND)
		pgPnl.SetSizer(pgButtonSizer)
		self.sizer.Add(pgPnl, 0, wx.EXPAND)

	def addShapeSizeInterface(self):
		#adds radio buttons for each dimension for each size option as found in self.shapeSizeOptions
		sizesPnl = wx.Panel(self)
		sizesPnl.SetBackgroundColour(self.objPnlBackground)
		self.sizesSizer = wx.FlexGridSizer(len(self.sizeOptions), 1, 10)
		self.sizeRbs = {}
		for dimension in self.sizeOptions:
			self.sizeRbs[dimension] = wx.RadioBox(sizesPnl, 1, dimension, choices=self.sizeOptions[dimension])
			self.sizeRbs[dimension].SetSelection(self.sizeOptions[dimension].index(self.currentShapeSize[dimension]))
			self.sizeRbs[dimension].Bind(wx.EVT_RADIOBOX, self.onSizeSelection)
			self.sizesSizer.Add(self.sizeRbs[dimension], 1, wx.EXPAND)
			self.currentShapeSize[dimension] = self.sizeOptions[dimension][0]
			if dimension == 'a':
				self.sizeRbs[dimension].Disable()
		sizesPnl.SetSizer(self.sizesSizer)
		self.sizer.Add(sizesPnl, 0, wx.EXPAND)
	
	def addWristRotationInterface(self):
		#adds 3 sliders (X, Y, Z) that when moved, change the orientation of the hand
		self.wristPnl = wx.Panel(self)
		self.wristPnl.SetBackgroundColour(self.handPnlBackground)
		wristSizer = wx.FlexGridSizer(7,1,10)
		self.wristSliders = {}
		wristLabel = wx.StaticText(self.wristPnl, label="Hand Rotation", style=wx.ALIGN_CENTER)
		wristLabel.SetFont(self.TitleFont)
		wristSizer.Add(wristLabel, 1, wx.ALIGN_CENTER_HORIZONTAL)
		for dimension in sorted(self.wristAngle.keys()):
			dimensionLabel = wx.StaticText(self.wristPnl, label='\t'+dimension, style=wx.ALIGN_LEFT)
			wristSizer.Add(dimensionLabel, 1, wx.ALIGN_LEFT)
			self.wristSliders[dimension] = wx.Slider(self.wristPnl, value=self.wristAngle[dimension], minValue=self.rotationSliderRange["min"], maxValue=self.rotationSliderRange["max"], size=(250,40),
				style=wx.SL_HORIZONTAL|wx.SL_LABELS)
			self.wristSliders[dimension].Bind(wx.EVT_SLIDER, self.onWristRotation)
			wristSizer.Add(self.wristSliders[dimension],1,flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=10)
		self.wristPnl.SetSizer(wristSizer)
		self.sizer.Add(self.wristPnl, 0, wx.EXPAND)

	def addObjRotationInterface(self):
		#adds 3 sliders (x, Y, Z) that when moved, change the orientation of the object
		objPnl = wx.Panel(self)
		objPnl.SetBackgroundColour(self.objPnlBackground)
		ObjSizer = wx.FlexGridSizer(7,1,10)
		self.objSliders = {}
		ObjLabel = wx.StaticText(objPnl, label="Object Rotation", style=wx.ALIGN_CENTER)
		ObjLabel.SetFont(self.TitleFont)
		ObjSizer.Add(ObjLabel, 1, wx.ALIGN_CENTER_HORIZONTAL)
		for dimension in sorted(self.objAngle.keys()):
			dimensionLabel = wx.StaticText(objPnl, label='\t'+dimension, style=wx.ALIGN_LEFT)
			ObjSizer.Add(dimensionLabel, 1, wx.ALIGN_LEFT)
			self.objSliders[dimension] = wx.Slider(objPnl, value=self.objAngle[dimension], minValue=self.rotationSliderRange["min"], maxValue=self.rotationSliderRange["max"], size=(250,40),
				style=wx.SL_HORIZONTAL|wx.SL_LABELS)
			self.objSliders[dimension].Bind(wx.EVT_SLIDER, self.onObjRotation)
			ObjSizer.Add(self.objSliders[dimension],1,flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=10)
		objPnl.SetSizer(ObjSizer)
		self.sizer.Add(objPnl, 0, wx.EXPAND)

	def addFingerLabels(self, fingerPnl):
		#adds labels for the finger sliders
		for i in range(1, 4):
			label = wx.StaticText(fingerPnl, label = 'Finger '+str(i),style = wx.ALIGN_CENTER)
			label.SetFont(self.TitleFont)               
			self.fingerSizer.Add(label,1,wx.ALIGN_CENTER_HORIZONTAL) 
	def addFingerSliders(self, fingerPnl):
		#adds sliders to control the fingers
		for i in range(1, 4):
			self.fingers.append(wx.Slider(fingerPnl, value = 0, minValue = self.fingerSliderRange["min"], maxValue = self.fingerSliderRange["max"], size=(100,200),
				style = wx.SL_VERTICAL|wx.SL_LABELS))
			self.fingers[-1].Bind(wx.EVT_SLIDER, self.onFinger)
			self.fingerSizer.Add(self.fingers[-1],1,flag = wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border = 20)
	def addFingerInterface(self):
		#adds a slider for every finger, that can close and open the finger
		self.fingers = []
		fingerPnl = wx.Panel(self)
		fingerPnl.SetBackgroundColour(self.handPnlBackground)
		self.fingerSizer = wx.FlexGridSizer(2, 3, 10)
		self.addFingerLabels(fingerPnl)
		self.addFingerSliders(fingerPnl)
		fingerPnl.SetSizer(self.fingerSizer)
		self.sizer.Add(fingerPnl, 0, wx.EXPAND)

	def addTranslationInterface(self):
		#adds three sliders (X, Y, Z) to translate the hand in the direction
		offPnl= wx.Panel(self)
		offPnl.SetBackgroundColour(self.handPnlBackground)
		offSizer = wx.FlexGridSizer(7,1,10)
		self.translationSliders = {}
		offLabel = wx.StaticText(offPnl, label='Hand Translation', style=wx.ALIGN_CENTER)
		offLabel.SetFont(self.TitleFont)
		offSizer.Add(offLabel, 1, wx.ALIGN_CENTER_HORIZONTAL)
		for dimension in sorted(self.translation.keys()):
			dimensionLabel = wx.StaticText(offPnl, label = '\t'+dimension, style=wx.ALIGN_LEFT)
			offSizer.Add(dimensionLabel, 1, wx.ALIGN_LEFT)
			self.translationSliders[dimension] = wx.Slider(offPnl, value = self.translation[dimension], minValue = 0, maxValue = 200, size=(250,40),
				style = wx.SL_HORIZONTAL|wx.SL_LABELS)
			self.translationSliders[dimension].Bind(wx.EVT_SLIDER, self.onTranslation)
			offSizer.Add(self.translationSliders[dimension],1,flag = wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border = 10)
		offPnl.SetSizer(offSizer)
		self.sizer.Add(offPnl, 0, wx.EXPAND)


	"--------------------------------------------------------------------------"
	def setFingerSliders(self):
		#adjust the finger sliders in case there was contact and the finger could not be moved
		self.fingers[0].SetValue((self.fingerSliderRange["max"]-self.fingerSliderRange["min"])*self.view.getFingerPositionPercent(1)+self.fingerSliderRange["min"])
		self.fingers[1].SetValue((self.fingerSliderRange["max"]-self.fingerSliderRange["min"])*self.view.getFingerPositionPercent(2)+self.fingerSliderRange["min"])
		self.fingers[2].SetValue((self.fingerSliderRange["max"]-self.fingerSliderRange["min"])*self.view.getFingerPositionPercent(3)+self.fingerSliderRange["min"])
	
	def onSizeSelection(self, event):
		# called when the object's size is changed (radio button selected)
		radioBox = event.GetEventObject()
		dimension = radioBox.GetLabel()
		newSize = radioBox.GetItemLabel(radioBox.GetSelection()).encode("ascii")
		self.currentShapeSize[dimension] = newSize
		self.view.setObject(self.currentShapeSize)


	def onGraspChosen(self, event):
		#called when a grasp button is clicked
		clicked = event.GetEventObject().GetLabel()
		grasp = self.view.setGrasp(clicked)
		self.setFingerSliders()
		print grasp

	def onObjectChosen(self, event):
		#called when a new object shape button is clicked
		clicked = event.GetEventObject().GetLabel()
		self.currentShapeSize["shape"] = clicked
		for dimension in self.sizeRbs:
			if dimension not in self.shapeList[clicked]:
				self.sizeRbs[dimension].Disable()
			else:
				self.sizeRbs[dimension].Enable()
		self.view.setObject(self.currentShapeSize)
	
	def onFinger(self, event):
		#called when a finger slider is moved to close or open the finger
		slider = event.GetEventObject()
		finger = self.fingers.index(slider)+1
		if not self.view.changeFingerPosition(finger, (float(slider.GetValue())-self.fingerSliderRange["min"])/(self.fingerSliderRange["max"]-self.fingerSliderRange["min"])):
			self.setFingerSliders()
	
	def onWristRotation(self, event):
		#called when a hand orientation slider is moved
		for dimension in self.wristSliders:
			if self.wristSliders[dimension] == event.GetEventObject():
				direction = dimension
				break
		activatedSlider = event.GetEventObject()
		newAngle = activatedSlider.GetValue()
		self.view.setWristRotation(direction, float(newAngle-self.wristAngle[direction])/((self.rotationSliderRange["max"]-self.rotationSliderRange["min"]) * .16))
		self.wristAngle[direction] = newAngle

	def onObjRotation(self, event):
		#called when an object orientation slider is moved
		for dimension in self.objSliders:
			if self.objSliders[dimension] == event.GetEventObject():
				direction = dimension
				break
		newAngle = event.GetEventObject().GetValue()
		self.view.setObjRotation(direction, float(newAngle-self.objAngle[direction])/((self.rotationSliderRange["max"]-self.rotationSliderRange["min"])*.16))
		self.objAngle[direction] = newAngle

	def onTranslation(self, event):
		#called when a hand translation slider is moved
		for dimension in self.translationSliders:
			if self.translationSliders[dimension] == event.GetEventObject():
				direction = dimension
				break
		newTranslation = event.GetEventObject().GetValue()
		newOffset = float(self.translation[direction]-newTranslation)/200
		if newOffset != 0:
			trueOffset = self.view.setHandTranslation(direction, newOffset)
			if trueOffset == newOffset:
				self.translation[direction] = newTranslation
			else:
				self.translation[direction] = self.translation[direction]+(trueOffset*-200)
				event.GetEventObject().SetValue(self.translation[direction])

"----------------------------------------------------------------------------"

if __name__ == "__main__":
	app = wx.App(False)
	GUI = ChooserGUI(app)
	pdb.set_trace()
	app.MainLoop()

