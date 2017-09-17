import pdb
import csv
import os
from pprint import pprint
import copy
from NearContactStudy import BASE_PATH

class SurveyResultsParser(object):
	def __init__(self):
		i = 1

	def loadResults(self, results_csv, map_csv):
		#loads results file and parses it in some way
		LM_results = dict()
		with open(results_csv, 'rb') as csvfile:
			reader = csv.reader(csvfile)
			headers = next(reader)
			first_row = next(reader)
			data = [row for row in reader]
			for i, (LM_ID, LM_Val) in enumerate(zip(headers, first_row)):
				if 'ResponseID' in LM_Val:
					LM_results['ResponseID'] = [data[k][i] for k in range(len(data))]

				if '_' not in LM_ID:
					continue
				#check if there is a dictionary there.
				#if there is add key
				#if not create dictionary and add key
				QID = LM_ID.split('_')[0]
				Q_order = int(LM_ID.split('_')[-1].split('(')[0])
				LM = int(LM_Val.split('/')[-1].strip('}'))
				rs = [data[k][i] for k in range(len(data))]
				try:
					LM_results[QID][LM] = rs
				except:
					LM_results[QID] = {LM: rs}

		#replaces loop and merge values with their corresponding mapping
		map_results = copy.deepcopy(LM_results)
		with open(map_csv, 'rb') as mapcsv:
			reader_map = csv.reader(mapcsv)
			for row in reader_map:
				QID = row[1]
				for LM_indx, map_val in enumerate(row[2:], start = 1):
					map_results[QID][map_val] = map_results[QID].pop(LM_indx) 
		return map_results



if __name__ == '__main__':
	R = SurveyResultsParser()
	map = R.loadResults('RefinementSurveyFilled.csv', map_csv = BASE_PATH + '/NearContact20Survey/QualtricsGeneration/Near Contact 2.0 - Refinement/Mapper.csv')