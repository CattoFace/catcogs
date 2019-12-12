from redbot.core import commands
import requests
from bs4 import BeautifulSoup

def scrape():
    url = findLatestPatchNotes()
    if not url:
        return 0
    site = requests.get(url)
    times = []
    soup = BeautifulSoup(site.text, 'html.parser').find('div', class_='component component-news-article').find('ul').find_next('p')
    soup = soup.find_next(lambda tag: tag.name=='span' and '2x EXP & Drop' in tag.text).find_next('p')
    for entry in soup.text.split("UTC:"):
        if entry:
            times.append("UTC:"+entry)
    return times

def findLatestPatchNotes():
    baseURL = 'http://maplestory.nexon.net'
    site = requests.get(baseURL + '/news/update#news-filter')
    soup = BeautifulSoup(site.content, 'html.parser')
    news = soup.find('ul', class_='news-container rows').find_all('div', class_='text')
    for entry in news:
        title = entry.find('a')
        if ('Patch Notes' in title.text):
            return baseURL + title['href']
    return 0

def findCountdown(times):
    for time in times:
        return '0'

def get2xTimes():
    times = scrape()
    toPrint=''
    if not times:
        return "No 2x periods were found"
    for time in times:
        toPrint+=time+"\n"
    #WORK IN PROGRESS    
    #countdown = findCountdown(times)
    #toPrint+="The next 2x period is in "+countdown
    return toPrint

class mapleCog(commands.Cog):

    @commands.command()
    async def next2x(self, ctx):
        """Finds the latest 2x post"""
        toPrint = get2xTimes()
        await ctx.send(toPrint)

    @commands.command()
    async def patchnotes(self, ctx):
        """Finds the latest patch notes"""
        toPrint = findLatestPatchNotes()
        if not toPrint:
            toPrint = "No patch notes were found."
        await ctx.send(toPrint)
