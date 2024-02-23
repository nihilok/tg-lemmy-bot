from functools import wraps
from typing import Type, Callable, Awaitable, Any

from pydantic import BaseModel, ConfigDict
from telegram import Update
from telegram.ext import ApplicationBuilder, BaseHandler

from constants import SUPERUSER
from persistence import (
    get_users,
    get_groups,
    remove_user_persistence,
    persist_group,
    remove_group_persistence,
    persist_user,
)


async def do_nothing():
    pass


class NotPermitted(Exception):
    pass


def check_users(user_id):
    if user_id == SUPERUSER:
        return user_id
    users = get_users()
    if str(user_id) in users:
        return user_id
    raise NotPermitted(f"User {user_id} not permitted")


def check_perms(chat_id, user_id):
    if user_id == SUPERUSER:
        return chat_id, user_id
    groups = get_groups()
    if chat_id in groups:
        return chat_id, user_id
    check_users(user_id)


def restrict(fn):
    @wraps(fn)
    async def wrapper(update, context):
        check_perms(update.effective_chat.id, update.effective_user.id)
        return await fn(update, context)

    return wrapper


def restrict_user(fn):
    @wraps(fn)
    async def wrapper(update, context):
        check_users(update.effective_user.id)
        return await fn(update, context)

    return wrapper


class MessageHandlerIn(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    constraint: Any = "start"  # e.g. telegram.ext.filters.BaseFilter
    handler: Callable[[int], Awaitable[None]]
    handler_type: Type[BaseHandler]


@restrict_user
async def add_user(update: Update, context):
    try:
        user_id = update.message.reply_to_message.from_user.id
    except AttributeError:
        await context.bot.send_message(
            update.effective_chat.id,
            "You must reply to a message from the target user to use this command",
        )
        return

    persist_user(update.effective_user.id)
    await context.bot.send_message(
        update.effective_chat.id,
        f"USER ID: {user_id} added",
    )


@restrict_user
async def remove_user(update: Update, context):
    try:
        user_id = update.message.reply_to_message.from_user.id
    except AttributeError:
        await context.bot.send_message(
            update.effective_chat.id,
            "You must reply to a message from the target user to use this command",
        )
        return

    remove_user_persistence(update.effective_user.id)
    await context.bot.send_message(
        update.effective_chat.id, f"USER ID: {user_id} removed"
    )


@restrict_user
async def add_group(update, context):
    persist_group(update.effective_chat.id)
    await context.bot.send_message(
        update.effective_chat.id, f"CHAT ID: {update.effective_chat.id} added"
    )


@restrict_user
async def remove_group(update, context):
    remove_group_persistence(update.effective_chat.id)
    await context.bot.send_message(
        update.effective_chat.id, f"CHAT ID: {update.effective_chat.id} removed"
    )


class TGBasebot:
    message_handlers: list[MessageHandlerIn] = []

    def __init__(self, token):
        self.application = ApplicationBuilder().token(token).build()
        for handler in self.message_handlers:
            self.application.add_handler(
                handler.handler_type(handler.constraint, handler.handler)
            )

    def run(self):
        self.application.run_polling()

    async def send_message(self, chat_id, msg="Testing"):
        await self.application.bot.send_message(chat_id, msg, parse_mode="HTML")
