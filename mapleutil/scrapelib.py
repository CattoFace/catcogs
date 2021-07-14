from bs4 import BeautifulSoup
import re
import requests
from datetime import datetime, timedelta
from functools import reduce
import gc
import json
import random

def fetch(url):
    with requests.session() as s:
        return s.get(url)
    
def scrape(category, targetSections, targetArticles):
    url = fetchUrl(category, targetArticles)
    if not url:
        return 0
    site = fetch(url)
    soup = BeautifulSoup(site.text, 'html.parser').find('div', class_='component component-news-article').find(
        'ul').find_next('p')
    soup = soup.find_next(lambda tag: tag.name == 'span' and any(x in tag.text for x in targetSections))
    return soup.find_next('p') if soup else 0
    
def fetchTimes(soup):
    times = []
    for entry in soup.text.split("UTC:"):
        if entry:
            times.append("UTC:" + entry)
    return times

def fetchChar(charName,eu):
	with requests.session() as s:
		char = s.get('https://maplestory.nexon.net/api/ranking?id=overall&character_name='+charName+('&region=eu' if eu else '')).json()
		return char[0] if char else 0
			     
def fetchCharImg(charName,eu):
	char = fetchChar(charName,eu)
	return char["CharacterImgUrl"] if char else 0

def fetchCharExp(charName,eu):
	data= fetchChar(charName,eu)
	if not data:
		return 0,0
	level = data['Level']
	exp = data['Exp']
	return level,exp
	
def fetchUrl(category, targets):
    baseURL = 'http://maplestory.nexon.net/news/'
    j = json.loads(requests.get("https://nexon.ws/api/news/1180").text)
    j = list(filter(lambda x:x["Category"]==category,j))
    if targets==[]: return baseURL + str(j[0]["Id"])
    for entry in j:
        if any(x in entry["Title"] for x in targets):
            return baseURL + str(entry["Id"])
    return 0


def findCountdown(unparsedData):
    parsedData = parseDatetimeData(unparsedData)
    nearest = reduce(lambda a, b: a if a - datetime.utcnow() < b - datetime.utcnow() and a - datetime.utcnow()>timedelta(0) else b, parsedData)
    return nearest - datetime.utcnow() if nearest - datetime.utcnow() > timedelta(0) else 0


def parseDatetimeData(unparsedData):
    parsedData=[]
    for unparsedEntry in unparsedData:
        parsedDate = findDate(unparsedEntry)
        parsedData = findAllTimes(parsedData, parsedDate, unparsedEntry)
    return parsedData


def findDate(unparsedEntry):
    splitData = unparsedEntry.split(" ")
    relevantData = splitData[1] + " " + splitData[2] + " " + str(datetime.utcnow().year)
    return datetime.strptime(relevantData, "%B %d %Y")


def findAllTimes(parsedData, parsedDate, unparsedEntry):
    data = unparsedEntry[unparsedEntry.index("at ") + 3:]
    data = data.split("and ")
    for entry in data:
        entry = entry[:entry.index(' -')]
        parsedData.append(datetime.strptime(
                str(parsedDate.year) + " " + str(parsedDate.month) + " " + str(parsedDate.day) + " " + entry,
                "%Y %m %d %I:%M %p"))
    return parsedData


def get2xTimes():
    page = scrape('update', ['2x EXP & Drop'], ["Patch Notes"])
    times = 0
    if page:
        times = fetchTimes()
    toPrint = ''
    if not times:
        return "No 2x periods were found"
    for entry in times:
        toPrint += entry + "\n"
    countdown = findCountdown(times)
    toPrint += ("The next 2x period is in " + str(countdown).split('.')[0]) if countdown else "All 2x periods have ended(or the last one is currently active)"
    return toPrint

def getMaintenanceTime():
    url = fetchUrl('maintenance',[])
    if not url:
        return 0
    site = fetch(url)
    soup = BeautifulSoup(site.text, 'html.parser').find('div', class_='article-content').find_next('p')
    while soup.text=="": soup=soup.find_next('p')
    return soup.text

def getUrsus2xStatus():
    summer = True
    response = f"Ursus 2x meso time is active between <t:1626213600:t> and {'<t:1626228000:t>' if summer else '<t:1626220800:t>'} and between <t:1626274800:t> and {'<t:1626289200:t>' if summer else '<t:1626238800:t>'}\n"
    currentTime = datetime.utcnow()
    isActive = 0
    checkTime = currentTime.replace(hour=1,minute=0,second=0)+timedelta(days=1)
    if currentTime.hour<1:
        isActive = 0
        checkTime = currentTime.replace(hour=1,minute=0,second=0)
    elif currentTime.hour<5:
        isActive = 1
        checkTime = currentTime.replace(hour=5,minute=0,second=0)
    elif currentTime.hour<18:
        isActive = 0
        checkTime = currentTime.replace(hour=18,minute=0,second=0)
    elif currentTime.hour<22:
        isActive = 1
        checkTime = currentTime.replace(hour=22,minute=0,second=0)
    if isActive:
        response+="Ursus 2x meso time is currently active, it will end in "
    else:
        response+="Ursus 2x meso time is not active, it will start in "
    return response + str(checkTime-currentTime).split('.')[0]

def getResetTimes():
    currentTime = datetime.utcnow()
    toPrint = currentTime.strftime("Maple time is currently %H:%M:%S %d-%m-%y")+"\n"
    toPrint += f"Daily reset will happen <t:{datetime.utcfromtimestamp(currentTime.replace(hour=0,minute=0,second=0)+timedelta(1)-currentTime)}:R>\n"
    toPrint += f"Weekly Boss reset will happen <t:{datetime.utcfromtimestamp(hour=0,minute=0,second=0)+timedelta(3-currentTime.weekday() if currentTime.weekday()<=2 else 10-currentTime.weekday())-currentTime)}:R>\n"
    toPrint += f"Dojo/Weekly Quests/Guild Potions reset will happen <t:{datetime.utcfromtimestamp(hour=0,minute=0,second=0)+timedelta(7-currentTime.weekday())-currentTime)}:R>\n"
    return toPrint

def downloadRankingData():
	API_ENDPOINT = "https://json.psty.io/api_v1/stores/rankingData"
	headers = { 'Api-Key': "544fa888-293e-4d4e-be20-8682153a1461"}
	data = requests.get(API_ENDPOINT,headers=headers)
	return data.json()['data']
	
def saveRankingData(data):
	API_ENDPOINT = "https://json.psty.io/api_v1/stores/rankingData"
	headers = { 'Api-Key': "544fa888-293e-4d4e-be20-8682153a1461", 'Content-Type': 'application/json'}
	data = requests.put(API_ENDPOINT,headers=headers,data=json.dumps(data))