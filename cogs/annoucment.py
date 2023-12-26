import discord
import redis.asyncio as redis
from typing import Optional
from discord.ext import commands


class Announcment(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Ready")

    async def cog_load(self) -> None:
        print(f"{self.__class__.__name__} loaded")

    @commands.hybrid_command(name="duyuru")
    @commands.has_any_role(1185604201242431608, 1185605115302924440)
    async def duyuru(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel,
        *,
        duyuru_başlığı: str,
        duyuru_metni: str,
        everyone: bool = False,
        duyuru_görseli: Optional[str] = None,
    ):
        embed = discord.Embed(
            color=0xFF0000,
            title=duyuru_başlığı,
            description=duyuru_metni,
        )
        if duyuru_görseli:
            embed.set_image(url=duyuru_görseli)

        if everyone:
            await channel.send(content="@everyone", embed=embed)

        else:
            await channel.send(embed=embed)

        return await ctx.send(f"Duyuru başarıyla gönderildi. {channel.mention}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Announcment(bot=bot))
