from discord.ext import commands
from discord import Interaction, app_commands, Embed, Colour, Guild, Member, VoiceState, VoiceChannel, CategoryChannel
from discord.message import Message
from ..classes import Buttons
from ..db import database as db


class CreatorRooms(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print(f"{self.__cog_name__} is ready!")
    
    async def create_voice_channel(self, guild: Guild, category: CategoryChannel, channel_name: str) -> VoiceChannel:
        return await guild.create_voice_channel(channel_name, category=category)
    

    def embed(self) -> Embed:
        embed = Embed(color=Colour.from_rgb(0, 0, 0))
        embed.set_author(name = "⚫ Управление каналами")
        embed.add_field(name = "", value = "Вы можете изменить конфигурацию своей комнаты с помощью\nвзаимодествия\n\n👑 一 назначить нового создателя комнаты\n🛗 一 ограничить/выдать доступ к комнате\n \
                        🧑‍🤝‍🧑 一 задать новый лимит участников\n✏️ 一 изменить название комнаты\n📲 一 выгнать участника из комнаты\n🎙️ 一 ограничить/выдать право говорить")
        return embed


    async def delete_voice_channel(self, guild: Guild, channel_id: int) -> None:
        channel = guild.get_channel(int(channel_id))
        await channel.delete()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState) -> None:
        if after.channel is not None and after.channel.id == db.field("SELECT ChannelId FROM roomsCreator WHERE GuildID = (?)", after.channel.guild.id):
            channel = await self.create_voice_channel(guild=after.channel.guild, category=after.channel.category, channel_name=f"Комната {member.name}")
            await channel.send(embed = self.embed(), view = Buttons.Buttons(client=self.client))
            if channel is not None:
                await member.move_to(channel)
                db.execute("INSERT INTO extraRooms VALUES (?, ?, ?, ?)", channel.guild.id, member.id, channel.id, channel.name)
                db.commit()

        if before.channel is not None:
            for channelId in db.column("SELECT ChannelId FROM extraRooms WHERE GuildID = (?)", before.channel.guild.id):
                if len(before.channel.members) == 0 and before.channel.id == channelId:
                    await self.delete_voice_channel(guild=before.channel.guild, channel_id=before.channel.id)
                    db.execute("DELETE FROM extraRooms WHERE ChannelId = (?)", before.channel.id)
                    db.commit()
    
    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        await self.client.process_commands(message)
        if f"<@{self.client.user.id}>" in message.content and type(message.channel) == VoiceChannel:
            await message.channel.send(embed=self.embed(), view=Buttons.Buttons(client = self.client))

    @app_commands.command(name="приват", description="Редактор создания приватных голосовых чатов.")
    @app_commands.describe(
        voiced="Отвечает какому голосовому каналу будет привязана активация"
    )
    async def privateVoices(self, interaction: Interaction, voiced: str) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)
        if (voice := interaction.guild.get_channel(int(voiced))) is not None:
            db.execute("INSERT INTO roomsCreator VALUES (?, ?)", interaction.guild_id, voiced)
            db.commit()
            await interaction.followup.send("Успешно")
            return
        await interaction.followup.send("Неверно введен id")


async def setup(client: commands.Bot) -> None:
    await client.add_cog(CreatorRooms(client))