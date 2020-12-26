import json
from . import scrapelib
#from scrapelib import *
def initiateBot():
	return scrapelib.downloadRankingData()
	#try:
	#	with open(jsonPath) as jsonFile:
	#		data = json.load(jsonFile)
	#except:
	#	open(jsonPath, 'w')
	#return data

def addChar(data,server,char,eu):
	delChar(data,server,char,eu)
	if not server in data:
		data[server]=[]
	data[server].append((char,eu))
	scrapelib.saveRankingData(data)	
	#updateJson(data)
	return True

def delChar(data,server,char,eu):
	if not server in data:
		return False
	data[server]= [x for x in data[server] if x[0]!=char or x[1]!=eu]
	scrapelib.saveRankingData(data)
	#updateJson(data)
	return True

def updateJson(data):
	jsonPath = 	str(redbot.core.data_manager.cog_data_path(raw_name='mapleUtil'))+'/rankData.py'
	with open(jsonPath, "w") as jsonFile:
		json.dump(data, jsonFile)
		
def generateLeaderboard(data,server):
	leaderboard = []
	if not server in data:
		return {}
	for char in data[server]:
		exp=scrapelib.fetchCharExp(char[0],char[1])
		leaderboard.append({'name':char[0],'region':'EU' if char[1] else 'NA','level':exp[0],'exp':exp[1] })
	leaderboard.sort(key = lambda x: (x['level'],x['exp']),reverse=1)
	for char in leaderboard:
		char['exp']= f"{char['exp']:,}" if char['exp']=='0' else 0
	return leaderboard

def formatLeaderboard(leaderboard):
	return '\n'.join('{name} - Region: {region} Level: {level} Exp: {exp}'.format(**x) for x in leaderboard)

