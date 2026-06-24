"""
Utility for sending Discord V2 transparent embeds (no colored border).
Usage:
    from utils.v2embed import send_v2, reply_v2

    await send_v2(ctx, "Hello world!")
    await send_v2(channel, "Hello!", title="Title", fields=[("Name", "Value")])
    await reply_v2(ctx, "Response here", mention_author=False)
"""
import discord
from typing import Optional, List, Tuple


def _build_container(
    description: str = None,
    title: str = None,
    fields: List[Tuple[str, str]] = None,
    footer: str = None,
    image: str = None,
    thumbnail: str = None,
) -> discord.ui.Container:
    parts = []
    if title:
        parts.append(f"## {title}")
    if description:
        parts.append(str(description))
    if fields:
        for fname, fvalue, *_ in fields:
            parts.append(f"**{fname}**\n{fvalue}")
    if footer:
        parts.append(f"-# {footer}")

    text = "\n\n".join(parts) if parts else "\u200b"
    children = [discord.ui.TextDisplay(text)]

    if thumbnail:
        children.append(discord.ui.MediaGallery(
            discord.ui.MediaGalleryItem(media=thumbnail)
        ))
    if image:
        children.append(discord.ui.MediaGallery(
            discord.ui.MediaGalleryItem(media=image)
        ))

    return discord.ui.Container(*children)


async def send_v2(
    target,
    description: str = None,
    *,
    title: str = None,
    fields: List[Tuple[str, str]] = None,
    footer: str = None,
    image: str = None,
    thumbnail: str = None,
    view=None,
    delete_after: float = None,
    **kwargs
):
    """Send a V2 transparent embed to a channel or ctx."""
    container = _build_container(description, title, fields, footer, image, thumbnail)
    send_kwargs = dict(components=[container], **kwargs)
    if view:
        send_kwargs["view"] = view
    if delete_after is not None:
        send_kwargs["delete_after"] = delete_after

    if hasattr(target, "channel") and hasattr(target, "send"):
        return await target.send(**send_kwargs)
    return await target.send(**send_kwargs)


async def reply_v2(
    ctx,
    description: str = None,
    *,
    title: str = None,
    fields: List[Tuple[str, str]] = None,
    footer: str = None,
    image: str = None,
    thumbnail: str = None,
    view=None,
    delete_after: float = None,
    mention_author: bool = False,
    **kwargs
):
    """Reply with a V2 transparent embed."""
    container = _build_container(description, title, fields, footer, image, thumbnail)
    send_kwargs = dict(
        components=[container],
        mention_author=mention_author,
        **kwargs
    )
    if view:
        send_kwargs["view"] = view
    if delete_after is not None:
        send_kwargs["delete_after"] = delete_after

    return await ctx.reply(**send_kwargs)
