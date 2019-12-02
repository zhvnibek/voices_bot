# import requests
# import json
import redis
import conf
from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram.utils.request import Request

token = conf.token
bot = conf.bot
updater = conf.updater
logger = conf.logger
# tg_request = Request()


def start(update, context):
    logger.info(update.effective_chat.id)
    context.bot.send_message(chat_id=update.effective_chat.id,
                            text="Hey, this is Voices Bot")

def save_received_voice(file_id: str, chat_id: int):
    logger.info(f"Saving the voice: {file_id} receieved from {chat_id}")
    key = f'{chat_id}:{file_id}'
    rcvd_voices.set(key, 1)

def save_sent_voice(file_id: str, chat_id: int, msg_id: int):
    logger.info(f"Saving the voice: {file_id} sent to {chat_id}:{msg_id}")
    key = f'{chat_id}:{msg_id}:{file_id}'
    sent_voices.set(key, 1)

def get_random_voice_id(chat_id: int) -> str:
    logger.info(f"Getting a voice for {chat_id}")
    key: str = rcvd_voices.randomkey()
    cached_chat_id, cached_file_id = key.split(':')
    if int(cached_chat_id) == chat_id:
        logger.info('the same chat_id!')
    return cached_file_id


def get_voice_owner(chat_id: int, msg_id: int) -> int:
    logger.info(f"Getting the replied voice id by msg_id: {msg_id}")
    matched_keys: list = sent_voices.keys(pattern=f'{chat_id}:{msg_id}:*')
    logger.info(f"Matched keys from sent_voices: {matched_keys}")
    if matched_keys:
        replied_file_id: str = matched_keys[0].split(':')[-1]
        logger.info(f"Getting the owner of the voice: {replied_file_id}")
        matched_keys: list = rcvd_voices.keys(pattern=f'*{replied_file_id}')
        logger.info(f"Matched keys from rcvd_voices: {matched_keys}")
        if matched_keys:
            voice_owner_chat_id: int = int(matched_keys[0].split(':')[0])
            logger.info(f"Voice owner chat_id: {voice_owner_chat_id}")
            return voice_owner_chat_id, replied_file_id

def receive_voice(update, context):
    logger.info("receiving a voice..")
    current_message_id = update.message.message_id
    logger.info(f"current message id: {current_message_id}")
    reply = update.message.reply_to_message
    if reply:
        logger.info(f"The voice is replying to {reply.message_id}")
        voice_owner_chat_id, replied_file_id = get_voice_owner(chat_id=update.effective_chat.id,
                                                msg_id=reply.message_id)
        context.bot.send_voice(chat_id=voice_owner_chat_id,
                                voice=update.message.voice.file_id,
                                caption='Someone has replied to your voice message -> [1]!')
        context.bot.send_voice(chat_id=voice_owner_chat_id,
                                voice=replied_file_id,
                                caption='[1] <- Your voice message.')
    save_received_voice(file_id=update.message.voice.file_id,
                        chat_id=update.effective_chat.id)
    cached_file_id = get_random_voice_id(chat_id=update.effective_chat.id)
    context.bot.send_voice(chat_id=update.effective_chat.id,
                            voice=cached_file_id,
                            caption="Here are some random voices!")
    save_sent_voice(file_id=cached_file_id,
                    chat_id=update.effective_chat.id,
                    msg_id=current_message_id+1)

if __name__ == '__main__':
    rcvd_voices = redis.StrictRedis(host='localhost', port=6379, db=1, decode_responses=True)
    sent_voices = redis.StrictRedis(host='localhost', port=6379, db=2, decode_responses=True)
    updater.start_polling()
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    voice_receiver = MessageHandler(Filters.voice, receive_voice)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(voice_receiver)
