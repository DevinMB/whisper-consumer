import os
import json
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
from kafka import KafkaConsumer, KafkaProducer

load_dotenv()

bootstrap_servers=[os.getenv('BROKER')]
topic_name=os.getenv('TOPIC_NAME')
bot_token=os.getenv('BOT_TOKEN')

producer = KafkaProducer(
    bootstrap_servers=bootstrap_servers,
    value_serializer=lambda m: json.dumps(m).encode('utf-8'),
    key_serializer=str.encode)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    timestamp = datetime.now().timestamp()
    
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
        # Handling messages from private chats, groups, or supergroups
        chat_type = update.message.chat.type.name  # Dynamically get the chat type as a string
        chat_id = update.message.chat.id
        username = update.message.from_user.username if update.message.from_user else 'Anonymous'
        first_name = update.message.from_user.first_name if update.message.from_user.first_name else 'Anonymous'
        last_name = update.message.from_user.last_name if update.message.from_user.last_name else 'Anonymous'
        user_id = update.message.from_user.id if update.message.from_user.id else 'Anonymous'
        text = update.message.text
        if update.message.chat.type.name == "PRIVATE":
            title = update.message.from_user.username
        else:
            title = update.message.chat.title if update.message.chat.title else "Group"
        
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

    print(message_data)
    
        # producer.send(topic_name, key=username, value=message_data)



# def handle_message(update, context):
#     username = update.message.from_user.username
#     message_text = update.message.text
#     timestamp = datetime.now().timestamp()

#     message_data = {
#         "timestamp": timestamp,
#         "user": username,
#         "message": message_text
#     }

#     # producer.send(topic_name, key=username, value=message_data)
#     print(message_data)

if __name__ == '__main__':
    application = ApplicationBuilder().token(bot_token).build()

    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    application.add_handler(message_handler)

    print('Whispererer is listening....')
    application.run_polling()
