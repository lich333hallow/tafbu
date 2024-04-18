from discord import ui, Interaction, utils, Client, PartialEmoji, HTTPException, PermissionOverwrite
from ..db import database as db


class Buttons(ui.View):
    def __init__(self, client: Client, timeout=None):
        self.client = client
        super().__init__(timeout=timeout)
    
    @ui.button(emoji=PartialEmoji(name="Lider", id=1144690922769096765), row=1)
    async def owner_callback(self, interaction: Interaction, button):
        user = interaction.user
        channels = db.field("SELECT ChannelId FROM extraRooms WHERE MemberID = (?)", interaction.user.id)
        if channels is not None:
            channel = self.client.get_channel(channels)
            await channel.set_permissions(user, manage_channels=False)
            del_ = await channel.send("Кому передать права?")
            msg1 = await self.client.wait_for("message", timeout=30.0, check=lambda x: x.author == interaction.user and interaction.channel == x.channel)
            new_user = await self.client.fetch_user(int(msg1.content[2:-1]))
            await channel.set_permissions(new_user, manage_channels=True)
            db.execute("UPDATE extraRooms SET MemberID = (?) WHERE ChannelId = (?)", new_user.id, channels)
            await del_.delete()
            await msg1.reply("Успешно!")
            return
        await interaction.followup.send("Вы не являетесь создателем комнаты")

    @ui.button(emoji=PartialEmoji(name="Member", id=1144691012699168888), row=1)
    async def limit_access_button(self, interaction: Interaction, button):
        user = interaction.user
        channels = db.field("SELECT ChannelId FROM extraRooms WHERE MemberID = (?)", interaction.user.id)
        if channels is not None:
            channel = self.client.get_channel(channels)
            del_ = await channel.send("Пинганите того, кому ограничить право заходить в эту комнату")
            msg = await self.client.wait_for("message", timeout=30.0, check=lambda x: x.author == user and interaction.channel == x.channel)
            member = utils.get(self.client.get_all_members(), id=int(msg.content[2:-1]))
            if channel.permissions_for(member).connect:
                await channel.set_permissions(member, connect=False)
            else:
                await channel.set_permissions(member, connect=True)
            await del_.delete()
            await msg.reply("Успешно!")
            return
        await interaction.followup.send("Вы не являетесь создателем комнаты")

    @ui.button(emoji=PartialEmoji(name="Players", id=1144691060744913087), row=1)
    async def limit_callback(self, interaction: Interaction, button):
        user = interaction.user
        channels = db.field("SELECT ChannelId FROM extraRooms WHERE MemberID = (?)", interaction.user.id)
        if channels is not None:
            channel = self.client.get_channel(channels)
            del_ = await channel.send("Укажите новый лимит пользователей")
            try:
                msg = await self.client.wait_for("message", timeout=30.0, check=lambda x: x.author == user and interaction.channel == x.channel)
            except HTTPException:
                await interaction.followup.send("Некорректный лимит")
                return
            await channel.edit(user_limit=int(msg.content))
            await del_.delete()
            await msg.reply("Успешно!")
            return
        await interaction.followup.send("Вы не являетесь создателем комнаты")


    @ui.button(emoji=PartialEmoji(name="Name", id=1144691110690685098), row=2)
    async def rename_callback(self, interaction: Interaction, button):
        user = interaction.user
        channels = db.field("SELECT ChannelId FROM extraRooms WHERE MemberID = (?)", interaction.user.id)
        if channels is not None:
            channel = self.client.get_channel(channels)
            del_ = await channel.send("Укажите новое название")
            msg = await self.client.wait_for("message", timeout=30.0, check=lambda x: x.author == user and interaction.channel == x.channel)
            await channel.edit(name=str(msg.content))
            await del_.delete()
            await msg.reply("Успешно!")
            return
        await interaction.followup.send("Вы не являетесь создателем комнаты")

    @ui.button(emoji=PartialEmoji(name="Exit", id=1144691169461284864), row=2)
    async def kick_callback(self, interaction: Interaction, button):
        user = interaction.user
        channels = db.field("SELECT ChannelId FROM extraRooms WHERE MemberID = (?)", interaction.user.id)
        if channels is not None:
            channel = self.client.get_channel(channels)
            del_ = await channel.send("Пинганите участника, которого хотите кикнуть")
            msg = await self.client.wait_for("message", timeout=30.0, check=lambda x: x.author == user and interaction.channel == x.channel)
            member = utils.get(channel.members, id=int(msg.content[2:-1]))
            await member.move_to(None)
            await del_.delete()
            await msg.reply("Успешно!")
            return
        await interaction.followup.send("Вы не являетесь создателем комнаты")


    @ui.button(emoji=PartialEmoji(name="Voice", id=1144691216399740928), row=2)
    async def mute_callback(self, interaction: Interaction, button):
        user = interaction.user
        channels = db.field("SELECT ChannelId FROM extraRooms WHERE MemberID = (?)", interaction.user.id)
        print(channels)
        if channels is not None:
            channel = self.client.get_channel(channels)
            del_ = await channel.send("Пинганите участника, которого хотите замутить")
            msg = await self.client.wait_for("message", timeout=30.0, check=lambda x: x.author == user and interaction.channel == x.channel)
            member = utils.get(channel.members, id=int(msg.content[2:-1]))
            if member.voice.mute:
                await member.edit(mute=False)
            else:
                await member.edit(mute=True)
            await del_.delete()
            await msg.reply("Успешно!")
            return
        await interaction.followup.send("Вы не являетесь создателем комнаты")