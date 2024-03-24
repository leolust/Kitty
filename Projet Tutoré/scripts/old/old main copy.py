import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(bot.user.name, "est en ligne !")

@bot.event
async def on_message(message : discord.Message):
    if message.author.bot:
        return
    if "bot" in message.content:
        await message.channel.send("Vous m'avez appelé ?")
    await bot.process_commands(message)

@bot.command()
async def test(ctx : commands.Context):
    return await ctx.send(f"Le test de {ctx.author} marche bien !")

@bot.command()
async def pgcd(ctx : commands.Context, a : int, b : int):
    while b:
        a, b = b, a % b
    return await ctx.send(str(a))

@bot.command()
async def echo(ctx : commands.Context, i : int, *, message : str): 
    # *, sers à récupérer toute la chaine qui suis sans avoir besoin de la mettre entre guillemets
    for _ in range(i):
        await ctx.send(message)

if __name__ == "__main__":
    bot.run("")
