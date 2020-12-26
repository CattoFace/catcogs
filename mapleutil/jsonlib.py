import json
from . import scrapelib
import os

def initiateBot():
	data ={}
	scriptDir = os.path.split(os.path.abspath(__file__))[0]
	jsonPath = os.path.join(scriptDir, "rankData.json")
	try:
		with open(jsonPath) as jsonFile:
			data = json.load(jsonFile)
	except:
		open(jsonPath, 'w')
	return data

def addChar(data,server,char,eu):
	delChar(data,server,char,eu)
	if not server in data:
		data[server]=[]
	data[server].append((char,eu))
	updateJson(data)
	return True

def delChar(data,server,char,eu):
	if not server in data:
		return False
	data[server]= [x for x in data[server] if x[0]!=char or x[1]!=eu]
	updateJson(data)
	return True

def updateJson(data):
	scriptDir = os.path.split(os.path.abspath(__file__))[0]
	jsonPath = os.path.join(scriptDir, "rankData.json")
	with open(jsonPath, "w") as jsonFile:
		json.dump(data, jsonFile)
		
def generateLeaderboard(data,server):
	leaderboard = []
	if not server in data:
		return {}
	for char in data[server]:
		exp=scrapelib.fetchCharExp(char[0],char[1])
		leaderboard.append({'name':char[0],'eu':char[1],'level':exp[0],'exp':exp[1] })
	leaderboard.sort(key = lambda x: (x['level'],x['exp']),reverse=1)
	return leaderboard

def formatLeaderboard(leaderboard):
	return '\n'.join('{name} - Level: {level} Exp: {exp}'.format(**x) for x in leaderboard)

