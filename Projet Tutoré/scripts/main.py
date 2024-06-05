import discord
from discord.ext import commands
import aiosqlite

from dotenv import load_dotenv
import os
load_dotenv()
token = os.getenv("BOT_TOKEN")
serv_id = os.getenv("SERV_ID")

async def create_table_Kitty(connection : aiosqlite.Connection) -> None:
    await connection.execute("""
    CREATE TABLE IF NOT EXISTS kitty (
    id INTEGER PRIMARY KEY,
    name TEXT,
    funds REAL DEFAULT 0,
    idCreator INTEGER,
    channelName VARCHAR(100),
    CHECK (funds >= 0),
    UNIQUE (name, channelName)
    FOREIGN KEY (idCreator) REFERENCES user(id)
    );
    """)
    await connection.commit()

async def create_table_Share(connection : aiosqlite.Connection) -> None:
    await connection.execute("""
    CREATE TABLE IF NOT EXISTS share (
    idKitty INTEGER,
    idUser INTEGER,
    amount REAL,
    CHECK (amount >= 0),
    PRIMARY KEY (idKitty, idUser),
    FOREIGN KEY (idKitty) REFERENCES kitty(id)
    FOREIGN KEY (idUser) REFERENCES user(id)
    );
    """)
    await connection.commit()


async def create_table_Purchase(connection : aiosqlite.Connection) -> None:
    await connection.execute("""
    CREATE TABLE IF NOT EXISTS purchase (
    idPurchase INTEGER PRIMARY KEY,
    idKitty INTEGER,
    idUser INTEGER,
    amount REAL,
    object TEXT,
    CHECK (amount >= 0),
    FOREIGN KEY (idKitty) REFERENCES kitty(id),
    FOREIGN KEY (idUser) REFERENCES user(id)
    );
    """)
    await connection.commit()

async def create_table_User(connection : aiosqlite.Connection) -> None:
    await connection.execute("""
    CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY,
    pseudo VARCHAR(35),
    prefer TEXT
    );
    """)
    await connection.commit()

async def create_table_DB(connection : aiosqlite.Connection) -> None:
    await create_table_Kitty(connection)
    await create_table_Share(connection)
    await create_table_Purchase(connection)
    await create_table_User(connection)

class MyBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix="!", intents=discord.Intents.all())

    async def setup_hook(self) -> None:
        await self.load_extension("plugins.DB")
        await self.load_extension("plugins.DB_Debug")
        await self.tree.sync(guild=discord.Object(id=serv_id))
        self.connection = await aiosqlite.connect('Kitty.db')
        await create_table_DB(self.connection)

    async def on_ready(self) -> None:
        print(self.user.name, "est en ligne !")

    async def on_shutdown(self):
        print("Connexion à la base de données fermée.")
        await self.connection.close()

bot = MyBot()

if __name__ == "__main__":
    bot.run(token)