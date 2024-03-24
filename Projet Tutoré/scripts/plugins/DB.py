import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite

from dotenv import load_dotenv
import os
load_dotenv()
serv_id = os.getenv("SERV_ID")

class DB(commands.Cog):
    def __init__(self, bot : commands.Bot, connection : aiosqlite.Connection) -> None:
        self.bot = bot
        self.connection = connection

    @commands.Cog.listener(name="on_ready")
    async def printReady(self) -> None:
        print("Cog de la BDD")

    @app_commands.command(name="createkitty", description="creates a kitty")
    async def createKitty(self, interaction : discord.Interaction, kitty_name : str) -> discord.Message:
        await self.connection.execute("""
        INSERT INTO kitty (name, creatorName) VALUES (?, ?)
        """, (kitty_name, interaction.user.name)
        )
        await self.connection.commit()
        return await interaction.response.send_message(f"La cagnotte \"{kitty_name}\" à été créé ")
    
    @app_commands.command(name="showkitty", description="Affiche le contenu de la table kitty")
    async def showKitty(self, interaction: discord.Interaction) -> discord.Message:
        # Exécute la requête SELECT * sur la table kitty
        cursor = await self.connection.execute("SELECT * FROM kitty")
        rows = await cursor.fetchall()

        # Formatage des résultatsS
        result_str = ""
        for row in rows:
            result_str += f"ID: {row[0]}, Name: {row[1]}, Funds: {row[2]}, Creator: {row[3]}\n"

        # Envoie des résultats dans le salon Discord
        await interaction.response.send_message(f"Contenu de la table Kitty:\n{result_str}")
    
async def setup(bot : commands.Bot) -> None:
        await bot.add_cog(DB(bot, await aiosqlite.connect('Kitty.db')), guild=discord.Object(id=serv_id))