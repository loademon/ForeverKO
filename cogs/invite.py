import discord
import redis.asyncio as redis
from discord.ext import commands


class Invite(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.r = redis.Redis(host="localhost", port=6379, db=0)
        self.invites = {}
        self.invite_channel_id = 1185641908400300132
        self.invite_channel: discord.TextChannel = None
        self.invite_log_message = None

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Ready")

    async def cog_load(self) -> None:
        guild_id = 951884318198874192
        guild = await self.bot.fetch_guild(guild_id)
        self.invites[guild.id] = await guild.invites()

        self.invite_channel = await self.bot.fetch_channel(self.invite_channel_id)
        print(f"{self.__class__.__name__} loaded")

    @staticmethod
    def find_invite_by_code(invite_list, code: str) -> discord.Invite:
        for inv in invite_list:
            if inv.code == code:
                return inv

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        invites_before_join = self.invites[member.guild.id]
        invites_after_join = await member.guild.invites()
        if member.flags.did_rejoin:
            return

        for invite in invites_before_join:
            if (
                invite.uses
                < self.find_invite_by_code(invites_after_join, invite.code).uses
            ):
                await self.r.zadd("Ivites", {invite.inviter.id: 1}, incr=True)
                await self.r.hset(f"info:{member.id}", "inviter", invite.inviter.id)

        self.invites[member.guild.id] = invites_after_join

        top_ten = await self.r.zrevrange(
            "Ivites", 0, 9, withscores=True
        )  # return list of tuples

        embed = discord.Embed(
            title="En Çok Davet Edenler",
            description="En çok davet edenlerin listesi",
            color=0xFF0000,
        )
        for index, (user_id, score) in enumerate(top_ten):
            if score == 0:
                continue

            user = await self.bot.fetch_user(user_id.decode("utf-8"))

            embed.add_field(
                inline=False,
                name=f"{index+1}. {user.mention}",
                value=f"{int(score)} davet",
            )

        if not self.invite_log_message:
            await self.invite_channel.purge()
            self.invite_log_message = await self.invite_channel.send(embed=embed)
            return

        await self.invite_log_message.edit(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        member_inviter = await self.r.hget(f"info:{member.id}", "inviter")
        if member_inviter is None:
            return
        await self.r.zadd("Ivites", {member_inviter: -1}, incr=True)

        top_ten = await self.r.zrevrange(
            "Ivites", 0, 9, withscores=True
        )  # return list of tuples

        embed = discord.Embed(
            title="En Çok Davet Edenler",
            description="En çok davet edenlerin listesi",
            color=0xFF0000,
        )
        for index, (user_id, score) in enumerate(top_ten):
            if score == 0:
                continue
            user = await self.bot.fetch_user(user_id.decode("utf-8"))
            embed.add_field(
                inline=False,
                name=f"{index+1}. {user.name}",
                value=f"{int(score)} davet",
            )

        if not self.invite_log_message:
            await self.invite_channel.purge()
            self.invite_log_message = await self.invite_channel.send(embed=embed)
            return

        await self.invite_log_message.edit(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Invite(bot=bot))
