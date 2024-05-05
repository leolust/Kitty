import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
import sqlite3

import repayment

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
    
    async def get_kitty_id(self, kitty_name, channel_name):
        cursor = await self.connection.execute("SELECT id FROM kitty WHERE name=? AND channelName=?", (kitty_name, channel_name))
        return await cursor.fetchone()

    ###################################################### CREATE ######################################################
    @app_commands.command(name="createkitty", description="creates a kitty")
    async def createKitty(self, interaction : discord.Interaction, kitty_name : str) -> discord.message:
        id = await self.get_kitty_id(kitty_name, interaction.channel.name)
        if id is not None:
            return await interaction.response.send_message(f"La cagnotte \"{kitty_name}\" existe déjà ")
        await self.connection.execute("""
        INSERT INTO kitty (name, creatorName, channelName) VALUES (?, ?, ?)
        """, (kitty_name, interaction.user.name, interaction.channel.name)
        )
        await self.connection.commit()
        return await interaction.response.send_message(f"La cagnotte \"{kitty_name}\" à été créé par {interaction.user.name}")
    
    ###################################################### PARTICIPATE ######################################################
    @app_commands.command(name="participate", description="Register your participation for a kitty")
    async def participate(self, interaction : discord.Interaction, kitty_name : str, amount : float) -> discord.message:
        idKitty = await self.get_kitty_id(kitty_name, interaction.channel.name)
        if idKitty is None: # Si la cagnotte n'existe pas on s'arrete
            return await interaction.response.send_message(f"La cagnotte \"{kitty_name}\" n'existe pas")
        amount = round(amount, 2)
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

    ###################################################### PURCHASE ######################################################
    @app_commands.command(name="purchase", description="Add a purchase for a kitty")
    async def purchase(self, interaction : discord.Interaction, kitty_name : str, object : str, amount : float) -> discord.message:
        amount = round(amount, 2)
        if amount == 0:
            return await interaction.response.send_message("Action Impossible, vérifez la cohérence de votre commande (exemple: fonds insuffisant, montant invalide...)")
        idKitty = await self.get_kitty_id(kitty_name, interaction.channel.name)
        if idKitty is None: # Si la cagnotte n'existe pas on s'arrete
            return await interaction.response.send_message(f"La cagnotte \"{kitty_name}\" n'existe pas")
        try:
            # Insertion de l'achat
            await self.connection.execute("""
            INSERT INTO purchase (idKitty, pseudo, amount, object) VALUES (?, ?, ?, ?)
            """, (idKitty[0], interaction.user.name, amount, object))
            # Mise à jour de la cagnotte
            await self.connection.execute("""
            UPDATE kitty SET funds = funds - ? WHERE id = ?
            """, (amount, idKitty[0]))
            await self.connection.commit()
        except sqlite3.IntegrityError as e:
            return await interaction.response.send_message("Action Impossible, vérifez la cohérence de votre commande (exemple: fonds insuffisant, montant invalide...)")
        return await interaction.response.send_message(f"{interaction.user.name} a dépensé {amount} euros pour l'achat de \"{object}\" pour la cagnotte \"{kitty_name}\"")

    ###################################################### CALCULATE ######################################################
    @app_commands.command(name="calculate", description="Calculate the transactions")
    async def calculate(self, interaction : discord.Interaction, kitty_name : str) -> discord.message:
        idKitty = await self.get_kitty_id(kitty_name, interaction.channel.name)
        if idKitty is None: # Si la cagnotte n'existe pas on s'arrete
            return await interaction.response.send_message(f"La cagnotte \"{kitty_name}\" n'existe pas")
        # Récupérer les contributions depuis la table share
        cursor = await self.connection.execute("SELECT pseudo, amount FROM share WHERE idKitty=?", idKitty)
        BDDcontrib = await cursor.fetchall()
        if BDDcontrib is None:
            return await interaction.response.send_message(f"La cagnotte \"{kitty_name}\" ne contient pas de participations")
        # Récupérer les dépenses depuis la table purchase
        cursor = await self.connection.execute("SELECT pseudo, amount FROM purchase WHERE idKitty=?", idKitty)
        BDDexpenses = await cursor.fetchall()
        if BDDcontrib is None:
            return await interaction.response.send_message(f"La cagnotte \"{kitty_name}\" ne contient pas d'achats")
        # Formatter les données sous forme de dictionnaires
        contributions = {pseudo: amount for pseudo, amount in BDDcontrib}
        expenses = {pseudo: amount for pseudo, amount in BDDexpenses}
        # Calculer les transactions
        repayments = repayment.repayment(contributions, expenses)
        # Afficher les transactions
        res = "\n".join([f"{debtor} doit rembourser {amount} euros à {creditor}" for debtor, creditor, amount in repayments])
        return await interaction.response.send_message(f"Voici les transactions à effectuer pour la cagnotte \"{kitty_name}\" \n {res}")
    
    ###################################################### SHOWKITTY ######################################################
    @app_commands.command(name="showkitty", description="Show informations about a kitty")
    async def kittyshow(self, interaction : discord.Interaction, kitty_name : str) -> discord.message:
        idKitty = await self.get_kitty_id(kitty_name, interaction.channel.name)
        if idKitty is None: # Si la cagnotte n'existe pas on s'arrete
            return await interaction.response.send_message(f"La cagnotte \"{kitty_name}\" n'existe pas")
        # Récupérer les informations de la cagnotte
        cursor = await self.connection.execute("SELECT name, funds, creatorName FROM kitty WHERE id = ?", idKitty)
        kitty_info = await cursor.fetchone()
        # Calculer la participation totale
        cursor = await self.connection.execute("SELECT SUM(amount) FROM share WHERE idKitty = ?", idKitty)
        total_contrib = await cursor.fetchone()
        total_contrib = total_contrib[0] if total_contrib[0] else 0
        # Calculer les dépenses totales
        cursor = await self.connection.execute("SELECT SUM(amount) FROM purchase WHERE idKitty = ?", idKitty)
        total_expenses = await cursor.fetchone()
        total_expenses = total_expenses[0] if total_expenses[0] else 0
        # Affichage
        message = (
            f"Résumé de la cagnotte \"{kitty_info[0]}\" :\n"
            f"- Créateur: {kitty_info[2]}\n"
            f"- Participation totale: {total_contrib}\n"
            f"- Dépenses totales: {total_expenses}\n"
            f"- Fonds restants: {kitty_info[1]}"
        )
        return await interaction.response.send_message(message)

    ###################################################### SHOWSHARES ######################################################
    @app_commands.command(name="showshares", description="Show all shares for a kitty")
    async def showshares(self, interaction : discord.Interaction, kitty_name : str) -> discord.message:
        idKitty = await self.get_kitty_id(kitty_name, interaction.channel.name)
        if idKitty is None: # Si la cagnotte n'existe pas on s'arrete
            return await interaction.response.send_message(f"La cagnotte \"{kitty_name}\" n'existe pas") 
        # Récupérer les participations
        cursor = await self.connection.execute("SELECT pseudo, amount FROM share WHERE idKitty = ?", idKitty)
        share_info = await cursor.fetchall()
        # Affichage
        message = f"Participations pour la cagnotte \"{kitty_name}\":\n"
        for pseudo, amount in share_info:
            message += f"- {pseudo}: {amount}\n"
        return await interaction.response.send_message(message)
    
    ###################################################### SHOWPURCHASES ######################################################
    @app_commands.command(name="showpurchases", description="Show all purchase for a kitty")
    async def showpurchases(self, interaction : discord.Interaction, kitty_name : str) -> discord.message:
        idKitty = await self.get_kitty_id(kitty_name, interaction.channel.name)
        if idKitty is None: # Si la cagnotte n'existe pas on s'arrete
            return await interaction.response.send_message(f"La cagnotte \"{kitty_name}\" n'existe pas")  
        # Récupérer les achats
        cursor = await self.connection.execute("SELECT pseudo, amount, object FROM purchase WHERE idKitty = ?", idKitty)
        purchase_info = await cursor.fetchall()
        # Affichage
        message = f"Achats pour la cagnotte \"{kitty_name}\":\n"
        for pseudo, amount, object in purchase_info:
            message += f"- {pseudo}: \"{object}\" à {amount} euros\n"
        return await interaction.response.send_message(message) 
        
async def setup(bot : commands.Bot) -> None:
        await bot.add_cog(DB(bot, await aiosqlite.connect('Kitty.db')), guild=discord.Object(id=serv_id))