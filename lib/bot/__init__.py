from discord import Game, Intents, Member, Guild
from discord.ext import commands

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.message import Message
from ..db import database as db
from glob import glob

cogs = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")] 

class Bot(commands.Bot):
    def __init__(self):
        self.ready = False
        self.scheduler = AsyncIOScheduler()

        db.autosave(self.scheduler)
        db.build()

        super().__init__(command_prefix="s!", intents=Intents.all())


    async def setup_hook(self):
        for cog in cogs:
            await self.load_extension(f"lib.cogs.{cog}")
        await self.tree.sync()

    def run(self, version):
        self.version = version

        with open("./lib/bot/token", "r", encoding="UTF-8") as t:
            self.token= t.read()

        print("Bot is running...")
        super().run(self.token, reconnect=True)

    async def on_connect(self):
        print("Bot connected")

    async def on_disconnected(self):
        print("Bot disconnected")

    async def on_ready(self):
        if not self.ready:
            self.ready = True
            await self.change_presence(activity=Game(name=f"эволюцию {self.version}"))
            print("Bot ready to use")
            for guild in self.guilds:
                for member in guild.members:
                    if db.record(f"SELECT UserID FROM users WHERE UserID = (?)", member.id) is None:
                        db.execute(f"INSERT INTO users VALUES (?, ?, ?, ?)", member.id, member.name, 0, guild.id)
                        db.commit()
        else:
            print("Bot reconnected")
    
    async def on_message(self, message: Message):
        await self.process_commands(message)
        if not message.author.bot:
            db.execute("UPDATE users SET MessagesAllTime = MessagesAllTime + (?) WHERE UserID = (?)", 1, message.author.id)
            db.commit() 
    
    async def on_guild_join(self, guild: Guild):
        await guild.owner.send("Просьба включить режим разработчика, для отображения ID")
        channel = self.get_channel(1031199800823132160)
        await channel.send(f"Бот был добавлен на сервер ```{guild.name}```")

        for member in guild.members:
            if db.record(f"SELECT UserID FROM users WHERE UserID = (?)", member.id) is None:
                db.execute(f"INSERT INTO users VALUES (?, ?, ?, ?)", member.id, member.name, 0, guild.id)
                db.commit()
    
    async def on_guild_remove(self, guild: Guild):

        channel = self.get_channel(1031199800823132160)
        await channel.send(f"Бот был удален с сервера ```{guild.name}```")

        for member in guild.members:
            db.execute("DELETE FROM users where UserID = (?)", member.id)

    async def on_member_join(self, member: Member):
        db.execute(f"INSERT INTO users VALUES (?, ?, ?, ?)", member.id, member.name, 0, member.guild.id)
        db.commit()
    
    async def on_member_leave(self, member: Member):
        db.execute(f"DELETE FROM users where UserID = (?)", member.id)
        db.commit()