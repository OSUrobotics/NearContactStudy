from NearContactStudy import ShapeSTLGeneratorPython
from NearContactStudy import dataResults, csvReader, removeUnfinishedRows, removeUnnecessaryColumns
from NearContactStudy import ContinuousAnalysis, Nonparametric, PolytopeNonparametric
from NearContactStudy import HAND_PARAM, BASE_PATH
from NearContactStudy import HandCenteredCSV
import matplotlib
import matplotlib.pyplot as plt
import pdb
from PIL import Image
import numpy as np
import csv
import os
from pprint import pprint

RESULTSCSV_PATH = 'NearContact20Survey/QualtricsDataProcessing/Near Contact 2.0 - Initial/Near_Contact_20_Imported.csv'
ANALYZEDRESULTSCSV_PATH = 'NearContact20Survey/QualtricsDataProcessing/%s_NonParamContinuousAnalyzedResponses.csv'
##### Creating Plots for Paper #####
data = dataResults()
reader = csvReader(RESULTSCSV_PATH, data)
reader.readCSV()
removeUnfinishedRows(data)
data.getWorkerIDs()
removeUnnecessaryColumns(data)
#This 3-depth tuple was copy-pasted from fill_in_qsf.py in NearContact20Survey/QualtricsGeneration
questions = (("equidistant_top", (("3 down the sides",(("cylinder_h_","up"), ("ellipse_h_","up"), ("cone_h_","up"))), ("3 around the sides",(("cylinder_e_","angled"), ("cone_e_","90"), ("cube_h_","angled"))),("2 around the sides, 1 on the base",(("cylinder_e_","up"), ("cone_e_","up"), ("cube_h_","up"))))),
						("equidistant_side",(("3 around the sides, palm on flat",(("cylinder_e_","up"), ("cube_h_","down"), ("cone_e_","up"))), ("3 around the sides, palm on round",(("ellipse_h_","up"), ("cylinder_h_","down"), ("cone_h_","90"))),("2 pinch the sides, 1 on the top",(("cylinder_h_","up"), ("cone_h_","up"), ("cube_h_","up"))))),
						("3fingerpinch_top",(("opposite sides",(("cylinder_h_","up"), ("cylinder_w_","up"), ("cube_h_","up"), ("ellipse_h_","up"), ("cone_h_","up"))), ("around the sides",(("cylinder_e_","up"), ("cone_e_","up"), ("cube_h_","angled"))))),
						("3fingerpinch_side",(("around the sides",(("cylinder_h_","up"), ("ellipse_h_","up"), ("cone_h_","up"))), ("end to end",(("cylinder_w_","up"), ("cone_e_","up"), ("cube_h_","up"))))), 
						("hook_side",(("over the top",(("cylinder_h_","up"), ("cylinder_e_","up"), ("cube_h_","up"), ("ellipse_h_","up"))), ("around the sides",(("cylinder_e_","90"), ("cube_h_","90"), ("cylinder_h_","90"), ("ellipse_h_","90"), ("cone_h_","90"))))),
						("2fingerpinch_top",(("2 around the sides",(("ellipse_h_","up"), ("cone_e_","up"), ("cylinder_e_","up"), ("cube_h_","angled"))), ("end to end",(("cylinder_w_","up"), ("cube_h_","up"), ("cone_h_","up"), ("cylinder_h_","up"))))),
						("2fingerpinch_side",(("around the sides",(("cylinder_h_","up"), ("ellipse_h_","up"), ("cone_h_","up"))), ("end to end",(("cylinder_w_","up"), ("cone_e_","up"), ("cube_h_","up"))))))
shapes = ("cone_h_", "cone_e_", "cylinder_h_", "cylinder_w_", "cylinder_e_", "ellipse_h_", "cube_h_")
data.changeCategories(questions)
data.removeWorkers()
data.toArray()
data.RearrangeDictToShapeSpace()
data.small_shapedata = data.CleanDataLess(data.small_shapedata, val_to_pop = 100)
data.large_shapedata = data.CleanDataGreater(data.large_shapedata, val_to_pop = 0)
Analysis = ContinuousAnalysis()
data.small_shapedata = data.mapShapeSpace(data.small_shapedata, Analysis)
data.large_shapedata = data.mapShapeSpace(data.large_shapedata, Analysis)
Stats = Nonparametric()
Surf = PolytopeNonparametric()
CIs = [.5, 0.0001, -0.5]
CI_str = {CI: ST for CI,ST in zip(CIs, ('75', '50', '25'))}
CI_titles = {CI: '%s%% Confidence' %CI_str[CI] for CI in CIs}
##### Table 2 #####
# for CI in CIs:
# 	Stats.AnalyzeResults((data.small_shapedata, data.large_shapedata), P = CI)
# 	pdb.set_trace()
# 	Stats.AnalyzeResultsToCSV(os.path.split(ANALYZEDRESULTSCSV_PATH %CI)[-1])

'''
stats_keys = [i for i in data.data.keys() if 'cube' in i]
CI = 0.5
with open(ANALYZEDRESULTSCSV_PATH %CI, 'rb') as csvfile:
	reader = csv.reader(csvfile)
	headers = next(reader)
	shape_col = headers.index('Shape')
	print_results = lambda x: pprint('%s %s, %s %s \t Median Range: %.2f - %.2f' %(x[0], x[1], x[2], x[5], float(x[6])/HAND_PARAM, float(x[11])/HAND_PARAM))
	for row in reader:
		if row[shape_col].strip() == 'cube':
			if row[0].strip() == '2fingerpinch' and row[2].strip() == 'end to end':
				print_results(row)
			elif row[0].strip() == '3fingerpinch' and row[2].strip() != 'around the sides':
				print_results(row)
			elif row[0].strip() == 'equidistant' and '3 around the sides' in row[2].strip():
				print_results(row)


### Figure of Polytope and Images
key =  ' equidistant_side: 2 pinch the sides, 1 on the top: cube_h_'
# key = data.small_shapedata.keys()[10]
ax = None
for CI in CIs:
	Stats.AnalyzeResults((data.small_shapedata, data.large_shapedata), P = CI)
	Surf.setDicts(Stats.small_shapedata_stats, Stats.large_shapedata_stats)
	data.parametrizeData(Stats.small_shapedata_stats)
	data.parametrizeData(Stats.large_shapedata_stats)
	ax, bound_points = Surf.createPolytopeStats(CI, key, image = False)
	ax.set_title(CI_titles[CI], fontsize = 40)
	ax.tick_params(axis='x', labelsize=25)
	ax.tick_params(axis='y', labelsize=25)
	ax.tick_params(axis='z', labelsize=25)
	ax.set_xlabel('width', fontsize=30)
	ax.xaxis.labelpad = 100
	ax.set_ylabel('height', fontsize=30)
	ax.set_zlabel('extent', fontsize=30)
	ax.figure.savefig('ICRAImages/%s.png' %CI, edgecolor='grey')
# plt.show()
CI = 0.5
	###### Figure of different confidence polytopes with grasp image also
files = ['ICRAImages/%s.png' %CI for CI in CIs]
images = map(Image.open, files)
images_crop = [i.crop((300, 150, i.size[0]-150, i.size[1]-80)) for i in images]
# images_crop = [i.crop((320, 150, i.size[0]-150, i.size[1]-100)) for i in images]
grasp_image_fn = Surf.FNFromKey(key)
grasp_image_fn.replace('GeneratedImagesReduced', 'GeneratedImagesCombined')
grasp_image = Image.open(grasp_image_fn).resize((images_crop[0].size[0], images_crop[0].size[1])).convert("RGBA")
images_np = [np.array(i) for i in images_crop]
images_np.insert(0,np.array(grasp_image))
imgs_comb = Image.fromarray(np.hstack(images_np))
imgs_comb.convert("RGB").save('ICRAImages/ConfidencePolytopes.pdf')


bound_points *= HAND_PARAM
IMAGE_PATH = BASE_PATH + '/ShapeImageGenerator/GeneratedImagesCombined/Grasps'
STL = ShapeSTLGeneratorPython()
HC = HandCenteredCSV(True)
for bp in bound_points:
	bp /= 100.0 # convert to cm
	# generate STL
	stl_name = '%s_h%s_w%s_e%s' %('cube', bp[0].round(2), bp[1].round(2), bp[2].round(2))
	stl_name = stl_name.replace('.', 'D')
	stl_name += '.stl'
	pprint(stl_name)
	STL.ShapeSTLGenerator('cube', float(30.0), stl_name, float(bp[0]), float(bp[1]), float(bp[2]), float(10.0))
	D = HC.HandT('equidistant', stl_name, bp[0], bp[1], bp[2], 'h', 'side', 'up','0')
	D['Joint Angles'] = np.array(D['Joint Angles'].split(',')).astype('float') #change from string to array
	D['Image Save Name'] = D['Image Save Name'].replace('.stl', '')
	HC.SIG.createImageFromParameters(D, obj_path = './')
	pdb.set_trace()
	# create images in openrave
	# file_name += '.png'
'''

###### Figure of 2 polytopes with grasps
CI = .50
Stats.AnalyzeResults((data.small_shapedata, data.large_shapedata), P = CI)
Surf.setDicts(Stats.small_shapedata_stats, Stats.large_shapedata_stats)
data.parametrizeData(Stats.small_shapedata_stats)
data.parametrizeData(Stats.large_shapedata_stats)
files = os.listdir('NearContact20Survey/QualtricsDataProcessing/TwoPolytopes/NonparametricContinuous/')
both_cube = [f for f in files if f.count('cube') == 2]
both_equidistant = [f for f in both_cube if f.count('equidistant') == 2]
top_side = [f for f in both_equidistant if 'equidistant_top' in f  and 'equidistant_side' in f]
# for fn in top_side:
# 	key1 = fn.split('__')[0] + '_'
# 	key2 = fn.split('__')[1].strip('.png').rsplit('_', 1)[0] + '_'
# 	key1_resp = Surf.responsesAsPoints(key1, CI)
# 	key2_resp = Surf.responsesAsPoints(key2, CI)
# 	check1 = Surf.pointsCreatePolytopeCheck(key1_resp)
# 	check2 = Surf.pointsCreatePolytopeCheck(key2_resp)
# 	if check1 and check2:
# 		[pprint('Key: %s' %k) for k in (key1, key2)]
# 		pprint('*'*10)
# 		ax = Surf.createMultiplePolytopeStats(CI, key_list=(key1,key2))
# 		plt.show()
key1 = ' equidistant_top: 3 around the sides: cube_h_'
key2 = ' equidistant_side: 2 pinch the sides, 1 on the top: cube_h_'
ax = Surf.createMultiplePolytopeStats(CI, key_list=(key1,key2))
ax.set_title(CI_titles[CI], fontsize = 40)
ax.tick_params(axis='x', labelsize=25)
ax.tick_params(axis='y', labelsize=25)
ax.tick_params(axis='z', labelsize=25)
ax.set_xlabel('width', fontsize=30)
ax.xaxis.labelpad = 100
ax.set_ylabel('height', fontsize=30)
ax.set_zlabel('extent', fontsize=30)
ax.set_ylabel('width', fontsize=30)
ax.figure.savefig('ICRAImages/TransitionPolytope.png')
grasp_fn = [Surf.FNFromKey(k) for k in (key1,key2)]
grasp_images = [Image.open(x) for x in grasp_fn]
grasp_images[0].save('ICRAImages/Key1_grasp.png')
grasp_images[1].save('ICRAImages/Key2_grasp.png')
pdb.set_trace()



# for CI in CIs:
# 	Stats.AnalyzeResults((data.small_shapedata, data.large_shapedata), P = CI)
# 	# Stats.AnalyzeResultsToCSV(file_out = '%sNonParamContinuousAnalyzedResponses.csv' %abs(CI))
# 	Surf.setDicts(Stats.small_shapedata_stats, Stats.large_shapedata_stats)
# 	data.parametrizeData(Stats.small_shapedata_stats)
# 	data.parametrizeData(Stats.large_shapedata_stats)
# 	ax = Surf.createPolytopeStats(CI, key, image = False)
# 	plt.show()
# 	pdb.set_trace()
# 	if not ax: pass # polytope does not exist!
# 	# Surf.createPolytopeStats()
# 	qps = Surf.paramsForNewQuestionsGrid(CI, key)
# 	# Surf.plotQuestionPoints(qps, ax = ax)
# 	# Surf.writePointsToCSV('%s_NonparametricNextQuestions.csv' %CI, qps, CI, key)
# 	Surf.writeAllQuestions('%s_NonparametricNextQuestions.csv' %CI, CI)
# 	# plt.show(block = True)
# 	# pdb.set_trace()
# 	# data.createPolytopeStatsAllNonparametric(CI_amount = 0.5 + CI/2.0)
# # data.createMultiplePolytopeStatsAll()