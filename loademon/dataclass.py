from discord.ext import commands, tasks
from discord import ActivityType, PartialEmoji
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ActivityConfig:
    type: ActivityType
    message: str


@dataclass
class ReadyConfig:
    message: str


@dataclass
class CommandErrorConfig:
    """For errors that happen in the use of a command."""

    message: str
    delete_after: int


@dataclass
class ErrorConfig:
    CommandNotFound: CommandErrorConfig
    NotOwner: CommandErrorConfig


@dataclass
class CogConfig:
    name: str
    is_active: bool


@dataclass
class CogLoadConfig:
    Cogs: list[CogConfig]


@dataclass
class MainConfig:
    api_key: str
    command_prefix: str
    activity: ActivityConfig
    ready: ReadyConfig
    error: ErrorConfig
    cogs: CogLoadConfig


@dataclass
class WelcomeConfig:
    logo: str
    guild_id: int
    channel_id: int
    join_message: str
    dm_message: str
    footer_message: str
    color: int
