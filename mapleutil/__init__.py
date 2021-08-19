from .mapleutil import MapleUtil

def setup(bot):
    #bot setup
    bot.add_cog(MapleUtil(bot))