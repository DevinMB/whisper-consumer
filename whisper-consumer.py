import os
import json
import threading
import time
from datetime import datetime
from pathlib import Path
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
from kafka import KafkaConsumer, KafkaProducer

load_dotenv()

bootstrap_servers=[os.getenv('BROKER')]
topic_name=os.getenv('TOPIC_NAME')
bot_token=os.getenv('BOT_TOKEN')

# The image HEALTHCHECK reads this file's age: it is touched every 30 s while
# the producer is connected to Kafka.
HEALTH_FILE = Path(os.getenv('HEALTH_FILE', '/tmp/healthy'))

producer = None  # created in main, so tests can import this module without Kafka


def to_record(update: Update, timestamp: float) -> tuple[str, dict]:
    """The Kafka key and value for one Telegram update."""
    
    chat_type = "Unknown"
    chat_id = "Unknown"
    user_id = "Unknown"
    username = "Unknown"
    first_name = "Unknown"
    last_name = "Unknown"
    title = "Unknown"
    text = "No text"

    if update.channel_post:
        chat_type = update.channel_post.chat.type.name 
        title = update.channel_post.chat.title
        text = update.channel_post.text
        chat_id = update.channel_post.chat.id
        username = update.channel_post.author_signature


    elif update.message:
        chat_type = update.message.chat.type.name 
        chat_id = update.message.chat.id
        username = update.message.from_user.username if update.message.from_user else 'Anonymous'
        first_name = update.message.from_user.first_name if update.message.from_user.first_name else 'Anonymous'
        last_name = update.message.from_user.last_name if update.message.from_user.last_name else 'Anonymous'
        user_id = update.message.from_user.id if update.message.from_user.id else 'Anonymous'
        text = update.message.text
        if update.message.chat.type.name == "PRIVATE":
            title = update.message.from_user.username
        else:
            title = update.message.chat.title if update.message.chat.title else "SOMEGROUP"
        
        text = update.message.text
        chat_id = update.message.chat.id
        title = update.message.chat.title if update.message.chat.title else update.message.from_user.username
        
    message_data = {
        "timestamp": timestamp,
        "chat_type": chat_type,
        "chat_id": chat_id,
        "user_id": user_id,
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "title": title,
        "message": text
    }
    return title, message_data


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    title, message_data = to_record(update, datetime.now().timestamp())

    print(message_data)
    
    producer.send(topic_name, key=title, value=message_data)


def report_health() -> None:
    while True:
        if producer.bootstrap_connected():
            HEALTH_FILE.touch()
        time.sleep(30)


if __name__ == '__main__':
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda m: json.dumps(m).encode('utf-8'),
        key_serializer=str.encode)
    threading.Thread(target=report_health, daemon=True).start()

    application = ApplicationBuilder().token(bot_token).build()

    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    application.add_handler(message_handler)

    print('Whispererer is listening....')
    application.run_polling()
