import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite

from dotenv import load_dotenv
import os
load_dotenv()
serv_id = os.getenv("SERV_ID")
my_pseudo = os.getenv("MY_PSEUDO")

class DB_temp(commands.Cog):
    def __init__(self, bot : commands.Bot, connection : aiosqlite.Connection) -> None:
        self.bot = bot
        self.connection = connection

    @commands.Cog.listener(name="on_ready")
    async def printReady(self) -> None:
        print("Cog temporaire pour afficher la BDD")

    ###################################################### KITTY ######################################################

    @app_commands.command(name="tablekitty", description="Affiche le contenu de la table kitty")
    async def table_Kitty(self, interaction: discord.Interaction) -> discord.Message:
        if interaction.user.name != my_pseudo:
            return await interaction.response.send_message("Vous n'avez pas les droits pour cette commande")
        cursor = await self.connection.execute("SELECT * FROM kitty")
        rows = await cursor.fetchall()
        result_str = ""
        for row in rows:
            result_str += f"ID: {row[0]}, Name: {row[1]}, Funds: {row[2]}, Creator: {row[3]}, Channel: {row[4]}\n"
        return await interaction.response.send_message(f"Contenu de la table kitty:\n{result_str}")

    ###################################################### SHARES ######################################################

    @app_commands.command(name='tableshares', description='affiche le contenue de la table share')
    async def table_shares(self, interaction: discord.Interaction) -> discord.Message:
        if interaction.user.name != my_pseudo:
            return await interaction.response.send_message("Vous n'avez pas les droits pour cette commande")
        cursor = await self.connection.execute("SELECT * FROM share")
        rows = await cursor.fetchall()
        result_str = ""
        for row in rows:
            result_str += f"IdKitty: {row[0]}, Pseudo: {row[1]}, Amount: {row[2]}\n"
        return await interaction.response.send_message(f"Contenu de la table share:\n{result_str}")

    ###################################################### PURCHASE ######################################################

    @app_commands.command(name='tablepurchase', description='affiche le contenue de la table purchase')
    async def table_purchases(self, interaction: discord.Interaction) -> discord.Message:
        if interaction.user.name != my_pseudo:
            return await interaction.response.send_message("Vous n'avez pas les droits pour cette commande")
        cursor = await self.connection.execute("SELECT * FROM purchase")
        rows = await cursor.fetchall()
        result_str = ""
        for row in rows:
            result_str += f"IdPurchase: {row[0]}, IdKitty: {row[1]}, Pseudo: {row[2]}, Amount: {row[3]}, Object: {row[4]}\n"
        return await interaction.response.send_message(f"Contenu de la table purchase:\n{result_str}")

    ###################################################### USER ######################################################
    
    @app_commands.command(name='tableuser', description='Affiche le contenu de la table user')
    async def table_user(self, interaction: discord.Interaction) -> discord.Message:
        if interaction.user.name != my_pseudo:
            return await interaction.response.send_message("Vous n'avez pas les droits pour cette commande")
        cursor = await self.connection.execute("SELECT * FROM user")
        rows = await cursor.fetchall()
        result_str = ""
        for row in rows:
            result_str += f"Id: {row[0]}, Pseudo: {row[1]}, Prefer: {row[2]}, MinAction: {row[3]}\n"
        return await interaction.response.send_message(f"Contenu de la table user:\n{result_str}", ephemeral=True)
    
    ###################################################### CLOSETO ######################################################

    @app_commands.command(name='tablecloseto', description='Affiche le contenu de la table closeto')
    async def table_closeto(self, interaction: discord.Interaction) -> discord.Message:
        if interaction.user.name != my_pseudo:
            return await interaction.response.send_message("Vous n'avez pas les droits pour cette commande")
        cursor = await self.connection.execute("SELECT * FROM closeto")
        rows = await cursor.fetchall()
        result_str = ""
        for row in rows:
            result_str += f"User1: {row[0]}, User2: {row[1]}\n"
        return await interaction.response.send_message(f"Contenu de la table closeto:\n{result_str}", ephemeral=True)

    ###################################################### SQL injection ######################################################

    @app_commands.command(name='sql_injection', description='Permet d entrer directement une requete SQL')
    async def sql_injection(self, interaction: discord.Interaction, requete : str) -> discord.Message:
        if interaction.user.name != my_pseudo:
            return await interaction.response.send_message("Vous n'avez pas les droits pour cette commande")
        cursor = await self.connection.execute(requete)
        await self.connection.commit()
        return await interaction.response.send_message(cursor, ephemeral=True)

async def setup(bot : commands.Bot) -> None:
        await bot.add_cog(DB_temp(bot, await aiosqlite.connect('Kitty.db')), guild=discord.Object(id=serv_id))