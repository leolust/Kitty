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
        cursor = await self.connection.execute(f"SELECT id FROM kitty WHERE name='{kitty_name}'")
        id = await cursor.fetchone()
        if id is not None:
            return await interaction.response.send_message(f"La cagnotte \"{kitty_name}\" existe déjà ")
        await self.connection.execute("""
        INSERT INTO kitty (name, creatorName) VALUES (?, ?)
        """, (kitty_name, interaction.user.name)
        )
        await self.connection.commit()
        return await interaction.response.send_message(f"La cagnotte \"{kitty_name}\" à été créé ")
    
    @app_commands.command(name="participate", description="Register your participation for a kitty")
    async def participate(self, interaction : discord.Interaction, kitty_name : str, amount : float) -> discord.Message:
        cursor = await self.connection.execute("SELECT id FROM kitty WHERE name=?", (kitty_name,))
        idKitty = await cursor.fetchone()
        if idKitty is None: # Si la cagnotte n'existe pas on s'arrete
            return await interaction.response.send_message(f"La cagnotte \"{kitty_name}\" n'existe pas")
        # Mise à jour de la cagnotte
        await self.connection.execute("""
        UPDATE kitty SET funds = funds + ? WHERE id = ?
        """, (amount, idKitty[0]))
        cursor = await self.connection.execute("SELECT amount FROM share WHERE idKitty=? AND pseudo=?", (idKitty[0], interaction.user.name))
        oldAmount = await cursor.fetchone()
        # Insertion ou mise à jour de la participation
        if oldAmount:
            amount += oldAmount[0]
            await self.connection.execute("""
            UPDATE share SET amount = ? WHERE idKitty = ? AND pseudo = ?
            """, (amount, idKitty[0], interaction.user.name))
        else:
            await self.connection.execute("""
            INSERT INTO share VALUES (?, ?, ?)
            """, (idKitty[0], interaction.user.name, amount))
        await self.connection.commit()
        return await interaction.response.send_message(f"Vous avez ajouté un total de {amount} euros à la cagnotte \"{kitty_name}\"")



#########################################################################################################################
#########################################################################################################################    
#########################################################################################################################

    @app_commands.command(name="showkitty", description="Affiche le contenu de la table kitty")
    async def showKitty(self, interaction: discord.Interaction) -> discord.Message:
        cursor = await self.connection.execute("SELECT * FROM kitty")
        rows = await cursor.fetchall()
        result_str = ""
        for row in rows:
            result_str += f"ID: {row[0]}, Name: {row[1]}, Funds: {row[2]}, Creator: {row[3]}\n"
        await interaction.response.send_message(f"Contenu de la table kitty:\n{result_str}")

    @app_commands.command(name='showshares', description='affiche le contenue de la table share')
    async def showshares(self, interaction: discord.Interaction) -> discord.Message:
        cursor = await self.connection.execute("SELECT * FROM share")
        rows = await cursor.fetchall()
        result_str = ""
        for row in rows:
            result_str += f"IdKitty: {row[0]}, Pseudo: {row[1]}, Amount: {row[2]}\n"
        await interaction.response.send_message(f"Contenu de la table share:\n{result_str}")   

async def setup(bot : commands.Bot) -> None:
        await bot.add_cog(DB(bot, await aiosqlite.connect('Kitty.db')), guild=discord.Object(id=serv_id))