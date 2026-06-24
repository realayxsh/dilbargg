"""
Compatibility shim: adds discord.py Components V2 stub classes to discord.ui
and patches send/edit methods so components=[Container(...)] works by
converting to standard discord.Embed calls.

Import and call install() BEFORE any other discord import that uses V2 classes.
"""
from __future__ import annotations
import discord


class TextDisplay:
    def __init__(self, content=""):
        self.content = str(content)


class MediaGalleryItem:
    def __init__(self, media=""):
        self.media = str(media)


class MediaGallery:
    def __init__(self, *items):
        self.items = list(items)

    def add_item(self, media=""):
        self.items.append(MediaGalleryItem(media=media))


class Separator:
    pass


class Thumbnail:
    def __init__(self, url="", media=None):
        self.url = url or media or ""


class Section:
    def __init__(self, *children, accessory=None):
        self.children = list(children)
        self.accessory = accessory


class Container:
    def __init__(self, *children):
        self.children = list(children)

    def add_item(self, item):
        self.children.append(item)


class LayoutView:
    def __init__(self):
        self.children = []

    def add_item(self, item):
        self.children.append(item)


def _children_to_embed(children) -> discord.Embed:
    lines = []
    images = []

    def walk(items):
        for child in items:
            if isinstance(child, TextDisplay):
                lines.append(child.content)
            elif isinstance(child, Section):
                walk(child.children)
                if isinstance(child.accessory, Thumbnail) and child.accessory.url:
                    images.append(child.accessory.url)
            elif isinstance(child, MediaGallery):
                for item in child.items:
                    if isinstance(item, MediaGalleryItem) and item.media:
                        images.append(item.media)
            elif isinstance(child, Separator):
                lines.append("")
            elif isinstance(child, (Container, LayoutView)):
                walk(child.children)

    walk(children)

    description = "\n".join(lines).strip() or None
    embed = discord.Embed(description=description)
    if images:
        embed.set_image(url=images[0])
    return embed


def _convert_components(kwargs: dict) -> dict:
    components = kwargs.pop("components", None)
    if not components:
        return kwargs

    embeds = []
    for comp in components:
        if isinstance(comp, (Container, LayoutView)):
            embeds.append(_children_to_embed(comp.children))
        elif isinstance(comp, TextDisplay):
            embeds.append(discord.Embed(description=comp.content))

    if len(embeds) == 1:
        kwargs["embed"] = embeds[0]
    elif embeds:
        kwargs["embeds"] = embeds
    return kwargs


_installed = False


def install():
    global _installed
    if _installed:
        return
    _installed = True

    discord.ui.Container = Container
    discord.ui.TextDisplay = TextDisplay
    discord.ui.MediaGallery = MediaGallery
    discord.ui.MediaGalleryItem = MediaGalleryItem
    discord.ui.Section = Section
    discord.ui.Separator = Separator
    discord.ui.Thumbnail = Thumbnail
    discord.ui.LayoutView = LayoutView

    _orig_send = discord.abc.Messageable.send

    async def _patched_send(self, content=None, **kwargs):
        kwargs = _convert_components(kwargs)
        return await _orig_send(self, content, **kwargs)

    discord.abc.Messageable.send = _patched_send

    _orig_reply = discord.Message.reply

    async def _patched_reply(self, content=None, **kwargs):
        kwargs = _convert_components(kwargs)
        return await _orig_reply(self, content, **kwargs)

    discord.Message.reply = _patched_reply

    _orig_edit = discord.Message.edit

    async def _patched_edit(self, **kwargs):
        kwargs = _convert_components(kwargs)
        return await _orig_edit(self, **kwargs)

    discord.Message.edit = _patched_edit

    _orig_send_msg = discord.InteractionResponse.send_message

    async def _patched_send_msg(self, content=None, **kwargs):
        kwargs = _convert_components(kwargs)
        return await _orig_send_msg(self, content, **kwargs)

    discord.InteractionResponse.send_message = _patched_send_msg

    _orig_webhook = discord.Webhook.send

    async def _patched_webhook(self, content=discord.utils.MISSING, **kwargs):
        kwargs = _convert_components(kwargs)
        return await _orig_webhook(self, content, **kwargs)

    discord.Webhook.send = _patched_webhook
