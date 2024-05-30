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
    creatorName VARCHAR(35),
    channelName VARCHAR(100),
    CHECK (funds >= 0),
    UNIQUE (name, channelName)
    );
    """)
    await connection.commit()

async def create_table_Share(connection : aiosqlite.Connection) -> None:
    await connection.execute("""
    CREATE TABLE IF NOT EXISTS share (
    idKitty INTEGER,
    pseudo VARCHAR(35),
    amount REAL,
    CHECK (amount >= 0),
    PRIMARY KEY (idKitty, pseudo),
    FOREIGN KEY (idKitty) REFERENCES kitty(id)
    );
    """)
    await connection.commit()


async def create_table_Purchase(connection : aiosqlite.Connection) -> None:
    await connection.execute("""
    CREATE TABLE IF NOT EXISTS purchase (
    idPurchase INTEGER PRIMARY KEY,
    idKitty INTEGER,
    pseudo VARCHAR(35),
    amount REAL,
    object TEXT,
    CHECK (amount >= 0),
    FOREIGN KEY (idKitty) REFERENCES kitty(id),
    FOREIGN KEY (pseudo) REFERENCES share(pseudo)       
    );
    """)
    await connection.commit()

async def create_table_DB(connection : aiosqlite.Connection) -> None:
    await create_table_Kitty(connection)
    await create_table_Share(connection)
    await create_table_Purchase(connection)

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