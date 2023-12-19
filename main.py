from typing import Any
from discord import Activity, Intents, Interaction
from loademon.MainConfig import CONFIG as config
from discord.ext import commands


class ForeverKo(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=config.command_prefix,
            intents=Intents.all(),
            activity=Activity(type=config.activity.type, name=config.activity.message),
            help_command=None,
        )

    async def on_ready(self):
        print(config.ready.message)

    async def on_command_error(
        self, context: commands.Context, e: Exception, /
    ) -> None:
        if e.__class__ == commands.CommandNotFound:
            error = config.error.CommandNotFound
            await context.send(
                f"**{context.message.content.split()[0]}** {error.message}",
                delete_after=error.delete_after,
            )

        if e.__class__ == commands.NotOwner:
            error = config.error.NotOwner
            await context.send(error.message, delete_after=error.delete_after)

    async def setup_hook(self) -> None:
        for cog in config.cogs.Cogs:
            if cog.is_active:
                try:
                    await self.load_extension(f"cogs.{cog.name}")
                except Exception as e:
                    print(str(e))


ForeverKo().run(config.api_key)
