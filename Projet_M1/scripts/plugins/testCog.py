import discord
from discord.ext import commands
from discord import app_commands

from dotenv import load_dotenv
import os
load_dotenv()
serv_id = os.getenv("SERV_ID")

# Un cog est une class qui contient un ensemble de commande
# Utilisé pour organiser le code et regrouper les fonctionnalités qui vont ensemble

# Les commandes hybrides peuvent être utilisé avec un slash ou avec le préfix

class testCog(commands.Cog):
    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener(name="on_ready")
    async def printReady(self) -> None:
        print("Cog de test")

    @commands.command(name="test")
    async def test_command(self, ctx : commands.Context) -> discord.Message:
        return await ctx.send(f"Le test de {ctx.author} marche bien !")

    @commands.command(name="pgcd")
    async def pgcd(self, ctx : commands.Context, a : int, b : int) -> discord.Message:
        while b:
            a, b = b, a % b
        return await ctx.send(str(a))

    @commands.command(name="echo")
    async def echo(self, ctx : commands.Context, i : int, *, message : str) -> discord.Message: 
        # *, sers à récupérer toute la chaine qui suis sans avoir besoin de la mettre entre guillemets
        for _ in range(i):
            await ctx.send(message)

    @app_commands.command(name="slash_cog", description="Ma première commande Slash")
    async def commande(self, interaction : discord.Interaction):
        return await interaction.response.send_message("Ma première commande Slash")
    
    @app_commands.command(name="new_test", description="Ma première commande Slash")
    async def commandeAtest(self, interaction : discord.Interaction):
        return await interaction.response.send_message("pitié")

    @commands.hybrid_command(name="hybride", description="Ma commande hybride")
    @commands.guild_only()
    async def firstHybrid(self, ctx : commands.Context) -> discord.Message:
        return await ctx.send("Les commandes hybrides peuvent être utilisé avec un slash ou avec le préfix")
    
async def setup(bot : commands.Bot) -> None:
        await bot.add_cog(testCog(bot), guild=discord.Object(id=serv_id))