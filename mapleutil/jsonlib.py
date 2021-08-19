import json
import redbot
from pathlib import Path

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
	f = Path(jsonPath)
	f.touch(exist_ok=True)
	with open(jsonPath, 'r') as jsonFile:
		data = json.load(jsonFile)
	return data

def assignChar(data, author,char,region):
	if not "personalCharacters" in data:
		data["personalCharacters"]={}
	data["personalCharacters"][author]={}
	data["personalCharacters"][author]["name"]=char
	data["personalCharacters"][author]["region"]=1 if region.lower()=="eu" else 0
	updateJson(data)

def getPersonalChar(data,author):
	if (not "personalCharacters" in data) or (not author in data["personalCharacters"]):
		return None
	return data["personalCharacters"][author]
	