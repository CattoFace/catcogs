from .mapleutil import MapleUtil

async def setup(bot):
    #bot setup
    await bot.add_cog(MapleUtil(bot))
