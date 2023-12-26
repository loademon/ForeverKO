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
            url="https://cdn.discordapp.com/attachments/1185610497907773440/1189294949754216531/LOGO-1.png?ex=659da43c&is=658b2f3c&hm=172a920697c7032575cd60ba7ff3ab45cb32e0b5fcef2884c49335c15a1eb5a1&"
        )

        await ctx.channel.send(
            content=content,
            embed=embed,
            view=EditorButton(),
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Streamer(bot=bot))
