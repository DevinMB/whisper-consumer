"""The Kafka record built from each kind of Telegram update. Downstream
consumers read these fields, so the shape is pinned here."""

import importlib.util
from pathlib import Path

from telegram import Update

spec = importlib.util.spec_from_file_location(
    "whisper_consumer", Path(__file__).resolve().parents[1] / "whisper-consumer.py")
wc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wc)

USER = {"id": 42, "is_bot": False, "first_name": "Ada", "last_name": "L", "username": "ada"}


def update(**kind) -> Update:
    return Update.de_json({"update_id": 1, **kind}, None)


def message(chat: dict, **extra) -> dict:
    return {"message_id": 7, "date": 0, "chat": chat, "text": "hello", **extra}


def test_group_message():
    key, rec = wc.to_record(update(message=message(
        {"id": -100, "type": "supergroup", "title": "Friends"}, **{"from": USER})), 1.5)
    assert key == "Friends"
    assert rec == {
        "timestamp": 1.5, "chat_type": "SUPERGROUP", "chat_id": -100, "user_id": 42,
        "username": "ada", "first_name": "Ada", "last_name": "L", "title": "Friends",
        "message": "hello",
    }


def test_private_message_is_keyed_by_username():
    key, rec = wc.to_record(update(message=message(
        {"id": 42, "type": "private", "first_name": "Ada"}, **{"from": USER})), 2.0)
    assert key == "ada" and rec["chat_type"] == "PRIVATE" and rec["title"] == "ada"


def test_missing_last_name_reads_anonymous():
    user = {k: v for k, v in USER.items() if k != "last_name"}
    _, rec = wc.to_record(update(message=message(
        {"id": -1, "type": "group", "title": "G"}, **{"from": user})), 0)
    assert rec["last_name"] == "Anonymous"


def test_channel_post():
    key, rec = wc.to_record(update(channel_post=message(
        {"id": -200, "type": "channel", "title": "News"}, author_signature="Ed")), 3.0)
    assert key == "News"
    assert rec["chat_type"] == "CHANNEL" and rec["username"] == "Ed"
    assert rec["user_id"] == "Unknown" and rec["message"] == "hello"


def test_importing_needs_no_kafka():
    assert wc.producer is None
