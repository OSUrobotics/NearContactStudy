import csv
import re
from NearContactStudy import BASE_PATH

QUESTIONMAPPER_PATH = BASE_PATH + '/NearContact20Survey/QualtricsDataProcessing/QuestionMapper.csv'

class KeyMapper(object):

	def map(self, key): #changes key from one naming convention to the other?
		key_split = re.split('[:_]', key)
		key_split = filter(None, key_split) # removes blank
		with open(QUESTIONMAPPER_PATH, 'rb') as csvfile:
			reader = csv.reader(csvfile)
			for row in reader:
				if row[0] != key_split[0].strip(): #grasp
					continue
				if row[1] != key_split[1].strip(): #approach
					continue
				if row[2] != key_split[3].strip(): #shape
					continue
				if row[3] != key_split[-1].strip(): #obj orientation
					continue
				if row[5] != key_split[2].strip(): #vicky grasp name
					continue
				break
			else:
				print('No Match Found')
				return
		key_return = [row[2], 17, 17, 17, row[3],  row[0], row[1],row[4]]
		if row[2] == 'cone': key_return.insert(4, 10)
		return key_return