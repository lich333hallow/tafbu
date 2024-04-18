from discord.ext import commands
from discord import Interaction, Embed, Colour, Status, Member, Object, app_commands
from typing import Optional
from json import load
from os.path import join
from sqlite3 import OperationalError
from ..db import database as db

class Commands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        with open(join("data/json/commands.json"), "r", encoding="utf-8") as json:
            self.c_info = load(json)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__cog_name__} cog is ready!")

    @app_commands.command(name="сервер", description="Показывает статистику сервера.")
    @app_commands.describe()
    async def server(self, interaction: Interaction):
        await interaction.response.defer(thinking=True)
        embed = Embed(color=Colour.from_rgb(0, 0, 0))
        live_members = list(filter(lambda x: x.bot == False, interaction.guild.members))
        administrators = list(filter(lambda x: x.guild_permissions.administrator == True and x.name != interaction.guild.owner.name, live_members))
        embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon.url)
        embed.add_field(
            name="👑 АДМИНИСТРАЦИЯ",
            value=f"```" + ", ".join([i.name for i in administrators]) + "```",
            inline=False
        )
        embed.add_field(
            name=f"👥  УЧАСТНИКИ: [{interaction.guild.member_count}]",
            value=f"```Онлайн: {len(list(filter(lambda x: x.status == Status.online, interaction.guild.members)))} | "
                f"Оффлайн: {len(list(filter(lambda x: x.status == Status.offline, interaction.guild.members)))} | "
                f"Боты: {len(list(filter(lambda x: x.bot == True, interaction.guild.members)))}"
                "```",
            inline=False
        )
        embed.add_field(
            name=f"📊 КАНАЛЫ И КАТЕГОРИИ: [{len(interaction.guild.channels)}]",
            value=f"```Текст: {len(interaction.guild.text_channels)} | "
            f"Форум: {len(interaction.guild.forums)} | "
            f"Объявление: {len(list(filter(lambda x: x.is_news() == True, interaction.guild.text_channels)))}```"
            f"```Категории: {len(interaction.guild.categories)} | "
            f"Голосовые: {len(interaction.guild.voice_channels)} | "
            f"Сцены: {len(interaction.guild.stage_channels)}```",
            inline=False
        )
        embed.add_field(
            name=f"🎭 РОЛИ НА СЕРВЕРЕ: [{len(interaction.guild.roles)}]",
            value="```" + ",\n".join([i.name for i in interaction.guild.roles]) + "```",
            inline=False
        )
        embed.add_field(
            name=f"🪄 ЭМОДЗИ И СТИКЕРЫ: [{len(interaction.guild.emojis)}]",
            value=f"```Обычные: {len(list(filter(lambda x: x.animated == False, interaction.guild.emojis)))} | "
            f"Анимированные: {len(list(filter(lambda x: x.animated == True, interaction.guild.emojis)))} | "
            f"Стикеры: {len(interaction.guild.stickers)}```",
            inline=False
        )
        embed.add_field(
            name=f"🗓️ДАТА СОЗДАНИЯ",
            value=f"```{interaction.guild.created_at.day} | {interaction.guild.created_at.month} | {interaction.guild.created_at.year}```",
            inline=False
        )
        embed.set_thumbnail(url=interaction.guild.icon.url)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="очистка", description="Очищает сообщения из канала.")
    @app_commands.describe(
        number="Отвечает сколько сообщений будет удалено"
    )
    async def purge(self, interaction: Interaction, number: Optional[int] = 1):
        await interaction.response.defer(ephemeral=True, thinking=True)
        await interaction.channel.purge(limit=number)
        await interaction.followup.send(f"```Успешно удалено {number} сообщений!```", ephemeral=True)

    @app_commands.command(name="аватар", description="Отправляет картинку пользователя")
    @app_commands.describe(
        mem="Отвечает аватарка какого пользователя будет отправлена"
    )
    async def avatar(self, interaction: Interaction, mem: Optional[Member] = None):
        await interaction.response.defer(thinking=True)
        if mem is None:
            mem = interaction.user
        embed = Embed(color=Colour.from_rgb(0, 0, 0))
        embed.set_author(
            name=f"{mem.name}",
            icon_url=mem.avatar.url
        )
        embed.set_image(url=mem.avatar.url)
        embed.set_footer(text=f"Запрошено {interaction.user.name}", icon_url=interaction.user.avatar.url)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="список", description="Показывает статистику")
    @app_commands.guilds(Object(1031195234379513937))
    async def guild_info(self, interaction: Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)
        info = "\n".join([guild.name for guild in self.client.guilds]), sum([1 for _ in self.client.guilds])
        await interaction.followup.send(info)

    @app_commands.command(name="сброс", description="Сбрасывает активные команды")
    @app_commands.describe(
        command_name="Название команды, которую надо сбросить"
    )
    async def reboot(self, interaction: Interaction, command_name: str):
        await interaction.response.defer(thinking=True, ephemeral=True)
        commands = ["роль", "приват", "rss"]
        if command_name not in commands:
            await interaction.followup.send("Неправильная команда")
            return

        if command_name == commands[0]:
            for channelId in db.column("SELECT ChannelId FROM rolesIDs WHERE GuildID = (?)", interaction.guild_id):
                channel = interaction.guild.get_channel(int(channelId))
                try:
                    mess = await channel.fetch_message(int(db.record("SELECT MessageId FROM rolesIDs WHERE GuildID = (?) AND ChannelId = (?)", interaction.guild_id, channelId)[0]))
                except TypeError:
                    await interaction.followup.send("Что-то пошло не так...")
                await mess.clear_reactions()
                db.execute("DELETE FROM rolesIDs WHERE ChannelId = (?)", channelId)
                db.commit()

        elif command_name == commands[1]:
            for channelId in db.column("SELECT ChannelId FROM roomsCreator WHERE GuildID = (?)", interaction.guild_id):
                db.execute("DELETE FROM roomsCreator WHERE ChannelId = (?)", channelId)
                db.commit()

        elif command_name == commands[2]:
            for channelId in db.column("SELECT ChannelId FROM rss WHERE GuildID = (?)", interaction.guild_id):
                db.execute("DELETE FROM rss WHERE ChannelId = (?)", channelId)
                db.commit()

        await interaction.followup.send("Успешно!")
        return

    @app_commands.command(name="помощь", description="Команды для работы")
    @app_commands.describe()
    async def help(self, interaction: Interaction):
        await interaction.response.defer(thinking=True)
        embed = Embed(title="Список команд", description="Ниже приведен список всех команд, описание и пример команды (на ветках не работают).\nБот может сбрасывать все команды при отключении.")
        for dict_ in self.c_info:
            embed.add_field(
                name="",
                value=dict_["description"],
                inline=False
            )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="статус", description="Показывает команды, которые работают на сервере")
    @app_commands.describe()
    async def status(self, interaction: Interaction):
        await interaction.response.defer(thinking=True)
        c = []
        mess = ""
        for dict_ in self.c_info:
            key = dict_["db_table"]
            if key == False:
                continue
            try:
                check = db.records(f"SELECT ChannelId FROM {key} WHERE GuildID = ?", interaction.guild_id)
                print(check)
                c.append((dict_["command_name"], "активно") if check else (dict_["command_name"], "неактивно"))
            except OperationalError:
                c.append((dict_["command_name"], "неактивно"))
        
        for tuple_ in c:
            mess += f"{tuple_[0]}: {tuple_[1]}\n"
        
        await interaction.followup.send(mess)



async def setup(client: commands.Bot):
    await client.add_cog(Commands(client))

