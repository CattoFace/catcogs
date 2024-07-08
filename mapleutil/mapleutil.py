import discord
from datetime import datetime
import gc
from redbot.core import app_commands, commands
from . import jsonlib
from . import scrapelib
import re
import json
import requests
import random 
from io import BytesIO
from .util import get_perecent

def generateEmbed(name, content):
    embed = discord.Embed(color=discord.Color.orange(), description=content, title="**"+name+"**")
    return embed

def subchar(charname,region, session):
    char = scrapelib.fetchChar(charname,region, session)
    if char:
        charname = char["characterName"]
        embd=generateEmbed(charname,f"World: {char['worldName']} Rank: {char['rank']:,}\nLevel: {char['level']} Exp: {char['exp']:,}({get_perecent(char['level'], char['exp']):.3f}%)\nClass: {char['jobName']}")
        file = discord.File(BytesIO(s.get(char["characterImgURL"]).content), filename=charname+".png")
        embd.set_image(url=f"attachment://{charname}.png")
    else:
        file = None
        embd=generateEmbed(charname, "The character was not found")
    return embd, file
    

class MapleUtil(commands.Cog):

    def __init__(self, bot):
        self.data = jsonlib.initiateBot()
        self.bot = bot
        self.session = requests.Session()

    def __del__(self):
        self.session.close()

    @app_commands.command(name="time", description="Shows the current time in GMS")
    async def time(self, interaction: discord.Interaction):
        toPrint = datetime.utcnow().strftime("Maple time is currently %H:%M:%S %d-%m-%y")
        await interaction.response.send_message(embed=generateEmbed("Time", toPrint))
        gc.collect()

    @app_commands.command(name="next2x", description="Finds the latest 2x post")
    async def next2x(self,iteraction: discord.Interaction):
        toPrint = scrapelib.get2xTimes()
        await iteraction.response.send_message(embed=generateEmbed("2x EXP & Drop", toPrint))
        gc.collect()

    @app_commands.command(name="patchnotes", description="Finds the latest patch notes")
    async def patchnotes(self,interaction: discord.Interaction):
        toPrint = scrapelib.fetchUrl("update", ["Patch Notes"], summary=True, session=self.session)
        if toPrint:
            self.data["patchnotes"]=toPrint
            jsonlib.updateJson(self.data)
        elif("patchnotes" in self.data):
            toPrint=self.data["patchnotes"]
        else:
            toPrint = "No patch notes were found."
        await interaction.response.send_message(embed=generateEmbed("Patch Notes", toPrint))
        gc.collect()

    @app_commands.command(description="Finds the latest Cash Shop Update")
    async def csupdate(self,interaction: discord.Interaction):
        toPrint = scrapelib.fetchUrl("sale", ["Cash Shop Update"], summary=True, session=self.session)
        if toPrint:
            self.data["csupdate"]=toPrint
            jsonlib.updateJson(self.data)
        elif("csupdate" in self.data):
            toPrint=self.data["csupdate"]
        else:
            toPrint = "No cash shop update post were found."
        await interaction.response.send_message(embed=generateEmbed("CS Update", toPrint))
        gc.collect()

    @app_commands.command(description="Sends info about current ursus 2x meso status")
    async def ursus(self,interaction: discord.Interaction):
        toPrint = scrapelib.getUrsus2xStatus(0 if ("summer" not in self.data) or self.data["summer"]==0 else 1)
        await interaction.response.send_message(embed=generateEmbed("Ursus Status", toPrint))
        gc.collect()

    @app_commands.command(name="maint", description="Finds the last maintenance times")
    async def maintenance(self,interaction: discord.Interaction):
        toPrint = scrapelib.fetchUrl("maintenance",summary=True, session=self.session)
        if toPrint:
            self.data["maintenance"]=toPrint
            jsonlib.updateJson(self.data)
        elif("csupdate" in self.data):
            toPrint=self.data["maintenance"]
        else:
            toPrint = "No cash shop update post were found."
        await interaction.response.send_message(generateEmbed("Maintenance", toPrint))
        gc.collect()

    @app_commands.command(description="Sends various times regarding the games reset timers")
    async def reset(self,interaction: discord.Interaction):
        toPrint=scrapelib.getResetTimes()
        await interaction.response.send_message(embed=generateEmbed("Times", toPrint))
        gc.collect()

    @app_commands.command(name="sunnysunday", description="Links the sunny sunday section in the last patch note, does not check sunny sunday existance!")
    async def sunnysunday(self,interaction: discord.Interaction):
        toPrint = scrapelib.fetchUrl("update", ["Patch Notes"], summary=True, session=self.session)
        if toPrint:
            self.data["patchnotes"]=toPrint
            jsonlib.updateJson(self.data)
        elif("patchnotes" in self.data):
            toPrint=self.data["patchnotes"]
        else:
            toPrint = "No patch notes were found."
        await interaction.response.send_message(embed=generateEmbed("Sunny Sunday", toPrint+"#SunnySunday"))
        gc.collect()

    @app_commands.command(description="Sends a random maple tip")
    async def mapletip(self,interaction: discord.Interaction):
        j = json.loads(requests.get("https://maplestory.io/api/GMS/251/tips").text)
        group=random.randint(0,2)
        toPrint = j[group]["messages"][random.randint(0,len(j[group]["messages"]))]
        await interaction.response.send_message(embed=generateEmbed("Maple Tip", toPrint))
        gc.collect()

    @app_commands.command(description="Shows info of the character from the NA region")
    @app_commands.describe(charname="The character to show")
    async def char(self,interaction: discord.Interaction,charname: str):
        embed, file = subchar(charname, 0, session=self.session)
        if file:
            await interaction.response.send_message(embed=embed, file=file)
        else:
            await interaction.response.send_message(embed=embed)
        gc.collect()

    @app_commands.command(description="Shows info of the character from the EU region")
    @app_commands.describe(charname="The character to show")
    async def chareu(self,interaction: discord.Interaction,charname: str):
        embed, file = subchar(charname, 1, session=self.session)
        if file:
            await interaction.response.send_message(embed=embed, file=file)
        else:
            await interaction.response.send_message(embed=embed)
        gc.collect()

    #@commands.has_permissions(manage_messages=True)
    @app_commands.command(description="Adds a character to this servers rankings as an NA character")
    @app_commands.describe(charname="The character to add")
    @app_commands.guild_only()
    async def addrank(self,interaction: discord.Interaction,charname: str):
        if scrapelib.fetchChar(charname,0, session=self.session):
            jsonlib.addChar(self.data,str(interaction.guild_id),charname,0)
            await interaction.response.send_message(charname +" was added")
        else:
            await interaction.response.send_message(charname +" was not found")
        gc.collect()
        
    #@commands.has_permissions(manage_messages=True)
    @app_commands.command(description="Adds a character to this servers rankings as an EU character")
    @app_commands.describe(charname="The character to add")
    @app_commands.guild_only()
    async def addrankeu(self,interaction: discord.Interaction,charname: str):
        if scrapelib.fetchChar(charname,1, session=self.session):
            jsonlib.addChar(self.data,str(interaction.guild_id),charname,1)
            await interaction.response.send_message(charname +" was added")
        else:
            await interaction.response.send_message(charname +" was not found")
        gc.collect()
            
    @app_commands.command(description="Removes a character from this servers rankings as an NA character")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.describe(charname="The character to remove")
    @app_commands.guild_only()
    async def delrank(self,interaction: discord.Interaction,charname: str):
        jsonlib.delChar(self.data, str(interaction.guild_id),charname,0)
        await interaction.response.send_message(charname +" was removed")
        gc.collect()
    
    @app_commands.command(description="Removes a character from this servers rankings as an EU character")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.describe(charname="The character to remove")
    @app_commands.guild_only()
    async def delrankeu(self,interaction: discord.Interaction,charname: str):
        jsonlib.delChar(self.data, str(interaction.guild_id),charname,1)
        await interaction.response.send_message(charname +" was removed")
        gc.collect()
    
    @commands.command()
    @commands.guild_only()
    async def serverrankings(self,ctx):
        """Print the servers current rankings"""
        async with ctx.typing():
            toPrint = scrapelib.formatLeaderboard(scrapelib.generateLeaderboard(self.data, str(ctx.guild.id), session=self.session))
            await ctx.send(embed=generateEmbed("Server Rankings", toPrint))
        gc.collect()
    
    @app_commands.command(description="registers a new character as yours")
    @app_commands.describe(charname="The character to add", region="The region of the character")
    @app_commands.choices(region=[app_commands.Choice(name="NA", value="na"), app_commands.Choice(name="EU", value="eu")])
    async def registermychar(self,interaction: discord.Interaction,charname: str, region: str):
        jsonlib.assignChar(self.data, str(interaction.user.id),charname,region)
        await interaction.response.send_message(charname+ " is now your registered IGN")
        gc.collect()

    @app_commands.command(description="shows your registered character")
    async def mychar(self,interaction: discord.Interaction):
        id = str(interaction.user.id)
        if not id:
            await interaction.response.send_message("Syntax error, please use either `mychar` or `mychar <mention>`")
        else:
            char = jsonlib.getPersonalChar(self.data,id)
            if char:
                embed, file = subchar(char["name"], char["region"], session=self.session)
                if file:
                    await interaction.response.send_message(embed=embed, file=file)
                else:
                    await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message('It looks like you don\'t have a assigned IGN, assign one with the command /registermychar <name> <region(NA/EU)>')
        gc.collect()

    @app_commands.command()
    @app_commands.default_permissions(manage_messages=True)
    async def setdata(self,interaction: discord.Interaction,key: str,s:str):
        self.data[key]=s
        jsonlib.updateJson(self.data)
        await interaction.response.send_message(f'{key} was set to {s}')
    
    @app_commands.command()
    @app_commands.default_permissions(manage_messages=True)
    async def setmemberchar(self,interaction: discord.Interaction,user:str,ign:str,region:str):
        id=str(re.sub('\D','',user) if re.match(r"<@!?[0-9]+>",user) else "")
        if id:
            jsonlib.assignChar(self.data,id,ign,region)
            await interaction.response.send_message(f'Set {user}\'s character to {ign} in {region}')
        else:
            await interaction.response.send_message("Invalid user")

    @app_commands.command()
    async def dumpdata(self,interaction: discord.Interaction):
        await interaction.response.send_message(self.data)

    @app_commands.command()
    @app_commands.choices(summer=[app_commands.Choice(name="True", value='true'), app_commands.Choice(name="False", value='false')])
    @app_commands.default_permissions(manage_messages=True)
    async def setursussummer(self,interaction: discord.Interaction, summer: str):
        if summer=='true':
            self.data["summer"]=1
            await interaction.response.send_message("Ursus summer turned on")
        else:
            self.data["summer"]=0
            await interaction.response.send_message("Ursus summer turned off")

    
