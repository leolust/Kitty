import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
import sqlite3

from dotenv import load_dotenv
import os
load_dotenv()
serv_id = os.getenv("SERV_ID")

class DB_temp(commands.Cog):
    def __init__(self, bot : commands.Bot, connection : aiosqlite.Connection) -> None:
        self.bot = bot
        self.connection = connection

    @commands.Cog.listener(name="on_ready")
    async def printReady(self) -> None:
        print("Cog temporaire pour afficher la BDD")

    @app_commands.command(name="tablekitty", description="Affiche le contenu de la table kitty")
    async def table_Kitty(self, interaction: discord.Interaction) -> discord.Message:
        cursor = await self.connection.execute("SELECT * FROM kitty")
        rows = await cursor.fetchall()
        result_str = ""
        for row in rows:
            result_str += f"ID: {row[0]}, Name: {row[1]}, Funds: {row[2]}, Creator: {row[3]}, Channel: {row[4]}\n"
        await interaction.response.send_message(f"Contenu de la table kitty:\n{result_str}")

    @app_commands.command(name='tableshares', description='affiche le contenue de la table share')
    async def table_shares(self, interaction: discord.Interaction) -> discord.Message:
        cursor = await self.connection.execute("SELECT * FROM share")
        rows = await cursor.fetchall()
        result_str = ""
        for row in rows:
            result_str += f"IdKitty: {row[0]}, Pseudo: {row[1]}, Amount: {row[2]}\n"
        await interaction.response.send_message(f"Contenu de la table share:\n{result_str}")

    @app_commands.command(name='tablepurchase', description='affiche le contenue de la table purchase')
    async def table_purchases(self, interaction: discord.Interaction) -> discord.Message:
        cursor = await self.connection.execute("SELECT * FROM purchase")
        rows = await cursor.fetchall()
        result_str = ""
        for row in rows:
            result_str += f"IdPurchase: {row[0]}, IdKitty: {row[1]}, Pseudo: {row[2]}, Amount: {row[3]}, Object: {row[4]}\n"
        await interaction.response.send_message(f"Contenu de la table purchase:\n{result_str}")


async def setup(bot : commands.Bot) -> None:
        await bot.add_cog(DB_temp(bot, await aiosqlite.connect('Kitty.db')), guild=discord.Object(id=serv_id))