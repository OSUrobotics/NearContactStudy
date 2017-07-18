import wx, pdb
import HandView
import os


class ChooserGUI(wx.Frame):
	def __init__(self, app):
		self.pregrasp_list = ['The Claw', 'The Pinch', 'The Cup', 'The Two-fer']
		self.currentShapeSize = {"shape":"cube", "h":"3", "w":"3", "e":"3", "a":"10"}
		self.sizeOptions = {}
		self.shape_list = []
		self.findAllShapeSizeOptions()
		self.wristAngle = 0
		self.offset = 20
		self.view = HandView.HandView()
		wx.Frame.__init__(self, parent=None, title="PreGrasp Chooser", pos=(-1, -1));
		self.sizer = wx.FlexGridSizer(2, 1, 20)
		self.addEverything()
		self.SetSizer(self.sizer)
		self.sizer.Fit(self)
		self.Show()		

	def addEverything(self):
		self.sizer = wx.FlexGridSizer(5, 1, 20)
		self.addShapeSizes()
		self.sizer.Add(self.sizesPnl, 0, wx.EXPAND)
		self.addShapeButtons()
		self.sizer.Add(self.shapeButtonSizer, 0, wx.EXPAND)
		self.addPreGraspButtons()
		self.sizer.Add(self.pgButtonSizer, 0, wx.EXPAND)
		self.addWristAndOffset()
		self.sizer.Add(self.wristOffPnl, 0, wx.EXPAND)
		self.addFingers()
		self.sizer.Add(self.fingerPnl, 0, wx.EXPAND)

	def parseImageFileName(self, name):
		underscore = name.find("_")
		if name[0:underscore] not in self.shape_list:
			self.shape_list.append(name[0:underscore])
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

	def addOffsetSlider(self):
		self.offLabel = wx.StaticText(self.wristOffPnl, label='Object Offset', style=wx.ALIGN_CENTER)
		self.wristOffSizer.Add(self.offLabel, 1, wx.ALIGN_CENTER_HORIZONTAL)
		self.offSlider = wx.Slider(self.wristOffPnl, value = self.offset, minValue = 0, maxValue = 100, size=(200,40),
				style = wx.SL_HORIZONTAL|wx.SL_LABELS)
		self.offSlider.Bind(wx.EVT_SLIDER, self.OnOffset)
		self.wristOffSizer.Add(self.offSlider,1,flag = wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border = 10)
	def addWristSlider(self):
		self.wristLabel = wx.StaticText(self.wristOffPnl, label='Wrist Angle', style=wx.ALIGN_CENTER)
		self.wristOffSizer.Add(self.wristLabel, 1, wx.ALIGN_CENTER_HORIZONTAL)
		self.wristSlider = wx.Slider(self.wristOffPnl, value = 0, minValue = 0, maxValue = 100, size=(200,40),
				style = wx.SL_HORIZONTAL|wx.SL_LABELS)
		self.wristSlider.Bind(wx.EVT_SLIDER, self.OnRotation)
		self.wristOffSizer.Add(self.wristSlider,1,flag = wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border = 10)
	def addWristAndOffset(self):
		self.wristOffPnl = wx.Panel(self)
		self.wristOffSizer = wx.FlexGridSizer(2,2,10)
		self.addWristSlider()
		self.addOffsetSlider()
		self.wristOffPnl.SetSizer(self.wristOffSizer)

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
		self.fingerSizer = wx.FlexGridSizer(2, 3, 10)
		self.addFingerLabels()
		self.addFingerSliders()
		self.fingerPnl.SetSizer(self.fingerSizer)

	def addShapeButtons(self):
		self.shapeButtonSizer = wx.FlexGridSizer(1, len(self.shape_list), 10)
		self.shape_buttons = []
		for shape in self.shape_list:
			current_button = wx.Button(self, -1, shape)
			self.shape_buttons.append(current_button)
			current_button.Bind(wx.EVT_BUTTON, self.objectChosen)
			self.shapeButtonSizer.Add(current_button, 1, wx.EXPAND)

	def addPreGraspButtons(self):
		self.pgButtonSizer = wx.FlexGridSizer(1, len(self.pregrasp_list), 10)
		self.pg_buttons = []
		for pg in self.pregrasp_list:
			current_button = wx.Button(self, -1, pg)
			self.pg_buttons.append(current_button)
			current_button.Bind(wx.EVT_BUTTON, self.graspChosen)
			self.pgButtonSizer.Add(current_button, 1, wx.EXPAND)

	def addShapeSizes(self):
		self.sizesPnl = wx.Panel(self)
		self.sizesSizer = wx.FlexGridSizer(len(self.sizeOptions), 1, 10)
		self.sizeRbs ={}
		for dimension in self.sizeOptions:
			rBox = wx.RadioBox(self.sizesPnl, 1, dimension, choices=self.sizeOptions[dimension])
			rBox.SetSelection(0)
			rBox.Bind(wx.EVT_RADIOBOX, self.OnSizeSelection)
			self.sizesSizer.Add(rBox, 1, wx.EXPAND)
			self.currentShapeSize[dimension] = self.sizeOptions[dimension][0]
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
		if clicked != "cone" and "a" in self.sizeRbs:
			for rb in self.sizeRbs["a"]:
				rb.Disable()
		elif clicked == "cone" and "a" in self.sizeRbs:
			for rb in self.sizeRbs["a"]:
				rb.Enable()
		self.view.setObject(self.currentShapeSize)
	
	def OnFinger(self, event):
		slider = event.GetEventObject()
		finger = self.fingers.index(slider)+1
		print self.view.changeFingerPosition(finger, slider.GetValue())

	def OnRotation(self, event):
		slider = event.GetEventObject()
		newAngle = slider.GetValue()
		self.view.setWristRotation(newAngle-self.wristAngle)
		self.wristAngle = newAngle

	def OnOffset(self, event):
		newOffset = event.GetEventObject().GetValue()
		self.view.setObjectOffset(float(self.offset-newOffset)/200)
		self.offset = newOffset

"----------------------------------------------------------------------------"

if __name__ == "__main__":
	app = wx.App(False)
	frame = ChooserGUI(app)
	pdb.set_trace()
	app.MainLoop()

