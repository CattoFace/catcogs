import json
from . import scrapelib
import redbot
#from scrapelib import *

jsonPath = 	str(redbot.core.data_manager.cog_data_path(raw_name='mapleUtil'))+'/rankData.py'

def initiateBot():
	return loadJson()

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
	data[server]= [x for x in data[server] if x[0].lower()!=char.lower() or x[1]!=eu]
	updateJson(data)
	return True

def updateJson(data):
	with open(jsonPath, "w") as jsonFile:
		json.dump(data, jsonFile)

def loadJson():
	with open(jsonPath, 'r') as jsonFile:
		data = json.load(jsonFile)
	return data

def generateLeaderboard(data,server):
	leaderboard = []
	if not server in data:
		return {}
	for char in data[server]:
		exp=scrapelib.fetchCharExp(char[0],char[1])
		leaderboard.append({'name':char[0],'region':'EU' if char[1] else 'NA','level':exp[0],'exp':exp[1] })
	leaderboard.sort(key = lambda x: (x['level'],x['exp']),reverse=1)
	for char in leaderboard:
		char['exp']= 0 if char['exp']=='0' else f"{char['exp']:,}"
	return leaderboard

def formatLeaderboard(leaderboard):
	return '\n'.join('{name} - Region: {region} Level: {level} Exp: {exp}'.format(**x) for x in leaderboard)

