from typing import Any
from discord.ext import commands
import discord
from discord_pgp.pgp import get_info, get_key
from discord_pgp import database

bot = commands.Bot("!", intents=discord.Intents.all())


@bot.command(name="키정보")
async def key_info(ctx: commands.Context[Any]):
    if not ctx.message.attachments:
        return await ctx.send("키 내놔")

    key_bytes = await ctx.message.attachments[0].read()
    key = get_key(key_bytes)

    if not key.is_public:
        return await ctx.send("님 그거 맞음?")

    infos, algo = get_info(key)

    embed = discord.Embed(title="PGP KEY info", description=f"This key use {algo}")
    for info in infos:
        embed.add_field(
            name=info.name, value=f"{info.email}\n\nSignatureType: {info.sig.name}"
        )
    await ctx.send(embed=embed)


@bot.command(name="유저정보")
async def user_info(ctx: commands.Context[Any], user: discord.User):
    ...


@bot.command(name="내정보")
async def my_info(ctx: commands.Context[Any]):
    users = database.read()
    for user in users:
        if user["user_id"] == ctx.author.id:
            key = get_key(user["key"])
            infos, algo = get_info(key)
            embed = discord.Embed(
                title="니가 등록한 정보임",
                description=f"알고리즘: {algo}\n\n인증됐음?: {user['verified']}",
            )
            for info in infos:
                embed.add_field(
                    name=info.name,
                    value=f"{info.email}\n\nSignatureType: {info.sig.name}",
                )
            return await ctx.send(embed=embed)

    await ctx.send("그런건 없다.")


@bot.command(name="키등록")
async def key_register(ctx: commands.Context[Any]):
    if not ctx.message.attachments:
        return await ctx.send("키 내놔")

    key_bytes = await ctx.message.attachments[0].read()
    key = get_key(key_bytes)

    if not key.is_public:
        return await ctx.send("님 그거 맞음?")

    info: dict[str, Any] = {
        "user_id": ctx.author.id,
        "key": str(key),
        "verified": False,
    }
    database.add_user(info)

    return await ctx.send("일단 그거 등록했음 ㅇㅇ http://home.saebasol.org:8000 가서 등록 ㄱ")
