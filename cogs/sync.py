"""Please do not make any changes to this file."""

from discord.ext import commands


class Sync(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Rady Don't Forget Sync")

    async def cog_load(self) -> None:
        print(f"{self.__class__.__name__} Loaded Don't Forget Sync")

    @commands.command(name="sync")
    @commands.is_owner()
    async def sync(self, ctx: commands.Context):
        """Sync all commands (Admin Command)"""
        bot: commands.Bot = self.bot
        await ctx.send("Synced", ephemeral=True)
        await bot.tree.sync()

    @commands.command(name="emergency")
    @commands.has_any_role(1185604201242431608, 1185605115302924440)
    async def emergency(self, ctx: commands.Context):
        """Emergency Stop"""
        exit()


async def setup(bot: commands.Bot):
    await bot.add_cog(Sync(bot=bot))
