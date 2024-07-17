from datetime import datetime, timedelta
from .util import get_percent
def status_dict2str(status):
    output = ''
    for i in range(3):
        label = f"login{'0' if i<10 else ''}{i}"
        s = ':green_square:  ' if status.get(label)==1 else ':red_square:  '
        if s:
            output += f"Login {i+1}:".rjust(11)+s
    output += "\n"
    for i in range(40):
        label = f"game{'0' if i<10 else ''}{i}"
        s = ':green_square:  ' if status.get(label)==1 else ':red_square:  '
        if s:
            output += f"Channel {i+1}:".rjust(11)+s
        if i%4==3:
            output+="\n"
    return status['worldName'],output

def fetchServerStatus(session, world=None):
    statuses = session.get("https://www.nexon.com/api/maplestory/no-auth/v1/server-status/na").json()["servers"]
    statuses.extend(session.get("https://www.nexon.com/api/maplestory/no-auth/v1/server-status/eu").json()["servers"])
    if world is not None:
        index = next(i for i,s in enumerate(statuses) if s["worldName"]==world)
        statuses.insert(0, statuses.pop(index))
    return [status_dict2str(status) for status in statuses]

def fetchChar(charName,eu,session):
    char = session.get(f"https://www.nexon.com/api/maplestory/no-auth/v1/ranking/{'eu' if eu else 'na'}?type=overall&id=legendary&character_name={charName}").json()
    return char["ranks"][0] if char["totalCount"]!=0 else None

def getUrsus2xStatus(summer):
    currentTime = datetime.utcnow()
    response = f"Ursus 2x meso time is active between <t:{str(int(currentTime.replace(hour=1,minute=0,second=0).timestamp()))}:t> and <t:{str(int(currentTime.replace(hour=5,minute=0,second=0).timestamp()  if summer else currentTime.replace(hour=3,minute=0,second=0).timestamp()))}:t> and between <t:{str(int(currentTime.replace(hour=18,minute=0,second=0).timestamp()))}:t> and <t:{str(int(currentTime.replace(hour=22,minute=0,second=0).timestamp() if summer else currentTime.replace(hour=20,minute=0,second=0).timestamp()))}:t>\n"
    isActive = 0
    checkTime = currentTime.replace(hour=1,minute=0,second=0)+timedelta(days=1)
    if currentTime.hour<1:
        isActive = 0
        checkTime = currentTime.replace(hour=1,minute=0,second=0)
    elif currentTime.hour<(5 if summer else 3):
        isActive = 1
        checkTime = currentTime.replace(hour=(5 if summer else 3),minute=0,second=0)
    elif currentTime.hour<18:
        isActive = 0
        checkTime = currentTime.replace(hour=18,minute=0,second=0)
    elif currentTime.hour<(22 if summer else 20):
        isActive = 1
        checkTime = currentTime.replace(hour=(22 if summer else 20),minute=0,second=0)
    if isActive:
        response+="Ursus 2x meso time is currently active, it will end in "
    else:
        response+="Ursus 2x meso time is not active, it will start in "
    return response + str(checkTime-currentTime).split('.')[0]

def getResetTimes():
    currentTime = datetime.utcnow()
    toPrint = currentTime.strftime("Maple time is currently %H:%M:%S %d-%m-%y")+"\n"
    toPrint += "Daily reset will happen in: " + str(currentTime.replace(hour=0,minute=0,second=0)+timedelta(1)-currentTime)+"\n"
    toPrint += "Weekly Boss reset will happen in: " + str(currentTime.replace(hour=0,minute=0,second=0)+timedelta(3-currentTime.weekday() if currentTime.weekday()<=2 else 10-currentTime.weekday())-currentTime)+"\n"
    toPrint += "Dojo/Weekly Quests/Guild Potions reset will happen in: " +str(currentTime.replace(hour=0,minute=0,second=0)+timedelta(7-currentTime.weekday())-currentTime)+"\n"
    return toPrint

def generateLeaderboard(data,server, session):
    leaderboard = []
    if server not in data or len(data[server])==0:
        return {}
    for char_name,char_region in data[server]:
        char=fetchChar(char_name,char_region, session)
        if char:
            leaderboard.append({'name':char["characterName"],'region':'EU' if char_region else 'NA','level':char["level"],'exp':char["exp"],"percent":get_percent(char["level"],char["exp"]) })
        else:
            leaderboard.append({'name':char_name,'region':'EU' if char_region else 'NA','level':0,'exp':0}) 
    leaderboard.sort(key = lambda x: (x['level'],x['exp']),reverse=1)
    return leaderboard

def formatLeaderboard(leaderboard):
    return '\n'.join('({rank}) {name} - Region: {region} Level: {level} Exp: {exp:,} ({percent:.3f}%)'.format(**x, rank=i+1) for i, x in enumerate(leaderboard))
