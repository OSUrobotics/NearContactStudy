#!/usr/bin/env python

import random
import wx
import wx.lib.newevent
import xml.dom.minidom
from math import pi
from threading import Thread
import os, pdb

RANGE = 10000

class Tester(wx.Frame): # would be cool to do this directly in OpenRave by clicking on scene
	def __init__(self, app):
		self.createFrame()
		self.loadJointList()
		self.Show()
		# app.MainLoop()
		self.createSliders()

	def createFrame(self):
		title = "Testing"
		wx.Frame.__init__(self, None, -1, title, (-1, -1));
		self.panel = wx.Panel(self, wx.ID_ANY);
		self.box = wx.BoxSizer(wx.VERTICAL)
		self.font = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD)

	def createSliders(self):
		# pdb.set_trace()
		for count, joint in enumerate(self.joint_list):
			print(joint)
			row = wx.GridSizer(1,2) # 1x2 row item
			label = wx.StaticText(self.panel, -1, joint) # create label
			label.SetFont(self.font)
			row.Add(label, 1, wx.ALIGN_CENTER_VERTICAL) # add label to row
			display = wx.TextCtrl(self.panel, value = str(0), style = wx.TE_READONLY | wx.ALIGN_LEFT)
			row.Add(display, flag= wx.ALIGN_RIGHT| wx.ALIGN_CENTER_VERTICAL) # add text box to row
			self.box.Add(row, 1, wx.EXPAND) # add row to box

			slider = wx.Slider(self.panel, -1, RANGE/2, 0, RANGE, style = wx.SL_AUTOTICKS | wx.SL_HORIZONTAL)
			slider.SetFont(self.font)
			self.box.Add(slider, 1, wx.EXPAND)



		self.panel.SetSizer(self.box)
		self.box.Fit(self)
		self.UpdateSlidersEvent, self.EVT_UPDATESLIDERS = wx.lib.newevent.NewEvent()
		self.Bind(self.EVT_UPDATESLIDERS, self.updateSliders)

	def update_sliders(self):
		for (name,joint_info) in self.joint_map.items():
			joint = joint_info['joint']
			joint_info['slidervalue'] = self.valueToSlider(joint['position'],
														   joint)
			joint_info['slider'].SetValue(joint_info['slidervalue'])
			joint_info['display'].SetValue("%.2f"%joint['position'])
		### Sliders ###
		#print "Joint list: ", self.jsp.joint_list
		# for name in self.jsp.joint_list:
		# 	if name not in self.jsp.free_joints:
		# 		continue
		# 	joint = self.jsp.free_joints[name]

		# 	if joint['min'] == joint['max']:
		# 		continue

		# 	row = wx.GridSizer(1,2)
		# 	label = wx.StaticText(panel, -1, name)
		# 	label.SetFont(font)
		# 	row.Add(label, 1, wx.ALIGN_CENTER_VERTICAL)

		# 	display = wx.TextCtrl (panel, value=str(0),
		# 				style=wx.TE_READONLY | wx.ALIGN_RIGHT)

		# 	row.Add(display, flag= wx.ALIGN_RIGHT| wx.ALIGN_CENTER_VERTICAL)
		# 	box.Add(row, 1, wx.EXPAND)
		# 	slider = wx.Slider(panel, -1, RANGE/2, 0, RANGE,
		# 				style= wx.SL_AUTOTICKS | wx.SL_HORIZONTAL)
		# 	slider.SetFont(font)
		# 	box.Add(slider, 1, wx.EXPAND)

		# 	self.joint_map[name] = {'slidervalue':0, 'display':display,
		# 							'slider':slider, 'joint':joint}

	def loadModel(self):
		base_path = os.path.dirname(os.path.realpath(__file__))
		base_path += '/../Interpolate Grasps/models/robots/'
	
	def loadJointList(self): # what does this do?
		self.free_joints = {}
		self.joint_list = []
		self.joint_list = ['Finger 1', 'Finger 2', 'Finger 3', 'Spread', 'Grasp Level']
		for name in self.joint_list:
			joint = {'min':0, 'max':2.5, 'zero':0, 'position':0}
			self.free_joints[name] = joint
		self.free_joints['Spread']['max'] = 3.14

class HandCommandGui(wx.Frame):
	def __init__(self, title, jsp, jnt_pub):
		wx.Frame.__init__(self, None, -1, title, (-1, -1));
		self.jsp = jsp
		self.jnt_pub = jnt_pub
		self.joint_map = {}
		panel = wx.Panel(self, wx.ID_ANY);
		box = wx.BoxSizer(wx.VERTICAL)
		font = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD)

		### Sliders ###
		#print "Joint list: ", self.jsp.joint_list
		for name in self.jsp.joint_list:
			if name not in self.jsp.free_joints:
				continue
			joint = self.jsp.free_joints[name]

			if joint['min'] == joint['max']:
				continue

			row = wx.GridSizer(1,2)
			label = wx.StaticText(panel, -1, name)
			label.SetFont(font)
			row.Add(label, 1, wx.ALIGN_CENTER_VERTICAL)

			display = wx.TextCtrl (panel, value=str(0),
						style=wx.TE_READONLY | wx.ALIGN_RIGHT)

			row.Add(display, flag= wx.ALIGN_RIGHT| wx.ALIGN_CENTER_VERTICAL)
			box.Add(row, 1, wx.EXPAND)
			slider = wx.Slider(panel, -1, RANGE/2, 0, RANGE,
						style= wx.SL_AUTOTICKS | wx.SL_HORIZONTAL)
			slider.SetFont(font)
			box.Add(slider, 1, wx.EXPAND)

			self.joint_map[name] = {'slidervalue':0, 'display':display,
									'slider':slider, 'joint':joint}

		self.UpdateSlidersEvent, self.EVT_UPDATESLIDERS = wx.lib.newevent.NewEvent()
		self.Bind(self.EVT_UPDATESLIDERS, self.updateSliders)

		# Buttons
		self.close_button = wx.Button(panel, 1, 'Close Hand')
		self.open_button = wx.Button(panel, 2, 'Open Hand')

		wx.EVT_BUTTON(self, 1, self.close_hand_cb)
		wx.EVT_BUTTON(self, 2, self.open_hand_cb)

		box.Add(self.close_button, 0, wx.EXPAND)
		box.Add(self.open_button, 1, wx.EXPAND)

		self.Bind(wx.EVT_SLIDER, self.sliderUpdate)
		panel.SetSizer(box)
		box.Fit(self)
		self.update_values()
		self.grasp_slider_val = self.get_grasp_slider_val() 

	def close_hand_cb(self, click):
		rospy.loginfo("Closing hand.")
		self.joint_map['Finger 1']['joint']['position'] = 2.5
		self.joint_map['Finger 2']['joint']['position'] = 2.5
		self.joint_map['Finger 3']['joint']['position'] = 2.5
	
		self.update_sliders()
		#self.sliderUpdate(None)

	def open_hand_cb(self, click):
		rospy.loginfo("Opening hand.")
		for (name, joint_info) in self.joint_map.items():
			joint_info['joint']['position'] = 0
	
		self.update_sliders()
		#self.sliderUpdate(None)

	def get_grasp_slider_val(self):
		return self.joint_map['Grasp Level']['slider'].GetValue()

	def update_values(self):
		for (name,joint_info) in self.joint_map.items():
			purevalue = joint_info['slidervalue']
			joint = joint_info['joint']
			value = self.sliderToValue(purevalue, joint)
			joint['position'] = value
		self.update_sliders()

	def updateSliders(self, event):
		self.update_sliders()

	def update_sliders(self):
		for (name,joint_info) in self.joint_map.items():
			joint = joint_info['joint']
			joint_info['slidervalue'] = self.valueToSlider(joint['position'],
														   joint)
			joint_info['slider'].SetValue(joint_info['slidervalue'])
			joint_info['display'].SetValue("%.2f"%joint['position'])

	
	def sliderUpdate(self, event):
		#print "sliderUpdate() called."
		# Set slider values if the overall grasp slider was moved
		grasp_slider_val = self.get_grasp_slider_val() 
		if self.grasp_slider_val != grasp_slider_val:
			self.grasp_slider_val = grasp_slider_val
			self.joint_map['Finger 1']['slidervalue'] = grasp_slider_val
			self.joint_map['Finger 2']['slidervalue'] = grasp_slider_val
			self.joint_map['Finger 3']['slidervalue'] = grasp_slider_val
			self.joint_map['Grasp Level']['slidervalue'] = grasp_slider_val
			#self.update_sliders()
		else:
			# Get slider values and publish
			for (name,joint_info) in self.joint_map.items():
					joint_info['slidervalue'] = joint_info['slider'].GetValue()
		
		self.update_values()
		self.jnt_pub.publish_jnts(self.joint_map)

	def valueToSlider(self, value, joint):
		return (value - joint['min']) * float(RANGE) / (joint['max'] - joint['min'])

	def sliderToValue(self, slider, joint):
		pctvalue = slider / float(RANGE)
		return joint['min'] + (joint['max']-joint['min']) * pctvalue


class JointPub:
	def __init__(self, jnts):
		joint_pub_topic = get_param("joint_pub_topic", "/bhand/hand_cmd")
		print "Creating joint command publisher."
		self.close_hand_pub = rospy.Publisher("/bhand/close_grasp", Empty, queue_size=1)
		self.open_hand_pub = rospy.Publisher("/bhand/open_grasp", Empty, queue_size=1)
		self.joint_pub = rospy.Publisher(joint_pub_topic, HandCommand, queue_size=1)
		self.hand_command_template = HandCommand()
		#self.joint_state_template = JointState()
		#self.joint_state_template.header.stamp = rospy.Time.now()
		#self.joint_state_template.name = jnts.joint_list
		#self.joint_state_template.position = [0.0] * len(jnts.joint_list)
		#self.joint_state_template.velocity = [0.0] * len(jnts.joint_list)
		#self.joint_state_template.effort = [0.0] * len(jnts.joint_list)

	def publish_jnts(self, joint_map):
		#for idx, name in enumerate(self.joint_state_template.name):
		#	self.joint_state_template.position[idx] = joint_map[name]['joint']['position']
		self.hand_command_template.header.stamp = rospy.Time.now()
		self.hand_command_template.f1 = joint_map['Finger 1']['joint']['position']
		self.hand_command_template.f2 = joint_map['Finger 2']['joint']['position']
		self.hand_command_template.f3 = joint_map['Finger 3']['joint']['position']
		
		self.hand_command_template.spread = joint_map['Spread']['joint']['position']
		rospy.loginfo("Publishing hand command.")
		self.joint_pub.publish(self.hand_command_template)

	def open_hand(self):
		self.open_hand_pub.publish(Empty())
	
	def close_hand(self):
		self.close_hand_pub.publish(Empty())

if __name__ == "__main__":
	# app = wx.App()
	# gui = HandCommandGui("BH280 Hand Control", jnts, jnt_pub)
	# gui.Show()
	# app.MainLoop()
	app = wx.App()
	gui = Tester(app)
	gui.Show()
	app.MainLoop()