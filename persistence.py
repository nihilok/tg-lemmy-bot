import json
import logging
from pathlib import Path

from constants import ALLOWED_USERS, ALLOWED_CHATS

PATH = Path("./data")
USERS_PATH = PATH / "users"
GROUPS_PATH = PATH / "groups"

logger = logging.getLogger("persistence")


def create_user_persistence():
    with open(USERS_PATH, "w") as f:
        json.dump({"users": ALLOWED_USERS}, f)


def create_group_persistence():
    with open(GROUPS_PATH, "w") as f:
        json.dump({"groups": ALLOWED_CHATS}, f)


def save_users(users: list[int]):
    with open(USERS_PATH, "w") as f:
        json.dump({"users": users}, f)


def save_groups(groups: list[int]):
    with open(GROUPS_PATH, "w") as f:
        json.dump({"groups": groups}, f)


def get_users() -> list[int]:
    with open(USERS_PATH, "r") as f:
        return json.load(f)["users"]


def get_groups() -> list[int]:
    with open(GROUPS_PATH, "r") as f:
        return json.load(f)["groups"]


def persist_group(group_id: int):
    groups = set(get_groups())
    groups.add(group_id)
    save_groups(list(groups))


def persist_user(user_id: int):
    users = set(get_users())
    users.add(user_id)
    save_users(list(users))


def remove_group_persistence(group_id: int):
    groups = set(get_groups())
    groups.remove(group_id)
    save_groups(list(groups))


def remove_user_persistence(user_id: int):
    users = set(get_users())
    users.remove(user_id)
    save_users(list(users))


def init_persistence():
    if not USERS_PATH.exists():
        create_user_persistence()
    if not GROUPS_PATH.exists():
        create_group_persistence()

    try:
        save_users(get_users())
    except Exception as e:
        logger.exception(e, stack_info=True, stacklevel=1)
        logger.warning("Recreating users file")
        create_user_persistence()
    try:
        save_groups(get_groups())
    except Exception as e:
        logger.exception(e, stack_info=True, stacklevel=1)
        logger.warning("Recreating groups file")
        create_group_persistence()
