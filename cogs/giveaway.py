import discord
from discord.ext import commands, tasks
from typing import Literal
import pickle
import random
from datetime import datetime, timedelta

import redis.asyncio as redis

GIVEAWAY_CHANNEL_ID = 1185613316698148884
FAST_GIVEAWAY_CHANNEL_ID = 1185640859132239932

MUDAVIM_CHANNEL_ID = 1186352400559243264
YUKSEK_MUDAVIM_CHANNEL_ID = 1186352446591737956

OWNER_ROLE_ID = 1185604201242431608
ADMIN_ROLE_ID = 1185605115302924440

giveaways = []


class JoinButton(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.r = redis.from_url("redis://localhost")
        self.bot = bot

    @discord.ui.button(
        label="Çekilişe Katıl",
        style=discord.ButtonStyle.green,
        emoji="🎉",
        custom_id="giveaway:join",
    )
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        status = await self.r.hget(f"giveaway:{interaction.message.id}", "status")
        status = pickle.loads(status)

        members = await self.r.hget(f"giveaway:{interaction.message.id}", "members")
        members: list = pickle.loads(members)

        channel_id = await self.r.hget(
            f"giveaway:{interaction.message.id}", "channel_id"
        )
        channel_id = pickle.loads(channel_id)

        message_id = await self.r.hget(
            f"giveaway:{interaction.message.id}", "message_id"
        )
        message_id = pickle.loads(message_id)

        channel = self.bot.get_channel(channel_id)
        message = await channel.fetch_message(message_id)

        if status:
            return await interaction.response.send_message(
                content="Çekiliş süresi sona erdiğinden bu çekilişe katılamazsınız.",
                ephemeral=True,
            )

        if interaction.user.id in members:
            return await interaction.response.send_message(
                content="Zaten bu çekilişe katılmışsınız.", ephemeral=True
            )

        members.append(interaction.user.id)

        length = len(members)

        message.embeds[0].set_field_at(
            index=3,
            name="Katılanlar",
            value=f"{length} kişi katıldı.",
        )

        await message.edit(
            content="everyone çekiliş başladı.",
            embed=message.embeds[0],
            view=JoinButton(bot=self.bot),
        )

        await self.r.hset(
            f"giveaway:{interaction.message.id}", "members", pickle.dumps(members)
        )

        return await interaction.response.send_message(
            content="Çekilişe başarıyla katıldınız.", ephemeral=True
        )

    @discord.ui.button(
        label="Çekilişi Kapat",
        style=discord.ButtonStyle.red,
        emoji="🔒",
        custom_id="giveaway:close",
    )
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        global giveaways
        if any(
            role.id == OWNER_ROLE_ID or role.id == ADMIN_ROLE_ID
            for role in interaction.user.roles
        ):
            channel_id = await self.r.hget(
                f"giveaway:{interaction.message.id}", "channel_id"
            )
            channel_id = pickle.loads(channel_id)
            message_id = await self.r.hget(
                f"giveaway:{interaction.message.id}", "message_id"
            )
            message_id = pickle.loads(message_id)
            channel = self.bot.get_channel(channel_id)
            message = await channel.fetch_message(message_id)

            giveaways.remove(f"giveaway:{interaction.message.id}")
            await self.r.delete(f"giveaway:{interaction.message.id}")
            await interaction.response.send_message(
                content="Çekiliş başarıyla kapatıldı.",
                ephemeral=True,
            )
            return await message.edit(
                content="Çekiliş yönetici kararıyla iptal edilmiştir.",
                embed=message.embeds[0],
                view=None,
            )

        return await interaction.response.send_message(
            content="Bu çekilişi sadece yöneticiler kapatabilir.",
            ephemeral=True,
        )


class Giveaway(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self.r = redis.from_url("redis://localhost")
        self.giveaway_loop.start()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__class__.__name__} Ready")

    async def cog_load(self) -> None:
        global giveaways
        self.bot.add_view(JoinButton(bot=self.bot))
        giveaways = await self.r.keys("giveaway:*")
        giveaways = [giveaway.decode() for giveaway in giveaways]
        print(f"{__class__.__name__} loaded")

    @tasks.loop(count=None)
    async def giveaway_loop(self):
        global giveaways
        now = datetime.now()

        for giveaway in giveaways:
            expire_time = await self.r.hget(giveaway, "expire_time")
            expire_time = pickle.loads(expire_time)

            if now > expire_time:
                channel_id = await self.r.hget(giveaway, "channel_id")
                channel_id = pickle.loads(channel_id)

                message_id = await self.r.hget(giveaway, "message_id")
                message_id = pickle.loads(message_id)

                channel = self.bot.get_channel(channel_id)
                message = await channel.fetch_message(message_id)

                await self.r.hset(giveaway, "status", pickle.dumps(True))

                members = await self.r.hget(giveaway, "members")
                members: list = pickle.loads(members)

                winner_count: bytes = await self.r.hget(giveaway, "winner_count")
                winner_count = int(winner_count.decode())

                winners: list[discord.Member] = []

                if len(members) == 0:
                    await self.r.delete(giveaway)
                    giveaways.remove(giveaway)
                    return await message.edit(
                        content="Yeterli katılım olmadığı için çekiliş iptal edilmiştir.",
                        embed=message.embeds[0],
                        view=None,
                    )

                if len(members) < winner_count:
                    await self.r.delete(giveaway)
                    giveaways.remove(giveaway)
                    return await message.edit(
                        content="Yeterli katılım olmadığı için çekiliş iptal edilmiştir.",
                        embed=message.embeds[0],
                        view=None,
                    )

                for _ in range(winner_count):
                    winner_id = random.choice(members)
                    winner = self.bot.get_user(winner_id)
                    winners.append(winner)
                    members.remove(winner.id)

                message.embeds[0].add_field(
                    inline=True,
                    name="Kazananlar",
                    value=", ".join([winner.mention for winner in winners]),
                )

                await message.edit(
                    content="Bu çekiliş sona erdi.",
                    embed=message.embeds[0],
                    view=None,
                )

                await message.reply(
                    content=f"çekiliş sona erdi. Kazananlar: {', '.join([winner.mention for winner in winners])}",
                )

                await self.r.delete(giveaway)
                giveaways.remove(giveaway)

    @giveaway_loop.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

    @commands.hybrid_command(name="çekiliş-başlat")
    @commands.has_any_role(1185604201242431608, 1185605115302924440)
    async def giveaway(
        self,
        ctx: commands.Context,
        çekiliş_tipi: Literal["Hızlı", "Normal", "Müdavim", "Yüksek Müdavim"],
        çekiliş_ne_kadar_sürecek_dakika: int,
        kaç_kişi_kazanacak: int,
        ödüller: str,
    ):
        global giveaways

        time = çekiliş_ne_kadar_sürecek_dakika
        now = datetime.now()
        expire_time = now + timedelta(minutes=time)
        timestamp = expire_time.timestamp()
        timestamp = int(timestamp)
        timestamp = f"<t:{timestamp}:R>"

        members = []

        embed = discord.Embed(
            color=0xFF0000,
            title="Çekiliş",
            description="Çekilişe katılmak için aşağıdaki butona tıklayınız.",
        )

        embed.add_field(
            inline=True,
            name="Çekiliş Bitimi",
            value=timestamp,
        )
        embed.add_field(
            inline=True,
            name="Kazanacak Kişi Sayısı",
            value=kaç_kişi_kazanacak,
        )

        embed.add_field(
            inline=True,
            name="Ödüller",
            value=ödüller,
        )

        embed.add_field(inline=True, name="Katılanlar", value="Henüz kimse katılmadı.")

        if çekiliş_tipi == "Normal":
            channel = self.bot.get_channel(GIVEAWAY_CHANNEL_ID)
            message = await channel.send(
                content="everyone çekiliş başladı.",
                embed=embed,
                view=JoinButton(self.bot),
            )

        if çekiliş_tipi == "Hızlı":
            channel = self.bot.get_channel(FAST_GIVEAWAY_CHANNEL_ID)
            message = await channel.send(
                content="everyone çekiliş başladı.",
                embed=embed,
                view=JoinButton(self.bot),
            )

        if çekiliş_tipi == "Müdavim":
            channel = self.bot.get_channel(MUDAVIM_CHANNEL_ID)
            message = await channel.send(
                content="everyone çekiliş başladı.",
                embed=embed,
                view=JoinButton(self.bot),
            )

        if çekiliş_tipi == "Yüksek Müdavim":
            channel = self.bot.get_channel(YUKSEK_MUDAVIM_CHANNEL_ID)
            message = await channel.send(
                content="everyone çekiliş başladı.",
                embed=embed,
                view=JoinButton(self.bot),
            )

        mapping = {
            "message_id": pickle.dumps(message.id),
            "channel_id": pickle.dumps(channel.id),
            "members": pickle.dumps(members),
            "status": pickle.dumps(False),
            "expire_time": pickle.dumps(expire_time),
            "winner_count": kaç_kişi_kazanacak,
        }

        giveaways.append(f"giveaway:{message.id}")

        await self.r.hset(f"giveaway:{message.id}", mapping=mapping)
        await ctx.send("Çekiliş başarıyla başlatıldı.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Giveaway(bot=bot))
