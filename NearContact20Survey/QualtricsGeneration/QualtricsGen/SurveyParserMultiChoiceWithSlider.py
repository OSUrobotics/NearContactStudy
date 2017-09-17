import json
from pprint import pprint
import pdb
import copy
from collections import OrderedDict
import random, string
import numpy as np
from NearContactStudy import SurveyParser, multi_choice, blockelement, flowelement, randomizerelement, LM_temp


SLIDER_QUESTION = {u'Element': u'SQ',
					u'Payload': 
						{u'ChoiceOrder': [],
						u'Choices': [],
						u'Configuration': 
							{u'CSSliderMax': 100,
							u'CSSliderMin': 0,
							u'CustomStart': False,
							u'GridLines': 10,
							u'MobileFirst': True,
							u'NotApplicable': False,
							u'NumDecimals': u'0',
							u'QuestionDescriptionOption': u'UseText',
							u'ShowValue': True,
							u'SnapToGrid': False
							},
						u'DataExportTag': u'Q6',
						u'DefaultChoices': False,
						u'DynamicChoices': 
							{u'DynamicType': u'ChoiceGroup',
							u'Locator': u'q://QID1/ChoiceGroup/SelectedChoices',
							u'Type': u'Dynamic'
							},
						u'DynamicChoicesData': [],
						u'GradingData': [],
						u'Labels': [],
						u'Language': [],
						u'QuestionDescription': u'Click to write the question text',
						u'QuestionID': u'QID5',
						u'QuestionText': u'Click to write the question text',
						u'QuestionType': u'Slider',
						u'Selector': u'HSLIDER',
						u'Validation': 
							{u'Settings': 
								{u'ForceResponse': u'OFF',
								u'ForceResponseType': u'ON',
								u'Type': u'None'
								}
							}
						},
					u'PrimaryAttribute': u'QID5',
					u'SecondaryAttribute': u'Click to write the question text',
					u'SurveyID': u'SV_6uotxyaL1nZukqV',
					u'TertiaryAttribute': None
					}

MULTICHOICE_SLIDER_BLOCK_ELEMENT= {u'BlockElements': 
										[{u'QuestionID': u'QID1', u'Type': u'Question'},
									  	{u'QuestionID': u'QID5', u'Type': u'Question'}
									  	],
									u'Description': u'BlockName2',
									u'ID': u'BL_6sWJKDNdI0GUkZv',
									u'Options': 
										{u'BlockLocking': u'false',
									  	u'Looping': u'Static',
									  	u'LoopingOptions': 
									  		{u'Randomization': u'None',
									   		u'Static': 
									   			{u'1': 
									   				{u'1': u'',
									   				 u'2': u'', 
									   				 u'3': u'', 
									   				 u'4': u''},
												u'2': 
													{u'1': u'', 
													u'2': u'', 
													u'3': u'', 
													u'4': u''}
												}
											},
											u'RandomizeQuestions': u'false'
										},
									u'Type': u'Default'
									}




class SurveyParserMultiChoiceWithSlider(SurveyParser):

	def getNextQID(self, json_dict): #get next available QID
		max_count = 0
		if isinstance(json_dict['SurveyElements'][0]['Payload'], dict): #if there are additional layers
			for k,v in json_dict['SurveyElements'][0]['Payload'].iteritems():
				for i in v['BlockElements']:
					next_QID = int(i['QuestionID'].strip('QID'))
					max_count = max(max_count, next_QID)
		elif isinstance(json_dict['SurveyElements'][0]['Payload'], list):
			for E in json_dict['SurveyElements'][0]['Payload']:
				if 'BlockElements' in E.keys():
					for Qs in E['BlockElements']:
						next_QID = int(Qs['QuestionID'].strip('QID'))
						max_count = max(max_count, next_QID)
		else:
			for i in json_dict['SurveyElements'][0]['Payload']:
				try:
					next_QID = int(i['BlockElements'][0]['QuestionID'].strip('QID'))
					max_count = max(max_count, next_QID)
				except:
					pass
		return max_count+1


	def createMultiChoiceSliderQuest(self, num_opts = 3, opts = None):
		# creates a multichoice question
		# followed by sliders that take the answers from the first question and ask for clarification
		# pdb.set_trace()
		new_multi_quest = copy.deepcopy(multi_choice[0])
		new_slider_quest = copy.deepcopy(SLIDER_QUESTION)
		new_block = copy.deepcopy(MULTICHOICE_SLIDER_BLOCK_ELEMENT)
		new_flow = copy.deepcopy(flowelement)


		#insert choices
		new_multi_quest['Payload']['Choices']  = dict()
		new_multi_quest['Payload']['ChoiceOrder'] = []
		for i in range(0, num_opts): #these should be loop merge values
			new_multi_quest['Payload']['Choices'][str(i+1)] = dict({'Display'.encode('ascii', 'ignore'): (LM_temp %str(i+1)).encode('ascii', 'ignore')})
		new_multi_quest['Payload']['ChoiceOrder'] = [(i+1) for i in range(0, num_opts)]
		# new_multi_quest['Payload']['ChoiceOrder'] = ['%s'.encode('ascii', 'ignore') %(i+1) for i in range(0, num_opts+1)]

		#change choices in block
		new_block['Options']['LoopingOptions']['Static'] = {'1':dict()}
		for i in range(0, num_opts):
			new_block['Options']['LoopingOptions']['Static']['1']['%s'.encode('ascii', 'ignore') %(i+1)] = opts[i].encode('ascii', 'ignore')

		#change block name
		new_block['Description'] = 'BlockName-Auto'.encode('ascii', 'ignore')

		#change blockID
		new_block['ID'] = self.genID()

		# add to flow
		new_flow['ID'] = new_block['ID'] #update ID

		return new_multi_quest, new_slider_quest, new_block, new_flow

	def addQuestion(self, quest, sliders, block, flow, json_dict, randomizer = False): #adds question to a qsf file
		#set survey ID
		survey_ID = json_dict['SurveyEntry']['SurveyID']


		#update Question QIDs
		QID1 = self.getNextQID(self.survey_in)
		QID1_str = 'QID%s'.encode('ascii', 'ignore') %QID1
		quest['PrimaryAttribute'] = QID1_str
		quest['Payload']['QuestionID'] = QID1_str
		QID2 = QID1 + 1
		QID2_str = 'QID%s'.encode('ascii', 'ignore') %QID2
		sliders['PrimaryAttribute'] = QID2_str
		sliders['Payload']['QuestionID'] = QID2_str

		#change QID in block
		block['BlockElements'][0]['QuestionID'] = QID1_str
		block['BlockElements'][1]['QuestionID'] = QID2_str

		#change QID in sliders pass through question
		sliders['Payload']['DynamicChoices']['Locator'] = 'q://%s/ChoiceGroup/SelectedChoices'%QID1_str


		#update export ID
		export_ID1 = 'Q%s' %QID1
		export_ID2 = 'Q%s' %QID2
		quest['Payload']['DataExportTag'] = export_ID1
		sliders['Payload']['DataExportTag'] = export_ID2
		json_dict['SurveyElements'].append(quest)
		json_dict['SurveyElements'].append(sliders)
		num_blocks = len(self.survey_in['SurveyElements'][0]['Payload'])
		# block_key = max([int(i) for i in json_dict['SurveyElements'][0]['Payload'][0].keys()] )
		if isinstance(json_dict['SurveyElements'][0]['Payload'], list): #sometimes two blocks appears (maybe because of trashcan?) -- only adds it after the last block
			json_dict['SurveyElements'][0]['Payload'].append(block)
		else:
			keys = json_dict['SurveyElements'][0]['Payload'].keys()
			keys_int = np.array(keys).astype('int')
			block_key = max(keys_int) + 1
			# json_dict['SurveyElements'][0]['Payload'][str(block_key + 1)] = json_dict['SurveyElements'][0]['Payload'][str(block_key)]  #moving the comment box til the very end
			json_dict['SurveyElements'][0]['Payload'][str(block_key)] = block

		# json_dict['SurveyElements'][0]['Payload'][str(block_key)] = block
		flow['FlowID'] = self.getNextFlow(json_dict)
		r_loc = 4 #randomizer location in list
		if randomizer:
			try:
				json_dict['SurveyElements'][1]['Payload']['Flow'][r_loc]['Flow'].append(flow)
			except: #first time the block doesn't even exist!
				randomizer_flow_ID = self.getNextFlow(json_dict)  #### issue with flow ID checker!
				randomizerelement['FlowID'] = randomizer_flow_ID
				json_dict['SurveyElements'][1]['Payload']['Flow'][r_loc] = copy.deepcopy(randomizerelement)
				json_dict['SurveyElements'][1]['Payload']['Flow'][r_loc]['Flow'] = [flow]
		else:
			json_dict['SurveyElements'][1]['Payload']['Flow'].append(flow)
		return QID1_str, export_ID1, QID2_str, export_ID2

if __name__ == '__main__':
	SP = SurveyParserMultiChoiceWithSlider()
	SP.loadBaseSurvey('TEST_-_-------_MultiChoiceSlider.qsf')
	for i1 in range(5):
		multi, slider, block, flow = SP.createMultiChoiceSliderQuest(num_opts = 5, opts = ['option%s' %i for i in range(1,6)])
		SP.addQuestion(multi, slider, block, flow, SP.survey_in, randomizer = True)
	SP.writeJSON('WriteTest.qsf', SP.survey_in)


