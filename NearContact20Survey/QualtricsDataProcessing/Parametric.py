import re
import pdb
import csv
import copy
import numpy as np


class Parametric(object):

	def AnalyzeResultsToCSV(self, file_out = 'ParametricAnalyzedResponses.csv'):
		# slices and dices data into a more readable format (or less)
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
			header.extend(['Average', 'StandardDeviation', 'Count', '']*2) #blank to seperate min from max
			writer.writerow(header)
			for q_key,v_small in self.small_shapedata_stats.iteritems():
				v_large = self.large_shapedata_stats[q_key]
				for dim_key in v_small.keys():
					q_key_split = re.split('[:_]', q_key)
					q_key_split = filter(None, q_key_split) # removes blank
					q_key_split.extend(dim_key.strip()) #random whitespace that needs to be removed
					avg1, std1, ct1 = v_small[dim_key][:]
					avg2, std2, ct2 = v_large[dim_key][:]
					q_key_split.extend([avg1, std1, ct1])
					q_key_split.extend(['']) #blank to seperate min from max
					q_key_split.extend([avg2, std2, ct1])
					writer.writerow(q_key_split)


	def stats(self, arr): # returns simple parametric stats from array
		avg = np.mean(arr).round(2)
		stdev = np.std(arr).round(2)
		ct = len(arr)
		return avg, stdev, ct

	def AnalyzeResults(self, dict_tuple): #analyzes data in arrays so that each question has stats instead of values
		self.small_shapedata = dict_tuple[0]
		self.large_shapedata = dict_tuple[1]
		self.small_shapedata_stats = copy.deepcopy(dict_tuple[0]) #assume small is first
		self.large_shapedata_stats = copy.deepcopy(dict_tuple[1])
		for d in (self.small_shapedata_stats, self.large_shapedata_stats):
			for k1,v1 in d.iteritems():
				for k2, v2 in v1.iteritems():
					d[k1][k2] = self.stats(v2)