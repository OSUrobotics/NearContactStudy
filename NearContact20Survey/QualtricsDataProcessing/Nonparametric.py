import re
import pdb
import csv
import copy
import numpy as np
import scipy.stats as st

class Nonparametric(object):

	def AnalyzeResultsToCSV(self, file_out = 'NonparametricAnalyzedResponse.csv'):
		#slices and dices data into a more readable format (or less)
		# assumes data has been converted from string into arrays
		with open(file_out, 'wb') as csvfile:
			writer = csv.writer(csvfile)
			header = ['Grasp Type', \
						'Approach', \
						'Hand Orientation', \
						'Shape', \
						'Shape Orientation', \
						'Changing Dimension',\
						]
			header.extend(['Average', 'Min Interval', 'Max Interval', 'Count', '']*2) #blank to seperate min from max
			writer.writerow(header)
			for q_key,v_small in self.small_shapedata_stats.iteritems():
				v_large = self.large_shapedata_stats[q_key]
				for dim_key in v_small.keys():
					# print('Small values: %s' %(v_small[dim_key]))
					q_key_split = re.split('[:_]', q_key)
					q_key_split = filter(None, q_key_split) # removes blank
					q_key_split.extend(dim_key.strip()) #random whitespace that needs to be removed
					avg1, rmin1, rmax1, ct1 = v_small[dim_key][:]
					avg2, rmin2, rmax2, ct2 = v_large[dim_key][:]
					q_key_split.extend([avg1, rmin1, rmax1, ct1])
					q_key_split.extend(['']) #blank to seperate min from max
					q_key_split.extend([avg2, rmin2, rmax2, ct1])
					writer.writerow(q_key_split)

	def stats(self, arr, P): # returns simple parametric stats from array
		sorted_arr = np.sort(arr)
		weights = np.ones(len(sorted_arr))/len(sorted_arr) #all weights the same and normalized
		new_arr = []
		new_weights = []
		for v,w in zip(sorted_arr, weights):
			if v in new_arr:
				new_weights[-1] += w
			else:
				new_arr.append(v)
				new_weights.append(w)
		dist = st.rv_discrete(values = (new_arr, new_weights))
		# fig, ax = plt.subplots(1,1)
		# ax.plot(new_arr, dist.pmf(new_arr), 'ro', ms=12, mec='r')
		# ax.vlines(new_arr, 0, dist.pmf(new_arr), colors='r', lw=4)
		# plt.show()
		CI = dist.interval(P)
		# print('Median: %s, Interval: (%s, %s)' %(dist.median(), CI[0], CI[1]))
		CI_range = abs(CI[0] - CI[1])
		ct = len(arr)
		return dist.median(), CI[0], CI[1], ct
		# pdb.set_trace()


	def AnalyzeResults(self, dict_tuple, P = 0): #analyzes data in arrays so that each question has stats instead of values
		self.small_shapedata = dict_tuple[0]
		self.large_shapedata = dict_tuple[1]
		self.small_shapedata_stats = copy.deepcopy(dict_tuple[0]) #assume small is first
		self.large_shapedata_stats = copy.deepcopy(dict_tuple[1])
		P = abs(P)
		for d in (self.small_shapedata_stats, self.large_shapedata_stats):
			for k1,v1 in d.iteritems():
				for k2, v2 in v1.iteritems():
					d[k1][k2] = self.stats(v2, P)