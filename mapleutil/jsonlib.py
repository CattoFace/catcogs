import json
from . import scrapelib
#from scrapelib import *

def addChar(data,server,char,eu):
	delChar(data,server,char,eu)
	if not server in data:
		data[server]=[]
	data[server].append((char,eu))
	saveRankingData(data)
	return True

def delChar(data,server,char,eu):
	if not server in data:
		return False
	data[server]= [x for x in data[server] if x[0]!=char or x[1]!=eu]
	saveRankingData(data)
	return True
		
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


