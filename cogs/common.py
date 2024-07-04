"""Common tools to share between cogs."""

# Standard imports
import asyncio
import itertools
import logging
from typing import Optional

# External imports
from discord import Embed, Member, Message, NotFound, Reaction
from discord.ext import commands

# Local imports
import utils.configuration as cfg

log = logging.getLogger('lydian')

class EmojiStr:
    """Shortcuts for certain emoji used by the bot."""
    # General
    num: list[str] = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    cancel: str = '❌'
    confirm: str = '✅'
    info: str = 'ℹ️'
    arrow_u: str = '⬆️'
    arrow_r: str = '➡️'
    arrow_d: str = '⬇️'
    arrow_l: str = '⬅️'
    dice: str = '🎲'
    # Media
    play: str = '▶️'
    pause: str = '⏸️'
    skip: str = '⏭️'
    repeat: str = '🔁'
    repeat_one: str = '🔂'
    shuffle: str = '🔀'
    inbox: str = '📥'
    outbox: str = '📤'

class SilentCancel(commands.CommandError):
    """Raised to cancel commands where "return" wouldn't work, like the `Voice` cog's `ensure_voice()`"""

async def is_command_enabled(ctx: commands.Context) -> bool:
    """Checks whether this command's name is found in the configuration's list of disabled commands."""
    if not ctx.command.name in cfg.DISABLED_COMMANDS:
        return True
    else:
        await ctx.send(embed=embedq(EmojiStr.cancel + ' This command is disabled.',
            'Commands can be disabled or "blacklisted" via `config.yml`. If this is unintended, check your configuration.'))
        return False

def command_aliases(command: str) -> list[str]:
    """Returns a list of aliases for the given command."""
    return cfg.COMMAND_ALIASES.get(command) or []

def command_from_alias(alias: str) -> str:
    """Finds a matching command for the given alias. Returns upon first match."""
    for key, val in itertools.chain(cfg.get('aliases').items(), cfg.get_default('aliases').items()):
        if alias in val:
            return key
    return ''

async def edit_or_send(ctx: commands.Context, target: Optional[Message], **kwargs) -> Message:
    """Checks if the given Message object exists (is `None` or not), edits it if so, creates and sends a new message if not.
    Returns the edited or sent message. **kwargs will be passed to the message constructor.

    @target: `Message` to target for editing"""
    try:
        message: Message = await target.edit(**kwargs) if target else await ctx.send(**kwargs)
    except NotFound:
        message: Message = await ctx.send(**kwargs)
    return message

def embedq(title: str='', subtext: str='', color: int=cfg.EMBED_COLOR, base: Optional[Embed]=None) -> Embed:
    """Shortcut for making embeds for messages."""
    if base:
        return Embed(title=title or base.title, description=subtext or base.description or None, color=color or base.color)
    return Embed(title=title, description=subtext or None, color=color)

async def prompt_for_choice(bot: commands.Bot, ctx: commands.Context,
    prompt_msg: Message,
    result_msg: Optional[Message]=None,
    yesno: bool=False,
    choice_nums: int=0,
    timeout_seconds: int=30,
    delete_prompt: bool=True) -> int:
    """Adds reactions to a given Message (`prompt_msg`) and returns the outcome.

    Returns the chosen number if a valid selection was made, 0 if the prompt was cancelled.

    @prompt_msg: A `Message` containing the choices that reaction will be added to.
    @result_msg: (`None`) A `Message` that can be edited based on the prompt's outcome.
    @yesno: (`False`) Makes this choice prompt a simple yes/no confirmation with a green checkbox and a cancel button.
        `choice_nums` does not need to be set if this is `True`.
    @choice_nums: (`0`) How many choices to give. Will always start at 1 and end at `choice_nums`.\
        An error will be raised if `yesno` is `False` but `choice_nums` is still the default `0`.\
        Maximum of 10, as that is the highest number an individual emoji can represent.
    @timeout_seconds: (`30`) How long to wait before automatically cancelling the prompt, in seconds.
    @delete_prompt: (`True`) Whether to delete `prompt_msg` after either a timeout has occurred,\
        the selection was cancelled, or a valid selection was made.
    """
    # Get reaction menu ready
    log.info('Prompting for reactions...')

    if (not yesno) and (choice_nums == 0):
        raise ValueError('choice_nums must be greater than 0 if this is not a yes/no dialog.')

    if not yesno:
        if choice_nums > len(EmojiStr.num):
            raise ValueError('choice_nums can not be greater than 10.')

        for i in range(choice_nums):
            await prompt_msg.add_reaction(EmojiStr.num[i + 1])
    else:
        await prompt_msg.add_reaction(EmojiStr.confirm)
    await prompt_msg.add_reaction(EmojiStr.cancel)

    def check(reaction: Reaction, user: Member) -> bool:
        return (user == ctx.message.author) and (str(reaction.emoji) in EmojiStr.num + [EmojiStr.confirm, EmojiStr.cancel])

    log.debug('Waiting for reaction...')

    async def handle_messages(result_msg_embed: Embed) -> None:
        if result_msg:
            await result_msg.edit(embed=result_msg_embed)
            await asyncio.sleep(3)
            await result_msg.delete()
        if delete_prompt:
            await prompt_msg.delete()

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=timeout_seconds, check=check) # pylint: disable=unused-variable
    except asyncio.TimeoutError:
        log.debug('Choice prompt timeout reached.')
        await handle_messages(embedq(EmojiStr.cancel + ' Prompt timed out.'))
        return 0

    log.debug('Received a valid reaction.')

    if str(reaction) == EmojiStr.cancel:
        log.debug('Selection cancelled.')
        await handle_messages(embedq(EmojiStr.cancel + ' Selection cancelled.'))
        return 0

    if str(reaction) == EmojiStr.confirm:
        log.debug('Selection confirmed.')
        await handle_messages(embedq(EmojiStr.confirm + ' Selection confirmed.'))
        return 1

    choice = EmojiStr.num.index(str(reaction))
    log.debug('%s selected.', choice)
    await handle_messages(embedq(EmojiStr.confirm + f' Option #{choice} selected.'))
    return choice
