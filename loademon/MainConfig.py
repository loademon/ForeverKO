from loademon.dataclass import (
    MainConfig,
    ActivityConfig,
    ActivityType,
    ReadyConfig,
    ErrorConfig,
    CommandErrorConfig,
    CogLoadConfig,
    CogConfig,
)

CONFIG = MainConfig(
    api_key="MTE4NTg5ODU5NDcwNDgzNDU4MA.GzZG0C.N9tl3hNA-6a5oLr9jL26_j5jJD8NFhhfwxWFrc",
    command_prefix="!",
    activity=ActivityConfig(type=ActivityType.playing, message="ForeverKO"),
    ready=ReadyConfig(message="ForeverKO bot hazır!"),
    error=ErrorConfig(
        CommandNotFound=CommandErrorConfig(
            message="komudu geçerli bir komut değil.", delete_after=5
        ),
        NotOwner=CommandErrorConfig(
            message="Bu komutu kullanmak için yetkin yok.", delete_after=5
        ),
    ),
    cogs=CogLoadConfig(
        Cogs=[
            CogConfig(name="welcome", is_active=True),
            CogConfig(name="streamer", is_active=True),
            CogConfig(name="giveaway", is_active=True),
            CogConfig(name="sync", is_active=True),
            CogConfig(name="level", is_active=True),
            CogConfig(name="invite", is_active=True),
            CogConfig(name="annoucment", is_active=True),
        ]
    ),
)
