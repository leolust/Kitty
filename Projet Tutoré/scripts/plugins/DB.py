import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
import sqlite3

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
        cursor = await self.connection.execute("SELECT id FROM kitty WHERE name=?", (kitty_name,))
        id = await cursor.fetchone()
        if id is not None:
            return await interaction.response.send_message(f"La cagnotte \"{kitty_name}\" existe déjà ")
        await self.connection.execute("""
        INSERT INTO kitty (name, creatorName) VALUES (?, ?)
        """, (kitty_name, interaction.user.name)
        )
        await self.connection.commit()
        return await interaction.response.send_message(f"La cagnotte \"{kitty_name}\" à été créé par {interaction.user.name}")
    
    @app_commands.command(name="participate", description="Register your participation for a kitty")
    async def participate(self, interaction : discord.Interaction, kitty_name : str, amount : float) -> discord.Message:
        amount = round(amount, 2)
        cursor = await self.connection.execute("SELECT id FROM kitty WHERE name=?", (kitty_name,))
        idKitty = await cursor.fetchone()
        if idKitty is None: # Si la cagnotte n'existe pas on s'arrete
            return await interaction.response.send_message(f"La cagnotte \"{kitty_name}\" n'existe pas")
        try:
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
        except sqlite3.IntegrityError as e:
            return await interaction.response.send_message("Action Impossible, vérifez la cohérence de votre commande (exemple: montant négatif)")
        return await interaction.response.send_message(f"Votre participation à la cagnotte \"{kitty_name}\" est de {amount} euros")

    @app_commands.command(name="purchase", description="Add a purchase for a kitty")
    async def purchase(self, interaction : discord.Interaction, kitty_name : str, object : str, amount : float) -> discord.Message:
        amount = round(amount, 2)
        if amount == 0:
            return await interaction.response.send_message("Action Impossible, vérifez la cohérence de votre commande (exemple: fonds insuffisant, montant invalide...)")
        cursor = await self.connection.execute("SELECT id FROM kitty WHERE name=?", (kitty_name,))
        idKitty = await cursor.fetchone()
        if idKitty is None: # Si la cagnotte n'existe pas on s'arrete
            return await interaction.response.send_message(f"La cagnotte \"{kitty_name}\" n'existe pas")
        try:
            # Insertion de l'achat
            await self.connection.execute("""
            INSERT INTO purchase (idKitty, pseudo, amount, object) VALUES (?, ?, ?, ?)
            """, (idKitty[0], interaction.user.name, amount, object))
            await self.connection.commit()
            # Mise à jour de la cagnotte
            await self.connection.execute("""
            UPDATE kitty SET funds = funds - ? WHERE id = ?
            """, (amount, idKitty[0]))
        except sqlite3.IntegrityError as e:
            return await interaction.response.send_message("Action Impossible, vérifez la cohérence de votre commande (exemple: fonds insuffisant, montant invalide...)")
        return await interaction.response.send_message(f"{interaction.user.name} a dépensé {amount} euros pour l'achat de \"{object}\" pour la cagnotte \"{kitty_name}\"")

async def setup(bot : commands.Bot) -> None:
        await bot.add_cog(DB(bot, await aiosqlite.connect('Kitty.db')), guild=discord.Object(id=serv_id))