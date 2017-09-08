import numpy as np

class DiscreteAnalysis(object):
	def array(self, arr): #discretize a set of values
		dims = [1, 9, 17, 25, 33]
		d_range = [20, 40, 60, 80, 100]
		disc_arr = []
		for k in arr:
			for i,d in enumerate(d_range):
				if k <= d:
					break
			disc_arr.append(dims[i])
		disc_arr = np.array(disc_arr)
		return disc_arr