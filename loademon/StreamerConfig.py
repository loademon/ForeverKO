import discord
from discord.interactions import Interaction
import redis.asyncio as redis


STREAMER_ROLE_ID = 1185606987212394577


OWNER_ROLE_ID = 1185604201242431608
ADMIN_ROLE_ID = 1185605115302924440


async def get_user_id(redis: redis.Redis, inter: discord.Interaction):
    return (
        (await redis.hget(name="Streamer Interactions", key=inter.message.id)).decode(
            "utf-8"
        )
        if (await redis.hget(name="Streamer Interactions", key=inter.message.id))
        is not None
        else None
    )


async def check_user_id(redis: redis.Redis, inter: discord.Interaction):
    user_id = await get_user_id(redis=redis, inter=inter)
    if user_id == None:
        raise await inter.response.send_message(
            "Beklenmeyen bir hata oluştu.", ephemeral=True
        )
    return user_id


async def get_user_status(redis: redis.Redis, inter: discord.Interaction, user_id: str):
    return (
        (await redis.hget(name="Streamer Status", key=user_id)).decode("utf-8")
        if (await redis.hget(name="Streamer Status", key=user_id)) is not None
        else None
    )


async def check_user_status(
    redis: redis.Redis, inter: discord.Interaction, user_id: str
):
    user_status = await get_user_status(redis=redis, inter=inter, user_id=user_id)
    if user_status == None:
        raise await inter.response.send_message(
            "Beklenmeyen bir hata oluştu.", ephemeral=True
        )

    if user_status == "Kabul Edildi" or user_status == "Reddedildi":
        raise await inter.response.send_message(
            f"Kullanıcının başvurusu zaten yanıtlanmış: **{user_status}**",
            ephemeral=True,
        )

    return user_status


async def add_editor_role(inter: discord.Interaction, user_id: int, redis: redis.Redis):
    role: discord.Role = inter.guild.get_role(STREAMER_ROLE_ID)
    user: discord.Member = inter.guild.get_member(int(user_id))
    await redis.hset(name="Streamer Status", key=user_id, value="Kabul Edildi")
    await user.add_roles(role)
    await inter.response.send_message(
        "Başvuru başarıyla kabul edildi. Roller eklendi.", ephemeral=True
    )


async def reject_editor(redis: redis.Redis, inter: discord.Interaction, user_id: int):
    await redis.hset(name="Streamer Status", key=user_id, value="Reddedildi")
    await inter.response.send_message("Başvuru başarıyla reddedildi.", ephemeral=True)


class ConfirmButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.r = redis.from_url("redis://localhost")

    @discord.ui.button(
        label="Kabul Et",
        style=discord.ButtonStyle.green,
        emoji="✔️",
        custom_id="streamer:accept",
    )
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            user_id = await check_user_id(redis=self.r, inter=interaction)
        except:
            return
        try:
            await check_user_status(redis=self.r, inter=interaction, user_id=user_id)
        except:
            return

        await add_editor_role(inter=interaction, user_id=user_id, redis=self.r)

    @discord.ui.button(
        label="Reddet",
        style=discord.ButtonStyle.red,
        emoji="✖️",
        custom_id="streamer:reject",
    )
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            user_id = await check_user_id(redis=self.r, inter=interaction)
        except:
            return
        try:
            await check_user_status(redis=self.r, inter=interaction, user_id=user_id)
        except:
            return
        await reject_editor(redis=self.r, inter=interaction, user_id=user_id)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # return 1078376343294713866 in [role.id for role in interaction.user.roles]
        return ADMIN_ROLE_ID  in [role.id for role in interaction.user.roles] or OWNER_ROLE_ID in [role.id for role in interaction.user.roles]


class EditorModal(discord.ui.Modal, title="Yayın Bilgileriniz"):
    def __init__(self):
        super().__init__(timeout=None)
        self.r = redis.from_url("redis://localhost")

    channel_name = discord.ui.TextInput(
        label="Kanal Linki", style=discord.TextStyle.long
    )
    avarage_viewers = discord.ui.TextInput(
        label="Ortalama İzleyici Sayısı", style=discord.TextStyle.short, required=True
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        msg: discord.Message = await interaction.channel.send(
            f"{interaction.user.mention} başvuru yaptı!\n{self.channel_name.label}: {self.channel_name}\n{self.avarage_viewers.label}: {self.avarage_viewers}",
            view=ConfirmButtons(),
        )

        await self.r.hset(
            name="Streamer Interactions", key=msg.id, value=interaction.user.id
        )
        await self.r.hset(
            name="Streamer Status", key=interaction.user.id, value="Beklemede"
        )
        await interaction.response.send_message(
            "Başvurunuz başarıyla yapıldı", ephemeral=True
        )


class EditorButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.r = redis.from_url("redis://localhost")

    @discord.ui.button(
        label="Başvuru Yap!",
        style=discord.ButtonStyle.blurple,
        emoji="📋",
        custom_id="StreamerButton",
    )
    async def callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if await self.r.hexists(name="Streamer Status", key=interaction.user.id):
            user_status = (
                (
                    await self.r.hget(name="Streamer Status", key=interaction.user.id)
                ).decode("utf-8")
                if (await self.r.hget(name="Streamer Status", key=interaction.user.id))
                is not None
                else None
            )
            if user_status == None:
                return await interaction.response.send_message(
                    "Beklenmeyen bir hata oluştu.", ephemeral=True
                )

            return await interaction.response.send_message(
                f"Aynı kullanıcı daha sonra izin verilmediği sürece birden fazla kez başvuru yapamaz\nŞu anki başvuru durumunuz: **{user_status}**",
                ephemeral=True,
            )

        return await interaction.response.send_modal(EditorModal())
