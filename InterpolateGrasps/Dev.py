import sys
import pdb
from DataTester import *

class Dev():
	def __init__(self):
		print("Dev Started")

	def myreload(self):
		del sys.modules['DataTester']
		from DataTester import *
		global V, Hand, Obj
		V = Vis()
		Obj = ObjectVis(V)
		Hand = HandVis(V)
		print("Reloaded Module")



if __name__ == '__main__':
	D = Dev()
	D.myreload()