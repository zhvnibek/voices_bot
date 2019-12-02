import os
import logging
import telegram
from telegram.ext import Updater

logging.basicConfig(format='%(levelname)s [%(asctime)s] [%(name)s] %(message)s', datefmt='%d/%m/%Y %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger('voices')

token = os.environ.get('TOKEN', '')
updater = Updater(token=token, use_context=True)
bot = telegram.Bot(token=token)
