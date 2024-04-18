from discord.ext import commands
from discord import app_commands, Interaction, RawReactionActionEvent, PartialEmoji
from ..db import database as db


class RolesIds(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__cog_name__} cog is ready!")

    def get_info(self, payload: RawReactionActionEvent) -> tuple:
        guild = self.client.get_guild(payload.guild_id)
        if (emoji := db.field("SELECT EmojiCode FROM rolesIDs WHERE GuildID = (?) AND MessageId = (?)", payload.guild_id, payload.message_id)) is not None:
            emoji = emoji.decode("unicode-escape")
        mess = db.field("SELECT MessageId FROM rolesIDs WHERE GuildID = (?) AND MessageId = (?)", payload.guild_id, payload.message_id)
        member = guild.get_member(payload.user_id)
        if (role := guild.get_role(db.field("SELECT RoleID FROM rolesIDs WHERE GuildID = (?) AND MessageId = (?)", payload.guild_id, payload.message_id))) is not None:
            return emoji, mess, role, member
        return emoji, mess, member

    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        try:
            emoji, mess, role, member = self.get_info(payload)
        except ValueError:
            pass
        if payload.message_id == mess and emoji == str(payload.emoji) and payload.member.bot == False:
            await member.add_roles(role)

    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent):
        try:
            emoji, mess, role, member = self.get_info(payload)
        except ValueError:
            pass
        if payload.message_id == mess and emoji == str(payload.emoji):  
            await member.remove_roles(role)

    @app_commands.command(name="роль", description="Редактор выдачи роли.")
    @app_commands.describe(
        messaged="Отвечает какому сообщению будет привязана активация роли",
        channeld="К какому каналу будет применяться ",
        roled="Отвечает какая роль будет выдаваться",
        emoji="Отвечает за какую эмодзи будет выполнять действия для выдачи роли"
    )
    async def setuprole(self, interaction: Interaction, messaged: str, channeld: str, roled: str, emoji: str):
        await interaction.response.defer(thinking=True, ephemeral=True)
        for channel in db.column("SELECT ChannelId FROM rolesIDs WHERE GuildID = (?)", interaction.guild_id):
            if interaction.guild.get_channel(int(channel)) is None:
                db.execute("DELETE FROM rolesIDs WHERE ChannelId = (?)", channel)
                db.commit()
        if ((channel := interaction.guild.get_channel(int(channeld))) is not None) and ((mess := await channel.fetch_message(int(messaged))) is not None):
            if type(emoji) == PartialEmoji:
                emoji = await interaction.guild.fetch_emoji(emoji.id)
                db.execute(f"INSERT INTO rolesIDs VALUES (?, ?, ?, ?, ?)", interaction.guild_id, roled, messaged, channeld, emoji.id)
            else:
                db.execute(f"INSERT INTO rolesIDs VALUES (?, ?, ?, ?, ?)", interaction.guild_id, roled, messaged, channeld, emoji.encode('unicode-escape'))
                db.commit()
            await mess.add_reaction(emoji)
            await interaction.followup.send("Успешно!")
            return
        await interaction.followup.send("Неверно указаны id")



async def setup(client: commands.Bot):
    await client.add_cog(RolesIds(client))
