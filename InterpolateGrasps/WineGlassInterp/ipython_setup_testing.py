from WineGlassInterpData import WineGlassInterpData, readRosBag, InterpHandPositions, readTextCapturedGrasps, object_transforms, readRosBags
from openravepy import *
import numpy as np
import matplotlib.pyplot as plt
# W = WineGlassInterpData(fns=['grasp1.bag', 'grasp2.bag', 'grasp3.bag'])
# W = WineGlassInterpData(fns=['Trial2/test1.bag', 'Trial2/test2.bag', 'Trial2/test3.bag', 'Trial2/test4.bag', 'Trial2/test5.bag', 'Trial2/test6.bag'])
W = WineGlassInterpData(fns=['Trial3/grasp1.bag', 'Trial3/grasp2.bag', 'Trial3/grasp3.bag'])
I = InterpHandPositions(W)
# W.data.showRGB()
# I.loadGrasp(0)
I.alignToManualTransform(object_transforms['grasp2'])
# I.initializeNewHand()
# I.interpolateHandPositions(0,1)
I.interpolateHandPositions(0,2)
sols_all = [I.A_OR.ikmodel.manip.FindIKSolutions(I.H.getGlobalTransformation(), i) for i in range(32)]



