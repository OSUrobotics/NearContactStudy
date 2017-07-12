import wx, pdb
import HandView
import os


class ChooserGUI(wx.Frame):
	def __init__(self, app):
		self.pregrasp_list = ['The Claw', 'The Pinch', 'The Cup', 'The Two-fer']
		self.shape_list = ['Cone', 'Cube', 'Cylinder', 'Ellipse']
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
		self.sizer = wx.FlexGridSizer(4, 1, 20)
		self.addShapeSizes()
		self.sizer.Add(self.sizesPnl, 0, wx.EXPAND)
		self.addButtons()
		self.sizer.Add(self.buttonSizer, 0, wx.EXPAND)
		self.addWristAndOffset()
		self.sizer.Add(self.wristOffPnl, 0, wx.EXPAND)
		self.addFingers()
		self.sizer.Add(self.fingerPnl, 0, wx.EXPAND)

	def parseImageFileName(self, name):
		underscore = name.find("_")
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
		imageFiles = os.listdir("/home/reu4/NearContactStudy/ShapeGenerator/Shapes")
		for image in imageFiles:
			self.parseImageFileName(image)
	def addShapeSizes(self):
		self.sizeOptions = {}
		self.findAllShapeSizeOptions()
		self.sizesPnl = wx.Panel(self)
		self.sizesSizer = wx.FlexGridSizer(len(self.sizeOptions), 1, 10)
		self.sizeRbs ={}
		for dimension in self.sizeOptions:
			self.sizeRbs[dimension] = []
			pnl = wx.Panel(self)
			grid = wx.FlexGridSizer(1, len(self.sizeOptions[dimension])+1,10)
			label = wx.StaticText(pnl, label = dimension, style=wx.ALIGN_CENTER)
			for value in sorted(self.sizeOptions[dimension]):
				self.sizeRbs[dimension].append(wx.RadioButton(pnl, 1, str(value)))
				grid.Add(self.sizeRbs[dimension][-1],1,flag = wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border = 10)
			pnl.SetSizer(grid)
			self.sizesSizer.Add(pnl, 0, wx.EXPAND)
		self.sizesPnl.SetSizer(self.sizesSizer)

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
		self.shape_buttons = []
		for shape in self.shape_list:
			current_button = wx.Button(self, -1, shape)
			self.shape_buttons.append(current_button)
			current_button.Bind(wx.EVT_BUTTON, self.objectChosen)
			self.buttonSizer.Add(current_button, 1, wx.EXPAND)
	def addPreGraspButtons(self):
		self.pg_buttons = []
		for pg in self.pregrasp_list:
			current_button = wx.Button(self, -1, pg)
			self.pg_buttons.append(current_button)
			current_button.Bind(wx.EVT_BUTTON, self.graspChosen)
			self.buttonSizer.Add(current_button, 1, wx.EXPAND)
	def addButtons(self):
		self.buttonSizer = wx.FlexGridSizer(2, len(self.pregrasp_list), 10)
		self.addShapeButtons()
		self.addPreGraspButtons()
		

	"--------------------------------------------------------------------------"

	def graspChosen(self, event):
		clicked = event.GetEventObject().GetLabel()
		grasp = self.view.setGrasp(clicked)
		self.fingers[0].SetValue(100*grasp[3]/2.44)
		self.fingers[1].SetValue(100*grasp[6]/2.44)
		self.fingers[2].SetValue(100*grasp[8]/2.44)
		print grasp

	def objectChosen(self, event):
		clicked = event.GetEventObject().GetLabel()
		if clicked != "Cone" and "a" in self.sizeRbs:
			for rb in self.sizeRbs["a"]:
				rb.Disable()
		elif clicked == "Cone" and "a" in self.sizeRbs:
			for rb in self.sizeRbs["a"]:
				rb.Enable()
		self.view.setObject(clicked)
	
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

