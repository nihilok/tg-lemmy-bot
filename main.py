import asyncio
import os

from telegram.ext import CommandHandler

from lemmy import get_top_posts_and_hot_posts, Post
from persistence import persist_group, init_persistence, get_groups
from telegram_basebot import (
    TGBasebot,
    MessageHandlerIn,
    check_perms,
    NotPermitted,
    add_group,
    add_user,
    remove_group,
    remove_user,
    restrict,
)


async def start_handler(update, context):
    authorised = False
    try:
        check_perms(update.effective_chat.id, update.effective_user.id)
        message = "Beep boop! Coding Assistant at your service!"
        persist_group(update.effective_chat.id)
        authorised = True
    except NotPermitted:
        message = "Beep boop! Unfortunately, you are not permitted to use me 😭"

    await context.bot.send_message(update.effective_chat.id, message)
    if authorised:
        await notify_channel(update.effective_chat.id)


async def send_message(chat_id, message):
    await bot.send_message(chat_id, message)


def escape_md(s: str):
    return (
        s.replace(".", r"\.")
        .replace("-", r"\-")
        .replace("(", r"\(")
        .replace(")", r"\)")
        .replace("!", r"\!")
        .replace("*", r"\*")
    )


def create_markdown_message(post: Post):
    show_body = post.url is None

    return f"""
<b><a href="{post.url}">{post.name}</a></b>
{"<i>" + post.content + "</i>" if show_body else""}
Votes: {post.score}
Community: {post.community}
"""


async def run_task():
    for chat_id in get_groups():
        await notify_channel(chat_id)


async def notify_channel(chat_id, limit=None, hot=False):
    if not limit:
        limit = 3
    if limit > 10:
        limit = 10
    posts = get_top_posts_and_hot_posts(limit=limit)
    if hot:
        if limit > 1:
            await send_message(chat_id, f"{limit} HOTTEST POSTS")
        for post in posts.hot:
            await send_message(chat_id, create_markdown_message(post))
    else:
        if limit > 1:
            await send_message(chat_id, f"{limit} TOP POSTS")
        for post in posts.top:
            await send_message(chat_id, create_markdown_message(post))


def run_task_synchronous():
    asyncio.run(run_task())


async def parse_limit(message):
    message_parts = message.split()
    if len(message_parts) > 2:
        return
    try:
        limit = int(message_parts[1])
        print(limit)
        return limit
    except ValueError:
        pass


@restrict
async def get_top_posts_handler(update, context):
    limit = await parse_limit(update.message.text)
    await notify_channel(update.effective_chat.id, limit)


@restrict
async def get_hot_posts_handler(update, context):
    limit = await parse_limit(update.message.text)
    await notify_channel(update.effective_chat.id, limit, hot=True)


class RedditBot(TGBasebot):
    message_handlers = [
        MessageHandlerIn(
            constraint="start", handler=start_handler, handler_type=CommandHandler
        ),
        MessageHandlerIn(
            constraint="add_group", handler=add_group, handler_type=CommandHandler
        ),
        MessageHandlerIn(
            constraint="add_user", handler=add_user, handler_type=CommandHandler
        ),
        MessageHandlerIn(
            constraint="remove_group", handler=remove_group, handler_type=CommandHandler
        ),
        MessageHandlerIn(
            constraint="remove_user", handler=remove_user, handler_type=CommandHandler
        ),
        MessageHandlerIn(
            constraint="top_posts",
            handler=get_top_posts_handler,
            handler_type=CommandHandler,
        ),
        MessageHandlerIn(
            constraint="top",
            handler=get_top_posts_handler,
            handler_type=CommandHandler,
        ),
        MessageHandlerIn(
            constraint="hot_posts",
            handler=get_hot_posts_handler,
            handler_type=CommandHandler,
        ),
        MessageHandlerIn(
            constraint="hot",
            handler=get_hot_posts_handler,
            handler_type=CommandHandler,
        ),
    ]


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.WARNING)

    init_persistence()
    bot = RedditBot(os.getenv("TG_LEMMY_BOT_TOKEN"))
    bot.run()
