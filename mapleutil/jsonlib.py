import json
from . import scrapelib

data = {}
def initiateBot():
	try:
		with open('rankData.json') as jsonFile:
			global data
			data = json.load(jsonFile)
	except:
		open('rankData.json', 'w') 

def addChar(server,char,eu):
	delChar(server,char,eu)
	if not server in data:
		data[server]=[]
	data[server].append((char,eu))
	updateJson()
	return True

def delChar(server,char,eu):
	if not server in data:
		return False
	data[server]= [x for x in data[server] if x[0]!=char or x[1]!=eu]
	updateJson()
	return True

def updateJson():
	with open("rankData.json", "w") as jsonFile:
		json.dump(data, jsonFile)
		
def generateLeaderboard(server):
	leaderboard = []
	for char in data[server]:
		exp=scrapelib.fetchCharExp(char[0],char[1])
		leaderboard.append({'name':char[0],'eu':char[1],'level':exp[0],'exp':exp[1] })
	leaderboard.sort(key = lambda x: (x['level'],x['exp']),reverse=1)
	return leaderboard

def formatLeaderboard(leaderboard):
	return '\n'.join('{name} - Level: {level} Exp: {exp}'.format(**x) for x in leaderboard)
