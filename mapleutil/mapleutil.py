import discord
from bs4 import BeautifulSoup
import re
import requests
from datetime import datetime, timedelta
from functools import reduce
import gc
from redbot.core import commands

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


def fetchUrl(category, targets):
    baseURL = 'http://maplestory.nexon.net'
    site = fetch(baseURL + '/news/'+category)
    soup = BeautifulSoup(site.content, 'html.parser')
    news = soup.find('ul', class_='news-container rows').find_all('div', class_='text')
    for entry in news:
        title = entry.find('a')
        if any(x in title.text for x in targets):
            return baseURL + title['href']
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
    url = fetchUrl('maintenance',['Scheduled', 'Unscheduled'])
    if not url:
        return 0
    site = fetch(url)
    soup = BeautifulSoup(site.text, 'html.parser').find('div', class_='article-content').find_next('p')
    return soup.text

def getUrsus2xStatus():
    currentTime = datetime.utcnow()
    if currentTime.hour>=10 and currentTime.hour<22:
        endTime = currentTime.replace(hour=22,minute=0,second=0)
        return "Ursus 2x meso time is active between 10 AM and 10 PM UTC\nUrsus 2x meso time is currently active, it will end in "+str(endTime-currentTime).split('.')[0]
    startTime = currentTime.replace(hour=10,minute=0,second=0)
    return  "Ursus 2x meso time is active between 10 AM and 10 PM UTC\nUrsus 2x meso time is not active, it will start in "\
            +(str(startTime-currentTime).split('.')[0] if currentTime.hour<10 else str(startTime + timedelta(days=1) - currentTime).split('.')[0])

def generateEmbed(name, content):
        embed = discord.Embed(color=discord.Color.orange(), description=content, title="**"+name+"**")
        return embed

def getResetTimes():
    currentTime = datetime.utcnow()
    toPrint = currentTime.strftime("Maple time is currently %H:%M %d-%m-%y")+"\n"
    toPrint += "Daily reset will happen in: " + str(currentTime.replace(hour=0,minute=0,second=0)+timedelta(1)-currentTime)+"\n"
    toPrint += "Weekly Boss reset will happen in: " + str(currentTime.replace(hour=0,minute=0,second=0)+timedelta(3-currentTime.weekday() if currentTime.weekday()<=2 else 10-currentTime.weekday())-currentTime)+"\n"
    toPrint += "Dojo reset will happen in: " +str(currentTime.replace(hour=0,minute=0,second=0)+timedelta(7-currentTime.weekday())-currentTime)+"\n"
    toPrint += "You can claim the weekly guild potions right now!" if currentTime.weekday()==0 else ("You will be able to claim the weekly guild potions in: "+str(currentTime.replace(hour=0,minute=0,second=0)+timedelta(7-currentTime.weekday())-currentTime))+"\n"
    return toPrint

class MapleUtil(commands.Cog):
    """performs various maple related commands"""

    @commands.command(name="time")
    async def time(self)
        """Prints maple time"""
        toPrint = datetime.utcnow().strftime("Maple time is currently %H:%M %d-%m-%y")
        await ctx.send(embed=generateEmbed("Time", toPrint))

    @commands.command(name="next2x", aliases=["2x"])
    async def next2x(self,ctx):
        """Finds the latest 2x post"""
        toPrint = get2xTimes()
        await ctx.send(embed=generateEmbed("2x EXP & Drop", toPrint))
        gc.collect()

    @commands.command(name="patchnotes", aliases=["patch"])
    async def patchnotes(self,ctx):
        """Finds the latest patch notes"""
        toPrint = fetchUrl("update", ["Patch Notes"])
        if not toPrint:
            toPrint = "No patch notes were found."
        await ctx.send(embed=generateEmbed("Patch Notes", toPrint))
        gc.collect()
    @commands.command()
    async def csupdate(self,ctx):
        """Finds the latest Cash Shop Update"""
        toPrint = fetchUrl("sale", ["Cash Shop Update"])
        if not toPrint:
            toPrint = "No Cash Shop update was found."
        await ctx.send(embed=generateEmbed("Cash Shop Update", toPrint))
        gc.collect()

    @commands.command()
    async def ursus(self,ctx):
        """Sends info about current ursus 2x meso status"""
        toPrint = getUrsus2xStatus()
        await ctx.send(embed=generateEmbed("Ursus Status", toPrint))
        gc.collect()

    @commands.command(name="maintenance", aliases=["maint"])
    async def maintenance(self,ctx):
        """Finds the last maintenance times"""
        toPrint = getMaintenanceTime()
        if not toPrint:
            toPrint = "No maintenance was found"
        await ctx.send(embed=generateEmbed("Maintenance", toPrint))
        gc.collect()

    @commands.command()
    async def reset(self,ctx):
        """Sends various times regarding the games reset timers"""
        toPrint=getResetTimes()
        await ctx.send(embed=generateEmbed("Times", toPrint))
        gc.collect()
        
    @commands.command(name="sunny", aliases=["sunnysunday"])
    async def sunny(self,ctx):
        """Links the sunny sunday section in the last patch note, does not check sunny sunday existance! just assumes one exists in the lastest patch notes"""
        toPrint = fetchUrl("update", ["Patch Notes"])+"#sunny"
        if not toPrint:
            toPrint = "No patch notes were found."
        await ctx.send(embed=generateEmbed("Sunny Sunday", toPrint))
        gc.collect()
def setup(bot):
    bot.add_cog(mapleUtil(bot))
