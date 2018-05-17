from WineGlassInterpData import WineGlassInterpData, readRosBag, InterpHandPositions, readTextCapturedGrasps, object_transforms, readRosBags, InterpData
from NearContactStudy import ColorsDict
from openravepy import *
from Utils import UtilTransforms
import numpy as np
import matplotlib.pyplot as plt
import pdb


camera_transform = np.array([[ 0.99669282, -0.08057594,  0.01053303, -0.09467104],
       [-0.02533629, -0.18497678,  0.98241624,  0.23782513],
       [-0.07721074, -0.97943408, -0.18640652,  0.37024531],
       [ 0.        ,  0.        ,  0.        ,  1.        ]])


W = WineGlassInterpData(fns=['Trial3/grasp1.bag', 'Trial3/grasp2.bag', 'Trial3/grasp3.bag'])
I = InterpHandPositions(W)

# W.data.showRGB()
# I.loadGrasp(0)
I.alignToManualTransform(object_transforms['grasp2'])
# I.saveInterpData('Trial3/InterpData1', 0, 2, object_transforms['grasp2'])
# I.initializeNewHand()
# I.interpolateHandPositions(0,1)

I.A.hide()
# I.O.changeColor(ColorsDict.colors['greenI'], [0,50,0])
I.O.changeColor(ColorsDict.colors['greenI'], 0.5)

# I.H1.show()
# I.H1.changeColor(ColorsDict.colors['blueI'])
# I.H1.moveToMakeValidGrasp2(body=I.O.obj)
# I.H1.hide()

# I.H2.show()
# I.H2.changeColor(ColorsDict.colors['blueI'])
# I.H2.moveToMakeValidGrasp2(body=I.O.obj)
# I.H2.hide()

for p in np.linspace(0,1,11):
	goalT, goal_hand_JA = I.interpolateHandPositions(0,2, prcnt = p)
	I.H2.hide()
	I.H1.hide()
	I.center_pt.SetVisible(False)
	I.G.hide()

	I.V.viewer.SetCamera(camera_transform)

	I.H.show()
	I.H.changeColor(ColorsDict.colors['blueI'])
	I.H.moveToMakeValidGrasp2(body=I.O.obj)
	c = I.H.getContact(body = I.O.obj)
	# pdb.set_trace()
	I.V.clearPoints()
	I.H.markContacts(c, pointsize=0.01)
	I.V.takeImage('Transparent_Interpolate_%s.png' %(int(p*10)))
	I.H.hide()
