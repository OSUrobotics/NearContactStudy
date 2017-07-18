import wx, pdb
import HandView
import os
import math


class ChooserGUI(wx.Frame):
	def __init__(self, app):
		self.pregrasp_list = ['The Claw', 'The Pinch', 'The Cup', 'The Two-fer']
		self.currentShapeSize = {"shape":"cube", "h":"3", "w":"3", "e":"3", "a":"10"}
		self.sizeOptions = {}
		self.shape_list = {}
		self.findAllShapeSizeOptions()
		self.wristAngle = {'X':0, 'Y':0, 'Z':0}
		self.offset = {'X':50, 'Y':50, 'Z':50}
		self.view = HandView.HandView()
		wx.Frame.__init__(self, parent=None, title="PreGrasp Chooser", pos=(-1, -1));
		self.addEverything()
		self.SetSizer(self.sizer)
		self.sizer.Fit(self)
		self.Show()		

	def addEverything(self):
		self.sizer = wx.FlexGridSizer(8, 2, 20)
		self.TitleFont = wx.Font(10,wx.DEFAULT, wx.NORMAL, wx.BOLD)
		self.addShapeButtons()
		self.sizer.Add(self.shapePnl, 0, wx.EXPAND)
		self.addPreGraspButtons()
		self.sizer.Add(self.pgPnl, 0, wx.EXPAND)
		self.addShapeSizes()
		self.sizer.Add(self.sizesPnl, 0, wx.EXPAND)
		self.addWristSliders()
		self.sizer.Add(self.wristPnl, 0, wx.EXPAND)
		self.addOffsetSliders()
		self.sizer.Add(self.offPnl, 0, wx.EXPAND)
		self.addFingers()
		self.sizer.Add(self.fingerPnl, 0, wx.EXPAND)

	def parseImageFileName(self, name):
		underscore = name.find("_")
		current_shape = name[0:underscore]
		if current_shape not in self.shape_list:
			self.shape_list[current_shape] = []
			for character in name[underscore:]:
				if character.isalpha():
					self.shape_list[current_shape].append(character)
				if character == '.':
					break
		while underscore != -1:
			dimension = name[underscore+1]
			value = ""
			i=2
			while name[underscore+i].isdigit():
				value += name[underscore+i]
				i+=1
			if dimension not in self.sizeOptions:
				self.sizeOptions[dimension] = []
			if int(value) not in self.sizeOptions[dimension]:
				self.sizeOptions[dimension].append(int(value))
			underscore = name.find("_", underscore+1)
	def findAllShapeSizeOptions(self):
		imageFiles = os.listdir("/home/reu3/Documents/NearContactStudy/ShapeGenerator/Shapes")
		for image in imageFiles:
			self.parseImageFileName(image)
		for dimension in self.sizeOptions:
			self.sizeOptions[dimension] = [str(value) for value in sorted(self.sizeOptions[dimension])]
		print self.shape_list
	
	def addOffsetSliders(self):
		self.offPnl= wx.Panel(self)
		self.offPnl.SetBackgroundColour((0xd9,0xfc,0xd9))
		offSizer = wx.FlexGridSizer(7,1,10)
		self.offsetSliders = {}
		offLabel = wx.StaticText(self.offPnl, label='Object Offset', style=wx.ALIGN_CENTER)
		offLabel.SetFont(self.TitleFont)
		offSizer.Add(offLabel, 1, wx.ALIGN_CENTER_HORIZONTAL)
		for dimension in ['X', 'Y', 'Z']:
			dimensionLabel = wx.StaticText(self.offPnl, label = '\t'+dimension, style=wx.ALIGN_LEFT)
			offSizer.Add(dimensionLabel, 1, wx.ALIGN_LEFT)
			self.offsetSliders[dimension] = wx.Slider(self.offPnl, value = self.offset[dimension], minValue = 0, maxValue = 100, size=(250,40),
				style = wx.SL_HORIZONTAL|wx.SL_LABELS)
			self.offsetSliders[dimension].Bind(wx.EVT_SLIDER, self.OnOffset)
			offSizer.Add(self.offsetSliders[dimension],1,flag = wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border = 10)
		self.offPnl.SetSizer(offSizer)

	def addWristSliders(self):
		self.wristPnl = wx.Panel(self)
		self.wristPnl.SetBackgroundColour((0xdd,0xd9,0xfc))
		wristSizer = wx.FlexGridSizer(7,1,10)
		self.wristSliders = {}
		wristLabel = wx.StaticText(self.wristPnl, label="Wrist Rotation", style=wx.ALIGN_CENTER)
		wristLabel.SetFont(self.TitleFont)
		wristSizer.Add(wristLabel, 1, wx.ALIGN_CENTER_HORIZONTAL)
		for dimension in ['X', 'Y', 'Z']:
			dimensionLabel = wx.StaticText(self.wristPnl, label='\t'+dimension, style=wx.ALIGN_LEFT)
			wristSizer.Add(dimensionLabel, 1, wx.ALIGN_LEFT)
			self.wristSliders[dimension] = wx.Slider(self.wristPnl, value=self.wristAngle[dimension], minValue=0, maxValue=100, size=(250,40),
				style=wx.SL_HORIZONTAL|wx.SL_LABELS)
			self.wristSliders[dimension].Bind(wx.EVT_SLIDER, self.OnRotation)
			wristSizer.Add(self.wristSliders[dimension],1,flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=10)
		self.wristPnl.SetSizer(wristSizer)

	def addFingerLabels(self):
		for i in range(1, 4):
			label = wx.StaticText(self.fingerPnl, label = 'Finger '+str(i),style = wx.ALIGN_CENTER)                
			self.fingerSizer.Add(label,1,wx.ALIGN_CENTER_HORIZONTAL) 
	def addFingerSliders(self):
		for i in range(1, 4):
			self.fingers.append(wx.Slider(self.fingerPnl, value = 0, minValue = 0, maxValue = 100, size=(100,200),
				style = wx.SL_VERTICAL|wx.SL_LABELS))
			self.fingers[-1].Bind(wx.EVT_SLIDER, self.OnFinger)
			self.fingerSizer.Add(self.fingers[-1],1,flag = wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border = 20)
	def addFingers(self):
		self.fingers = []
		self.fingerPnl = wx.Panel(self)
		self.fingerPnl.SetBackgroundColour((0xdd,0xd9,0xfc))
		self.fingerSizer = wx.FlexGridSizer(2, 3, 10)
		self.addFingerLabels()
		self.addFingerSliders()
		self.fingerPnl.SetSizer(self.fingerSizer)

	def addShapeButtons(self):
		self.shapePnl = wx.Panel(self)
		self.shapePnl.SetBackgroundColour((0xd9,0xfc,0xd9))
		shapeButtonSizer = wx.FlexGridSizer(math.ceil(len(self.pregrasp_list)/3), 3, 10)
		self.shape_buttons = []
		for shape in self.shape_list:
			current_button = wx.Button(self.shapePnl, -1, shape)
			self.shape_buttons.append(current_button)
			current_button.Bind(wx.EVT_BUTTON, self.objectChosen)
			shapeButtonSizer.Add(current_button, 1, wx.EXPAND)
		self.shapePnl.SetSizer(shapeButtonSizer)

	def addPreGraspButtons(self):
		self.pgPnl = wx.Panel(self)
		self.pgPnl.SetBackgroundColour((0xdd,0xd9,0xfc))
		pgButtonSizer = wx.FlexGridSizer(math.ceil(len(self.pregrasp_list)/3), 3, 10)
		self.pg_buttons = []
		for pg in self.pregrasp_list:
			current_button = wx.Button(self.pgPnl, -1, pg)
			self.pg_buttons.append(current_button)
			current_button.Bind(wx.EVT_BUTTON, self.graspChosen)
			pgButtonSizer.Add(current_button, 1, wx.EXPAND)
		self.pgPnl.SetSizer(pgButtonSizer)

	def addShapeSizes(self):
		self.sizesPnl = wx.Panel(self)
		self.sizesPnl.SetBackgroundColour((0xd9,0xfc,0xd9))
		self.sizesSizer = wx.FlexGridSizer(len(self.sizeOptions), 1, 10)
		self.sizeRbs = {}
		for dimension in self.sizeOptions:
			self.sizeRbs[dimension] = wx.RadioBox(self.sizesPnl, 1, dimension, choices=self.sizeOptions[dimension])
			self.sizeRbs[dimension].SetSelection(0)
			self.sizeRbs[dimension].Bind(wx.EVT_RADIOBOX, self.OnSizeSelection)
			self.sizesSizer.Add(self.sizeRbs[dimension], 1, wx.EXPAND)
			self.currentShapeSize[dimension] = self.sizeOptions[dimension][0]
			if dimension == 'a':
				self.sizeRbs[dimension].Disable()
		self.sizesPnl.SetSizer(self.sizesSizer)

	"--------------------------------------------------------------------------"
	def OnSizeSelection(self, event):
		radioBox = event.GetEventObject()
		dimension = radioBox.GetLabel()
		newSize = radioBox.GetItemLabel(radioBox.GetSelection()).encode("ascii")
		self.currentShapeSize[dimension] = newSize
		self.view.setObject(self.currentShapeSize)


	def graspChosen(self, event):
		clicked = event.GetEventObject().GetLabel()
		grasp = self.view.setGrasp(clicked)
		self.fingers[0].SetValue(100*grasp[3]/2.44)
		self.fingers[1].SetValue(100*grasp[6]/2.44)
		self.fingers[2].SetValue(100*grasp[8]/2.44)
		print grasp

	def objectChosen(self, event):
		clicked = event.GetEventObject().GetLabel()
		self.currentShapeSize["shape"] = clicked
		for dimension in self.sizeRbs:
			if dimension not in self.shape_list[clicked]:
				self.sizeRbs[dimension].Disable()
			else:
				self.sizeRbs[dimension].Enable()
		self.view.setObject(self.currentShapeSize)
	
	def OnFinger(self, event):
		slider = event.GetEventObject()
		finger = self.fingers.index(slider)+1
		print self.view.changeFingerPosition(finger, slider.GetValue())

	def OnRotation(self, event):
		for dimension in self.wristSliders:
			if self.wristSliders[dimension] == event.GetEventObject():
				direction = dimension
				break
		newAngle = event.GetEventObject().GetValue()
		self.view.setWristRotation(direction, newAngle-self.wristAngle[direction])
		self.wristAngle[direction] = newAngle

	def OnOffset(self, event):
		for dimension in self.offsetSliders:
			if self.offsetSliders[dimension] == event.GetEventObject():
				direction = dimension
				break
		newOffset = event.GetEventObject().GetValue()
		self.view.setObjectOffset(direction, float(self.offset[direction]-newOffset)/200)
		self.offset[direction] = newOffset

"----------------------------------------------------------------------------"

if __name__ == "__main__":
	app = wx.App(False)
	frame = ChooserGUI(app)
	pdb.set_trace()
	app.MainLoop()

