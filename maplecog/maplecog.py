from redbot.core import commands
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from functools import reduce


def __init__(self, bot):
    self.bot = bot

def scrape():
    url = findLatestPatchNotes()
    if not url:
        return 0
    site = requests.get(url)
    times = []
    soup = BeautifulSoup(site.text, 'html.parser').find('div', class_='component component-news-article').find(
        'ul').find_next('p')
    soup = soup.find_next(lambda tag: tag.name == 'span' and '2x EXP & Drop' in tag.text).find_next('p')
    for entry in soup.text.split("UTC:"):
        if entry:
            times.append("UTC:" + entry)
    return times


def findLatestPatchNotes():
    baseURL = 'http://maplestory.nexon.net'
    site = requests.get(baseURL + '/news/update#news-filter')
    soup = BeautifulSoup(site.content, 'html.parser')
    news = soup.find('ul', class_='news-container rows').find_all('div', class_='text')
    for entry in news:
        title = entry.find('a')
        if 'Patch Notes' in title.text:
            return baseURL + title['href']
    return 0


def findCountdown(unparsedData):
    parsedData = parseDatetimeData(unparsedData)
    nearest = reduce(lambda a, b: a if a - datetime.utcnow() < b - datetime.utcnow() else b, parsedData)
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
                "%Y %m %d %H:%M %p"))
    return parsedData


def get2xTimes():
    times = scrape()
    toPrint = ''
    if not times:
        return "No 2x periods were found"
    for entry in times:
        toPrint += entry + "\n"
    countdown = findCountdown(times)
    toPrint += ("The next 2x period is in " + str(countdown).split('.')[0]) if countdown else "All 2x periods have ended(or the last one is currently active"
    return toPrint

def getUrsus2xStatus():
    currentTime = datetime.utcnow()
    if currentTime.hour>10 and currentTime.hour<22:
        endTime = currentTime.replace(hour=22,minute=0,second=0)
        return "Ursus 2x meso time is currently active, it will end in "+str(endTime-currentTime).split('.')[0]
    startTime = currentTime.replace(hour=10,minute=0,second=0)
    return  "Ursus 2x meso time is not active, it will start in "\
            +(str(startTime)-currentTime).split('.')[0] if startTime-currentTime>timedelta(0) else str(startTime + timedelta(days=1) - currentTime.split('.')[0])


class mapleCog(commands.Cog):

    @commands.command()
    async def next2x(self, ctx):
        """Finds the latest 2x post"""
        toPrint = get2xTimes()
        await self.bot.say(toPrint)

    @commands.command()
    async def patchnotes(self, ctx):
        """Finds the latest patch notes"""
        toPrint = findLatestPatchNotes()
        if not toPrint:
            toPrint = "No patch notes were found."
        await self.bot.say(toPrint)

    @commands.command()
    async def ursus(self, ctx):
        """sends info about current ursus 2x meso status"""
        toPrint = getUrsus2xStatus()
        await self.bot.say(toPrint)
