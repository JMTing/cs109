'''
# Cleans the swimmer's data from USA swimming
#
# Jason Ting
# CS 109 Final Project
# Fall, 2013
'''

import pandas as pd
import numpy as np

# converts the time into seconds
def getSec(time):
	if ':' in time:
		l = time.split(':')
		return int(l[0]) * 60 + float(l[1])
	else:
		return float(time)

# loads in the results to pandas and add column names
df = pd.read_csv("results_clean.txt", header=None, delimiter = '\t', error_bad_lines = False)
df.columns = ('Name','Team','Year','School','Event','Course','Age','Time1','Time2','Power Points','Standard','Meet','LSC','Club','Date')

# cleans time into seconds
df['Time2'] = df['Time2'].apply(lambda x: getSec(x))

print df['Time2']
