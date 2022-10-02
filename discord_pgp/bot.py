from typing import Any
from discord.ext import commands
import discord
from discord_pgp.pgp import get_info

bot = commands.Bot("!", intents=discord.Intents.all())


@bot.command(name="키정보")
async def keyinfo(ctx: commands.Context[Any]):
    key = await ctx.message.attachments[0].read()
    infos, algo = get_info(key)

    embed = discord.Embed(title="PGP KEY info", description=f"This key use {algo}")
    for info in infos:
        embed.add_field(name=info.name, value=f"{info.email}\n\nSignatureType: {info.sig.name}")
    await ctx.send(embed=embed)


