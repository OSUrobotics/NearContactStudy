from WineGlassInterpData import WineGlassInterpData, readRosBag, InterpHandPositions, readTextCapturedGrasps, object_transforms, readRosBags
from openravepy import *
from Utils import UtilTransforms
import numpy as np
import matplotlib.pyplot as plt
import pdb
# W = WineGlassInterpData(fns=['grasp1.bag', 'grasp2.bag', 'grasp3.bag'])
# W = WineGlassInterpData(fns=['Trial2/test1.bag', 'Trial2/test2.bag', 'Trial2/test3.bag', 'Trial2/test4.bag', 'Trial2/test5.bag', 'Trial2/test6.bag'])
W = WineGlassInterpData(fns=['Trial3/grasp1.bag', 'Trial3/grasp2.bag', 'Trial3/grasp3.bag'])
I = InterpHandPositions(W)

# W.data.showRGB()
# I.loadGrasp(0)
I.alignToManualTransform(object_transforms['grasp2'])
I.saveInterpData('Trial3/InterpData1', 0, 2, object_transforms['grasp2'])
# I.initializeNewHand()
# I.interpolateHandPositions(0,1)
goalT, goal_hand_JA = I.interpolateHandPositions(0,2)
# pdb.set_trace()
U = UtilTransforms()
I.loadORArm()
I.A_OR.setJointAngles(np.array([-0.73, -1.06,  1.51, -0.87,  0.  , -0.  ,  0.  , -0.  , -0.  ,0.  ,  0.  ]))
traj = I.generateTraj(goalT, goal_hand_JA, I.A_OR.getJointAngles())
traj_lift = I.generateTraj(np.matmul(U.TL2T([0,0,0.2]), goalT), goal_hand_JA, traj[-1], reset=False)
traj_putdown = I.generateTraj(goalT, goal_hand_JA, traj_lift[-1], reset=False)
return_traj = traj[::-1]
traj_full = I.A_OR.sequentialCombineTrajectories((traj, traj_lift, traj_putdown, return_traj))
I.showTraj(traj_full)
I.saveTraj('Trial3/interpTrajectory', traj_full)
# I.showTraj(traj)
# I.A_OR.generateOperationalSpaceStraightLineTrajectory(I.H.obj.GetTransformPose())



