import discord
from discord.ext import commands
from discord import app_commands

from dotenv import load_dotenv
import os
load_dotenv()
token = os.getenv("BOT_TOKEN")
serv_id = os.getenv("SERV_ID")

# Un cog est une class qui contient un ensemble de commande
# Utilisé pour organiser le code et regrouper les fonctionnalités qui vont ensemble

class testCog(commands.Cog):
    def __init__(self, client : discord.Client) -> None:
        self.client = client

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



class MyClient(discord.Client):
    def __init__(self) -> None:
        super().__init__(intents=discord.Intents.all())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        await self.add_cog(testCog(self), guild=discord.Object(id=serv_id))
        await self.tree.sync(guild=discord.Object(id=serv_id))

    async def on_ready(self) -> None:
        print(self.user, "est en ligne !")

client = MyClient()

if __name__ == "__main__":
    client.run(token)