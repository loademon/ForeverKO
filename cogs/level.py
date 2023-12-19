import discord
from discord.ext import commands
import datetime

import redis.asyncio as redis

from loademon.SpamDetector import SpamDetector

ALLOWED_CHANNELS = [
    1185996673223233648,
    1185243123056648233,
]  # Genel sohbet kanal id'leri


LEVEL_ROLES = {
    "1": 1186352953402077254,  # çaylak role_id
    "2": 1186351153223573574,  # müdavim role_id
    "3": 1186351942436389024,  # yüksek müdavim role_id
}

LEVEL_UP_LOG_CHANNEL = 1185895889819144263  # Level atlayanların loglanacağı kanal id'si


class Level(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.r = redis.Redis(host="localhost", port=6379, db=0)
        self.detector = SpamDetector(max_messages=5, time_window=60, max_similarity=0.8)
        self.LEVELS_REQUIRED_POINTS = {
            "1": "1",
            "2": "4",
            "3": "30",
        }

        self.spam_conts = {}

    async def user_is_admin(self, user: discord.User) -> bool:
        user_roles = [role.id for role in user.roles]
        if 1185604201242431608 in user_roles or 1185605115302924440 in user_roles:
            return True
        return False

    async def get_user_level(self, user_id: int) -> int:
        return await self.r.zscore("User Level", user_id)

    async def get_user_points(self, user_id: int) -> int:
        return await self.r.zscore("User Points", user_id)

    async def calculate_level_from_points(self, points: int) -> int:
        if points < 1:
            return 0
        elif points < 4:
            return 1
        elif points < 30:
            return 2
        else:
            return 3

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Ready")

    async def cog_load(self) -> None:
        print(f"{self.__class__.__name__} loaded")

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.author.id == self.bot.user.id:
            return

        if msg.channel.id in ALLOWED_CHANNELS:
            if await self.r.zscore("User Points", msg.author.id) is None:
                await self.r.zadd("User Points", {msg.author.id: 0})
                await self.r.zadd("User Level", {msg.author.id: 0})

            level = await self.calculate_level_from_points(
                await self.get_user_points(msg.author.id)
            )
            user_level = await self.get_user_level(msg.author.id)

            similar, tip = self.detector.is_spam(
                user_id=msg.author.id, message=msg.content
            )

            if similar:
                if tip and not await self.user_is_admin(msg.author):
                    await msg.delete()
                    if msg.author.id in self.spam_conts:
                        self.spam_conts[msg.author.id] += 1
                    else:
                        self.spam_conts[msg.author.id] = 1

                    if self.spam_conts[msg.author.id] == 3:
                        await msg.channel.send(
                            f"{msg.author.mention} spam yapmayı kes yoksa susturulacaksın!",
                            delete_after=5,
                        )

                    elif self.spam_conts[msg.author.id] >= 5:
                        await msg.author.timeout(datetime.timedelta(minutes=1))
                        await msg.channel.send(
                            f"{msg.author.mention} 1 dakika boyunca susturuldu!",
                            delete_after=5,
                        )
                        self.spam_conts[msg.author.id] = 0
                    return

                return

            await self.r.zincrby("User Points", 0.05, msg.author.id)

            if level > user_level:
                await self.r.zadd("User Level", {msg.author.id: level})
                await msg.author.add_roles(msg.guild.get_role(LEVEL_ROLES[str(level)]))
                channel = self.bot.get_channel(LEVEL_UP_LOG_CHANNEL)
                await channel.send(
                    f"{msg.author.mention} seviye atladı. Yeni seviyesi: {level}"
                )


async def setup(bot: commands.Bot):
    await bot.add_cog(Level(bot=bot))
