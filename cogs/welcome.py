import discord
from discord.ext import commands

from loademon.WelcomeConfig import CONFIG as config


class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__class__.__name__} Ready")

    async def cog_load(self) -> None:
        print(f"{__class__.__name__} loaded")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.guild.id == config.guild_id:
            channel: discord.TextChannel = self.bot.get_channel(config.channel_id)
            embed = discord.Embed(
                color=config.color,
                title=config.join_message,
                description=f"{config.join_message} {member.mention}",
            )
            embed.set_thumbnail(url=config.logo)
            embed.set_footer(text=config.footer_message, icon_url=config.logo)
            role: discord.Role = member.guild.get_role(1185611468515844146)
            await member.add_roles(role)
            dm = await member.create_dm()
            await dm.send(content=member.mention, embed=embed)
            await dm.send(config.dm_message)
            await channel.send(content=member.mention, embed=embed)
        else:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Welcome(bot=bot))
