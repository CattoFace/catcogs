import discord
from datetime import datetime, timedelta
import gc
from redbot.core import commands
from . import jsonlib
from . import scrapelib
import redbot
import re

data ={}

def generateEmbed(name, content):
	embed = discord.Embed(color=discord.Color.orange(), description=content, title="**"+name+"**")
	return embed

def subchar(charName,region):
	char=scrapelib.fetchChar(charName,region)
	embd = 0
	if char:
		embd=generateEmbed(char["CharacterName"],"World: "+char["WorldName"] + " Rank: "+f'{char["Rank"]:,}'+"\nLevel: "+str(char["Level"])+" Exp: "+f'{char["Exp"]:,}'+"\nClass: "+char["JobName"])
		embd.set_image(url=char["CharacterImgUrl"])
	else:
		embd=generateEmbed(charName, "The character was not found")
	return embd
    

class MapleUtil(commands.Cog):
	"""performs various maple related commands"""

	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="time")
	async def time(self,ctx):
		"""Prints maple time"""
		toPrint = datetime.utcnow().strftime("Maple time is currently %H:%M:%S %d-%m-%y")
		await ctx.send(embed=generateEmbed("Time", toPrint))
		gc.collect()

	@commands.command(name="next2x", aliases=["2x"])
	async def next2x(self,ctx):
		"""Finds the latest 2x post"""
		toPrint = scrapelib.get2xTimes()
		await ctx.send(embed=generateEmbed("2x EXP & Drop", toPrint))
		gc.collect()

	@commands.command(name="patchnotes", aliases=["patch"])
	async def patchnotes(self,ctx):
		"""Finds the latest patch notes"""
		toPrint = scrapelib.fetchUrl("update", ["Patch Notes"])
		if toPrint:
			data["patchnotes"]=toPrint
			jsonlib.updateJson(data)
		elif("patchnotes" in data):
			toPrint=data["patchnotes"]
		else:
		    toPrint = "No patch notes were found."
		await ctx.send(toPrint)
		gc.collect()

	@commands.command()
	async def csupdate(self,ctx):
		"""Finds the latest Cash Shop Update"""
		toPrint = scrapelib.fetchUrl("sale", ["Cash Shop Update"])
		if toPrint:
			data["csupdate"]=toPrint
			jsonlib.updateJson(data)
		elif("csupdate" in data):
			toPrint=data["csupdate"]
		else:
		    toPrint = "No cash shop update post were found."
		await ctx.send(toPrint)
		gc.collect()

	@commands.command()
	async def ursus(self,ctx):
		"""Sends info about current ursus 2x meso status"""
		toPrint = scrapelib.getUrsus2xStatus(0 if (not "summer" in data) or data["summer"]==0 else 1)
		await ctx.send(embed=generateEmbed("Ursus Status", toPrint))
		gc.collect()

	@commands.command(name="maintenance", aliases=["maint"])
	async def maintenance(self,ctx):
		"""Finds the last maintenance times"""
		toPrint = scrapelib.getMaintenanceTime()
		if toPrint:
			data["maint"]=toPrint
			jsonlib.updateJson(data)
		elif("maint" in data):
			toPrint=data["maint"]
		else:
		    toPrint = "No maintenance were found."
		await ctx.send(embed=generateEmbed("Maintenance",toPrint))
		gc.collect()

	@commands.command()
	async def reset(self,ctx):
		"""Sends various times regarding the games reset timers"""
		toPrint=scrapelib.getResetTimes()
		await ctx.send(embed=generateEmbed("Times", toPrint))
		gc.collect()

	@commands.command(name="sunny", aliases=["sunnysunday"])
	async def sunny(self,ctx):
		"""Links the sunny sunday section in the last patch note, does not check sunny sunday existance! just assumes one exists in the lastest patch notes"""	
		toPrint = scrapelib.fetchUrl("update", ["Patch Notes"])
		if toPrint:
			data["patchnotes"]=toPrint
			jsonlib.updateJson(data)
		elif("patchnotes" in data):
			toPrint=data["patchnotes"]
		else:
		    toPrint = "No patch notes were found."
		await ctx.send(toPrint+"#sunny")
		gc.collect()

	@commands.command()
	async def mapletip(self,ctx):
		"""Sends a random maple tip"""
		j = json.loads(requests.get("https://maplestory.io/api/GMS/219/tips").text)
		group=random.randint(0,2)
		toPrint = j[group]["messages"][random.randint(0,len(j[group]["messages"]))]
		await ctx.send(embed=generateEmbed("Maple Tip", toPrint))
		gc.collect()

	@commands.command()
	async def char(self,ctx,charName):
		"""Shows an image of the character from the NA region"""
		await ctx.send(embed=subchar(charName,0))
		gc.collect()

	@commands.command()
	async def chareu(self,ctx,charName):
		"""Shows an image of the character from the EU region"""
		await ctx.send(embed=subchar(charName,1))
		gc.collect()

	#@commands.has_permissions(manage_messages=True)
	@commands.command()
	async def addrank(self,ctx,char):
		"""Adds a character to this servers rankings as an NA character"""
		if scrapelib.fetchChar(char,0):
			jsonlib.addChar(data,str(ctx.guild.id),char,0)
			await ctx.send(char +" was added")
		else:
			await ctx.send(char +" was not found")
		gc.collect()
    	
	#@commands.has_permissions(manage_messages=True)
	@commands.command()
	async def addrankeu(self,ctx,char):
		"""Adds a character to this servers rankings as an EU character"""
		if scrapelib.fetchChar(char,1):
			jsonlib.addChar(data,str(ctx.guild.id),char,1)
			await ctx.send(char +" was added")
		else:
			await ctx.send(char +" was not found")
		gc.collect()
        	
	@commands.has_permissions(manage_messages=True)
	@commands.command()
	async def delrank(self,ctx,char):
		"""Removes a character from this servers rankings as an NA character"""
		jsonlib.delChar(data, str(ctx.guild.id),char,0)
		await ctx.send(char +" was removed")
		gc.collect()
	
	@commands.command()
	async def delrankeu(self,ctx,char):
		"""Removes a character from this servers rankings as an EU character"""
		jsonlib.delChar(data, str(ctx.guild.id),char,1)
		await ctx.send(char +" was removed")
		gc.collect()
	
	@commands.command()
	async def serverrankings(self,ctx):
		"""Prints the servers current rankings"""
		async with ctx.typing():
			toPrint = scrapelib.formatLeaderboard(scrapelib.generateLeaderboard(data, str(ctx.guild.id)))
			await ctx.send(embed=generateEmbed("Server Rankings", toPrint))
		gc.collect()
	
	@commands.command()
	async def registermychar(self,ctx,name,region):
		"""registers a new character as yours"""
		jsonlib.assignChar(data, str(ctx.author.id),name,region)
		await ctx.send(name+ " is now your registered IGN")
		gc.collect()

	@commands.command()
	async def mychar(self,ctx,*args):
		"""shows your registered character"""
		id = str(ctx.author.id if len(args)==0 else (re.sub('\D','',args[0]) if re.match(r"<@!?[0-9]+>",args[0]) else ""))
		if not id:
			await ctx.send("Syntax error, please use either `mychar` or `mychar <mention>`")
		else:
			char = jsonlib.getPersonalChar(data,id)
			if char:
				await ctx.send(embed=subchar(char["name"],char["region"]))
			else:
				await ctx.send('It looks like '+ ("you don\'t" if len(args)==0 else 'the specified user doesn\'t')+" have an assigned IGN, assign one with the command `registermychar <name> <region(NA/EU)>`")
		gc.collect()

	@commands.has_permissions(manage_messages=True)
	@commands.command()
	async def setdata(self,ctx,key,s):
		data[key]=s
		jsonlib.updateJson(data)
		await ctx.send(f'{key} was set to {s}')
	
	@commands.has_permissions(manage_messages=True)
	@commands.command()
	async def setmemberchar(self,ctx,user,ign,region):
		id=str(re.sub('\D','',user) if re.match(r"<@!?[0-9]+>",user) else "")
		if id:
			jsonlib.assignChar(data,id,ign,region)
			await ctx.send(f'Set {user}\'s character to {ign} in {region}')
		else:
			await ctx.send("Invlalid user")

	@commands.has_permissions(manage_messages=True)
	@commands.command()
	async def dumpdata(self,ctx):
		await ctx.send(data)

	@commands.has_permissions(manage_messages=True)
	@commands.command()
	async def setursussummer(self,ctx,bool):
		if bool.lower()=="true":
			data["summer"]=1
			await ctx.send("Ursus summer turned on")
		elif bool.lower()=="false":
			data["summer"]=0
			await ctx.send("Ursus summer turned off")
		else:
			await ctx.send("Invalid parameter, use `true` or `false`")
		

	
data = jsonlib.initiateBot()
