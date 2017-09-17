from NearContactStudy import SurveyParser as SP
import pdb
import csv
import os
from pprint import pprint

class QSFGen(object):
	def __init__(self):
		self.SP = SP()
		self.firstMapWrite = True

	def QuestionGen(self, fn):
		with open(fn, 'rb') as csvfile:
			reader = csv.reader(csvfile)
			for row in reader:
				row.pop(0)
				yield row

	def fillSurvey(self, qsf_out_fn, question_fn = 'AllQuestions.csv', mapper_fn = 'Mapper.csv'):
		gen = self.QuestionGen(question_fn)
		self.SP.changeSurveyName(self.SP.survey_in, name = 'WithFileNames')
		for qs in gen:
			qs.insert(3,'None') #this makes None the weird answer at the bottom, should also have other questions in intended grid format
			num_of_opts = len(qs)
			quest, block, flow = self.SP.createMultiChoiceQuest(num_opts = num_of_opts, opts = qs)
			QID_str, export_ID = self.SP.addQuestion(quest, block, flow, self.SP.survey_in, randomizer = True)
			qs.insert(0,export_ID)
			qs.insert(0,QID_str)
			self.writeMapper(mapper_fn, qs)
		self.SP.writeJSON(qsf_out_fn, self.SP.survey_in)

	def writeMapper(self, map_fn, row):
		#writes mapping from QID to options (fields should be in order because it is a list)
		if self.firstMapWrite:
			try:
				os.remove(map_fn)
			except:
				pass
			self.firstMapWrite = False
		with open(map_fn, 'ab') as csvfile:
			writer = csv.writer(csvfile)
			writer.writerow(row)

if __name__ == '__main__':
	Q = QSFGen()
	Q.SP.loadBaseSurvey('/home/ammar/Documents/Projects/NearContactStudy/NearContact20Survey/QualtricsGeneration/QualtricsGen/RefinementSurvey-Base.qsf')
	Q.SP.setQCountToBeAsked(25, Q.SP.survey_in)
	Q.fillSurvey('RefinementSurveyFilled.qsf', question_fn = 'AllQuestions.csv')
	pdb.set_trace()
