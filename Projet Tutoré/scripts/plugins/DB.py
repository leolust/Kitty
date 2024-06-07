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
    
    async def get_user_id(self, pseudo):
        cursor = await self.connection.execute("SELECT id FROM user WHERE pseudo=?", (pseudo,))
        return await cursor.fetchone()

    async def get_user_name(self, id):
        cursor = await self.connection.execute("SELECT pseudo FROM user WHERE id=?", (id,))
        return await cursor.fetchone()
    
    ###################################################### ADDME ######################################################
    @app_commands.command(name="kittyaddme", description="Add you as a kitty user")
    async def kittyaddme(self, interaction : discord.Interaction) -> discord.message:
        idUser = await self.get_user_id(interaction.user.name)
        if idUser is not None:
            return await interaction.response.send_message(f"Vous êtes déjà enregistré")
        await self.connection.execute("""
        INSERT INTO user (pseudo) VALUES (?)
        """, (interaction.user.name,)
        )
        await self.connection.commit()
        return await interaction.response.send_message(f"Vous êtes enregistré comme utilisateur de ce bot, vous pouvez désormais utiliser toutes ses fonctionnalitées")

    ###################################################### CREATE ######################################################
    @app_commands.command(name="createkitty", description="creates a kitty")
    async def createKitty(self, interaction : discord.Interaction, kitty_name : str) -> discord.message:
        idUser = await self.get_user_id(interaction.user.name)
        if idUser is None: # Si l'utilisateur n'est pas enregistré
            return await interaction.response.send_message(f"Avant d'utiliser les commandes de ce bot, veuillez vous enregistrer avec la commande /kittyaddme")
        id = await self.get_kitty_id(kitty_name, interaction.channel.name)
        if id is not None:
            return await interaction.response.send_message(f"La cagnotte \"{kitty_name}\" existe déjà ")
        await self.connection.execute("""
        INSERT INTO kitty (name, idCreator, channelName) VALUES (?, ?, ?)
        """, (kitty_name, idUser[0], interaction.channel.name)
        )
        await self.connection.commit()
        return await interaction.response.send_message(f"La cagnotte \"{kitty_name}\" à été créé par {interaction.user.mention}")

    ###################################################### PARTICIPATE ######################################################
    @app_commands.command(name="participate", description="Register your participation for a kitty")
    async def participate(self, interaction : discord.Interaction, kitty_name : str, amount : float) -> discord.message:
        idUser = await self.get_user_id(interaction.user.name)
        if idUser is None: # Si l'utilisateur n'est pas enregistré
            return await interaction.response.send_message(f"Avant d'utiliser les commandes de ce bot, veuillez vous enregistrer avec la commande /kittyaddme")
        idKitty = await self.get_kitty_id(kitty_name, interaction.channel.name)
        if idKitty is None: # Si la cagnotte n'existe pas on s'arrete
            return await interaction.response.send_message(f"La cagnotte \"{kitty_name}\" n'existe pas")
        amount = round(amount, 2)
        try:
            # Mise à jour de la cagnotte
            await self.connection.execute("""
            UPDATE kitty SET funds = funds + ? WHERE id = ?
            """, (amount, idKitty[0]))
            cursor = await self.connection.execute("SELECT amount FROM share WHERE idKitty=? AND idUser=?", (idKitty[0], idUser[0]))
            oldAmount = await cursor.fetchone()
            # Insertion ou mise à jour de la participation
            if oldAmount:
                amount += oldAmount[0]
                await self.connection.execute("""
                UPDATE share SET amount = ? WHERE idKitty = ? AND idUser = ?
                """, (amount, idKitty[0], idUser[0]))
            else:
                await self.connection.execute("""
                INSERT INTO share VALUES (?, ?, ?)
                """, (idKitty[0], idUser[0], amount))
            await self.connection.commit()
        except sqlite3.IntegrityError as e:
            return await interaction.response.send_message("Action Impossible, vérifez la cohérence de votre commande (exemple: montant négatif)")
        return await interaction.response.send_message(f"Votre participation totale à la cagnotte \"{kitty_name}\" est de {amount} euros")

    ###################################################### PURCHASE ######################################################
    @app_commands.command(name="purchase", description="Add a purchase for a kitty")
    async def purchase(self, interaction : discord.Interaction, kitty_name : str, object : str, amount : float) -> discord.message:
        amount = round(amount, 2)
        if amount <= 0:
            return await interaction.response.send_message("Action Impossible: montant invalide")
        idUser = await self.get_user_id(interaction.user.name)
        if idUser is None: # Si l'utilisateur n'est pas enregistré
            return await interaction.response.send_message(f"Avant d'utiliser les commandes de ce bot, veuillez vous enregistrer avec la commande /kittyaddme")
        idKitty = await self.get_kitty_id(kitty_name, interaction.channel.name)
        if idKitty is None: # Si la cagnotte n'existe pas on s'arrete
            return await interaction.response.send_message(f"La cagnotte \"{kitty_name}\" n'existe pas")
        cursor = await self.connection.execute("SELECT amount FROM share WHERE idKitty=? AND idUser=?", (idKitty[0], idUser[0]))
        isInShare = await cursor.fetchone()
        if isInShare is None: # Si l'utilisateur ne participe pas à la cagnotte
            return await interaction.response.send_message("Vous ne pouvez pas dépenser pour une cagnotte si vous n'y participez pas")
        try:
            # Insertion de l'achat
            await self.connection.execute("""
            INSERT INTO purchase (idKitty, idUser, amount, object) VALUES (?, ?, ?, ?)
            """, (idKitty[0], idUser[0], amount, object))
            # Mise à jour de la cagnotte
            await self.connection.execute("""
            UPDATE kitty SET funds = ROUND(funds - ?, 2) WHERE id = ?
            """, (amount, idKitty[0]))
            await self.connection.commit()
        except sqlite3.IntegrityError as e:
            return await interaction.response.send_message("Action Impossible, vérifez la cohérence de votre commande (exemple: fonds insuffisant)")
        return await interaction.response.send_message(f"{interaction.user.mention} a dépensé {amount} euros de la cagnotte \"{kitty_name}\" pour l'achat de \"{object}\"")

    ###################################################### CALCULATE ######################################################
    @app_commands.command(name="calculate", description="Calculate the transactions")
    async def calculate(self, interaction : discord.Interaction, kitty_name : str) -> discord.message:
        idUser = await self.get_user_id(interaction.user.name)
        if idUser is None: # Si l'utilisateur n'est pas enregistré
            return await interaction.response.send_message(f"Avant d'utiliser les commandes de ce bot, veuillez vous enregistrer avec la commande /kittyaddme")
        idKitty = await self.get_kitty_id(kitty_name, interaction.channel.name)
        if idKitty is None: # Si la cagnotte n'existe pas on s'arrete
            return await interaction.response.send_message(f"La cagnotte \"{kitty_name}\" n'existe pas")
        # Récupérer les contributions depuis la table share
        cursor = await self.connection.execute("SELECT idUser, amount FROM share WHERE idKitty=?", idKitty)
        BDDcontrib = await cursor.fetchall()
        if BDDcontrib is None:
            return await interaction.response.send_message(f"La cagnotte \"{kitty_name}\" ne contient pas de participations")
        # Récupérer les dépenses depuis la table purchase
        cursor = await self.connection.execute("SELECT idUser, amount FROM purchase WHERE idKitty=?", idKitty)
        BDDexpenses = await cursor.fetchall()
        if BDDexpenses is None:
            return await interaction.response.send_message(f"La cagnotte \"{kitty_name}\" ne contient pas d'achats")
        # Formatter les données sous forme de dictionnaires
        contributions = {pseudo: amount for pseudo, amount in BDDcontrib}
        expenses = {pseudo: amount for pseudo, amount in BDDexpenses}
        # Calculer les transactions
        repayments = repayment.repayment(contributions, expenses)
        # Afficher les transactions
        res = f"Voici les transactions à effectuer pour la cagnotte \"{kitty_name}\" :\n"
        for idDebtor, idCreditor, amount in repayments:
            debtor = await self.get_user_name(idDebtor)
            creditor = await self.get_user_name(idCreditor)
            memberDebtor = interaction.guild.get_member_named(debtor[0])
            memberCreditor = interaction.guild.get_member_named(creditor[0])
            res += f"{memberDebtor.mention if memberDebtor is not None else debtor[0]} doit rembourser {amount} euros à {memberCreditor.mention if memberCreditor is not None else creditor}\n"
        return await interaction.response.send_message(f"{res}")
    
    ###################################################### DELETE ######################################################
    @app_commands.command(name="kittydelete", description="Delete a kitty")
    async def kittydelete(self, interaction : discord.Interaction, kitty_name : str) -> discord.message:
        idUser = await self.get_user_id(interaction.user.name)
        if idUser is None: # Si l'utilisateur n'est pas enregistré
            return await interaction.response.send_message(f"Avant d'utiliser les commandes de ce bot, veuillez vous enregistrer avec la commande /kittyaddme")
        idKitty = await self.get_kitty_id(kitty_name, interaction.channel.name)
        if idKitty is None: # Si la cagnotte n'existe pas on s'arrete
            return await interaction.response.send_message(f"La cagnotte \"{kitty_name}\" n'existe pas")
        # Verification du droit de fermeture
        cursor = await self.connection.execute("SELECT idCreator FROM kitty WHERE id = ?", idKitty)
        creator = await cursor.fetchone()
        if (creator[0] != idUser[0]):
            return await interaction.response.send_message(f"Vous n'avez pas les droits pour fermer la cagnotte \"{kitty_name}\"")
        # Suppression de la cagnotte
        rename = str(idKitty[0]) + ":" + interaction.channel.name
        await self.connection.execute("""
        UPDATE kitty SET channelName = ? WHERE id = ?
        """, (rename, idKitty[0]))
        await self.connection.commit()
        return await interaction.response.send_message(f"La cagnotte \"{kitty_name}\" a été fermée")

    ###################################################### SHOWKITTY ######################################################
    @app_commands.command(name="showkitty", description="Show informations about a kitty")
    async def kittyshow(self, interaction : discord.Interaction, kitty_name : str) -> discord.message:
        idUser = await self.get_user_id(interaction.user.name)
        if idUser is None: # Si l'utilisateur n'est pas enregistré
            return await interaction.response.send_message(f"Avant d'utiliser les commandes de ce bot, veuillez vous enregistrer avec la commande /kittyaddme")
        idKitty = await self.get_kitty_id(kitty_name, interaction.channel.name)
        if idKitty is None: # Si la cagnotte n'existe pas on s'arrete
            return await interaction.response.send_message(f"La cagnotte \"{kitty_name}\" n'existe pas")
        # Récupérer les informations de la cagnotte
        cursor = await self.connection.execute("SELECT name, funds, idCreator FROM kitty WHERE id = ?", idKitty)
        kitty_info = await cursor.fetchone()
        # Récupérer le pseudo du créateur
        creator = await self.get_user_name(kitty_info[2])
        memberCreator = interaction.guild.get_member_named(creator[0])
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
            f"- Créateur: {memberCreator.display_name if memberCreator is not None else creator[0]}\n"
            f"- Participation totale: {total_contrib}\n"
            f"- Dépenses totales: {total_expenses}\n"
            f"- Fonds restants: {kitty_info[1]}"
        )
        return await interaction.response.send_message(message)

    ###################################################### SHOWSHARES ######################################################
    @app_commands.command(name="showshares", description="Show all shares for a kitty")
    async def showshares(self, interaction : discord.Interaction, kitty_name : str) -> discord.message:
        idUser = await self.get_user_id(interaction.user.name)
        if idUser is None: # Si l'utilisateur n'est pas enregistré
            return await interaction.response.send_message(f"Avant d'utiliser les commandes de ce bot, veuillez vous enregistrer avec la commande /kittyaddme")
        idKitty = await self.get_kitty_id(kitty_name, interaction.channel.name)
        if idKitty is None: # Si la cagnotte n'existe pas on s'arrete
            return await interaction.response.send_message(f"La cagnotte \"{kitty_name}\" n'existe pas") 
        # Récupérer les participations
        cursor = await self.connection.execute("SELECT idUser, amount FROM share WHERE idKitty = ?", idKitty)
        share_info = await cursor.fetchall()
        # Affichage
        message = f"Participations pour la cagnotte \"{kitty_name}\":\n"
        for idUser, amount in share_info:
            pseudo = await self.get_user_name(idUser)
            memberPseudo = interaction.guild.get_member_named(pseudo[0])
            message += f"- {memberPseudo.display_name if memberPseudo is not None else pseudo[0]}: {amount}\n"
        return await interaction.response.send_message(message)
    
    ###################################################### SHOWPURCHASES ######################################################
    @app_commands.command(name="showpurchases", description="Show all purchase for a kitty")
    async def showpurchases(self, interaction : discord.Interaction, kitty_name : str) -> discord.message:
        idUser = await self.get_user_id(interaction.user.name)
        if idUser is None: # Si l'utilisateur n'est pas enregistré
            return await interaction.response.send_message(f"Avant d'utiliser les commandes de ce bot, veuillez vous enregistrer avec la commande /kittyaddme")
        idKitty = await self.get_kitty_id(kitty_name, interaction.channel.name)
        if idKitty is None: # Si la cagnotte n'existe pas on s'arrete
            return await interaction.response.send_message(f"La cagnotte \"{kitty_name}\" n'existe pas")  
        # Récupérer les achats
        cursor = await self.connection.execute("SELECT idUser, amount, object FROM purchase WHERE idKitty = ?", idKitty)
        purchase_info = await cursor.fetchall()
        # Affichage
        message = f"Achats pour la cagnotte \"{kitty_name}\":\n"
        for idUser, amount, object in purchase_info:
            pseudo = await self.get_user_name(idUser)
            memberPseudo = interaction.guild.get_member_named(pseudo[0])
            message += f"- {memberPseudo.display_name if memberPseudo is not None else pseudo[0]}: \"{object}\" à {amount} euros\n"
        return await interaction.response.send_message(message) 
    
    ###################################################### KITTYME ######################################################
    @app_commands.command(name="kittyme", description="Show all the kitty you participate in")
    async def kittyme(self, interaction : discord.Interaction) -> discord.message:
        idUser = await self.get_user_id(interaction.user.name)
        if idUser is None: # Si l'utilisateur n'est pas enregistré
            return await interaction.response.send_message(f"Avant d'utiliser les commandes de ce bot, veuillez vous enregistrer avec la commande /kittyaddme", ephemeral=True)
        cursor = await self.connection.execute("SELECT DISTINCT name, channelName FROM kitty JOIN share ON id = idKitty WHERE idUser = ? AND channelName NOT LIKE '%:%'", idUser)
        kitty_share = await cursor.fetchall()
        cursor = await self.connection.execute("SELECT name, channelName FROM kitty WHERE idCreator = ? AND channelName NOT LIKE '%:%'", idUser)
        kitty_create = await cursor.fetchall()
        # Affichage
        message = f"Vous apparaissez dans les cagnottes suivantes:\n"
        for name, channel in kitty_create:
            message += f"- Vous avez créé la cagnotte \"{name}\" sur le channel \"{channel}\"\n"
        for name, channel in kitty_share:
            message += f"- Vous participez à la cagnotte \"{name}\" sur le channel \"{channel}\"\n"
        return await interaction.response.send_message(message, ephemeral=True) 

    ###################################################### KITTYCLOSETO ######################################################
    @app_commands.command(name="kittycloseto", description="Add someone to your close friends list")
    async def kittycloseto(self, interaction : discord.Interaction, friend: discord.Member = None) -> discord.message:
        idUser = await self.get_user_id(interaction.user.name)
        if idUser is None: # Si l'utilisateur n'est pas enregistré
            return await interaction.response.send_message(f"Avant d'utiliser les commandes de ce bot, veuillez vous enregistrer avec la commande /kittyaddme", ephemeral=True)
        if friend is None:
            message = f"Voici la liste des personnes que vous avez ajouté en amis proches: \n"
            cursor = await self.connection.execute("SELECT user2 FROM closeto WHERE user1=?", idUser)
            friendList = await cursor.fetchall()
            for friendId in friendList:
                pseudo = await self.get_user_name(friendId[0])
                memberPseudo = interaction.guild.get_member_named(pseudo[0])
                message += f"{memberPseudo.mention if memberPseudo is not None else pseudo[0]}\n"
            return await interaction.response.send_message(message, ephemeral=True)
        idFriend = await self.get_user_id(friend.name)
        if idFriend is None:
            return await interaction.response.send_message(f"La personne que vous voulez ajouter n'est pas enregistré dans le bot {friend.name}", ephemeral=True)
        if idUser == idFriend:
            return await interaction.response.send_message(f"Impossible de s'ajouter sois-même... (arretez vos bêtises !)", ephemeral=True)
        cursor = await self.connection.execute("SELECT user1 FROM closeto WHERE user1=? AND user2=?", (idUser[0], idFriend[0]))
        already = await cursor.fetchone()
        if already:
            await self.connection.execute("""
            DELETE FROM closeto WHERE user1=? AND user2=?
            """, (idUser[0], idFriend[0]))
            message = f"{friend.mention} a été retiré de votre liste d'amis proches\n"
        else:
            await self.connection.execute("""
            INSERT INTO closeto VALUES (?, ?)
            """, (idUser[0], idFriend[0]))
            message = f"{friend.mention} a été ajouté à votre liste d'amis proches\n"
        await self.connection.commit()
        return await interaction.response.send_message(message, ephemeral=True)
    
    ###################################################### KITTYHELP ######################################################
    @app_commands.command(name="kittyhelp", description="Display help to use the bot")
    async def kittyhelp(self, interaction : discord.Interaction) -> discord.message:
        message = f"# Ce bot permet de créer et gérer des cagnottes #\n" 
        message += f"Dans un premier temps, enregistrez vous avec la commande: ```/kittyaddme```vous aurez ensuite accès aux commandes suivantes:\n\n"
        message += f"```/createkitty [kitty_name]```"
        message += f"Permet de créer une cagnotte en lui donnant un nom. Le bot renvoie un message pour confirmer la création de la cagnotte, ou pour indiquer qu’elle n’a pas pu être créée.\n\n"
        message += f"```/participate [kitty_name] [amount]```"
        message += f"Permet de participer à un cagnotte en indiquant le nom de la cagnotte et le montant que l’on souhaite. Il est possible de diminuer sa participation en entrant une valeur négative, sauf si l’argent a déjà été dépensée. Le bot renvoie un message pour préciser si la participation a été validée ou invalidée.\n\n"
        message += f"```/purchase [kitty_name] [object] [amount]```"
        message += f"Permet d’ajouter une dépense à une cagnotte, en précisant le nom de la cagnotte, l’objet de la dépense ainsi que son montant. Le bot renvoie un message pour préciser si la dépense a été validée ou invalidée.\n\n"
        message += f"```/calculate [kitty_name]```"
        message += f"Permet de calculer et d’afficher les transactions minimum à faire pour que les participant d’un cagnotte donnée se remboursent.\n\n"
        message += f"```/kittydelete [kitty_name]```"
        message += f"Permet de supprimer une cagnotte donnée si vous en êtes le créateur.\n\n"
        message += f"```/showkitty [kitty_name]```"
        message += f"Affiche les informations d’une cagnotte donnée. Son créateur, le total des participations, le total des dépenses, et les fonds restants.\n\n"
        message += f"```/showshares [kitty_name]```"
        message += f"Affiche chaque participation à une cagnotte donnée (participant et montant).\n\n"
        message += f"```/showpurchase [kitty_name]```"
        message += f"Affiche les dépenses d’une cagnotte donnée (acheteur, objet et montant).\n\n"
        message += f"```/kittyme```"
        message += f"Affiche toutes les cagnottes créée par l’utilisateur, ainsi que toutes les cagnottes auxquelles il a participé (l’utilisateur est le seul à voir la réponse du bot).\n\n"
        message += f"```/kittycloseto```"
        message += f"A venir..."
        return await interaction.response.send_message(message, ephemeral=True)
    
async def setup(bot : commands.Bot) -> None:
        await bot.add_cog(DB(bot, await aiosqlite.connect('Kitty.db')), guild=discord.Object(id=serv_id))