import numpy as np

class ContinuousAnalysis(object):
	def array(self, arr): #map continuously, but clamp max and min values
		dims = [1, 33]
		clamp_range = [10, 90]
		cont_arr = []
		for k in arr:
			if k < clamp_range[0]:
				cont_arr.append(dims[0])
			elif k > clamp_range[1]:
				cont_arr.append(dims[1])
			else:
				cont_arr.append(np.interp(k, clamp_range, dims)) #maps slider value to size value
		cont_arr = np.array(cont_arr)
		return cont_arr