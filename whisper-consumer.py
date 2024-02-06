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
    if update.message and update.message.text:
        username = update.message.from_user.username if update.message.from_user else 'Anonymous'
        first_name = update.message.from_user.first_name
        last_name = update.message.from_user.last_name
        user_id= update.message.from_user.id
        timestamp = datetime.now().timestamp()

        message_data = {
        "timestamp": timestamp,
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "user_id": user_id,
        "message": update.message.text
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
