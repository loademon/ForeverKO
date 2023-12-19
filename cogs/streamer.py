import discord
from discord.ext import commands

import redis.asyncio as redis

from loademon.StreamerConfig import ConfirmButtons, EditorButton, EditorModal


class Streamer(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Ready")

    async def cog_load(self) -> None:
        self.bot.add_view(EditorButton())
        self.bot.add_view(ConfirmButtons())
        print(f"{self.__class__.__name__} loaded")

    @commands.hybrid_command(name="yayıncı-başvuru-aç")
    @commands.has_any_role(1185604201242431608, 1185605115302924440)
    async def editor(self, ctx: commands.Context):
        content = "everyone"
        embed = discord.Embed(
            color=0xFF0000,
            title="Sponsor Yayıncı Başvurusu Nedir?",
            description="Sponsor yayıncı ForeverKO platformunu TikTok, Kick gibi platformlarda tanıtan. ForeverKO için içerik üretenlere verilen bir unvandır.\n\nSponsor yayıncı olmak için aşağıdaki butona tıklayarak başvuru yapabilirsiniz.\n\nBaşvurunuz onaylanırsa size özel bir rol verilecektir.Bu rol ile yayınlarınızı duyurabilirsiniz.",
        )
        embed.add_field(
            inline=True,
            name="Şartlar",
            value="- Günlük en az 2 saat yayın.\n- Sadece farm yayınlarından oluşmamalıdır.\n- Yayınlarınızda ForeverKO'yu tanıtmalısınız.",
        )
        embed.add_field(
            inline=True, name="Ödüller", value="- Sponsor Paket\n- Haftalık Bakiye"
        )
        embed.set_thumbnail(
            url="https://raw.githubusercontent.com/loademon/ForeverKO-utils/main/Error_poop.png"
        )

        await ctx.channel.send(
            content=content,
            embed=embed,
            view=EditorButton(),
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Streamer(bot=bot))
