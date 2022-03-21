import logging, os, sys, random
from typing import Dict
from datetime import date

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    Filters,
    MessageHandler,
    CallbackContext,
    CallbackQueryHandler,
)
# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

TOKEN = os.getenv("TOKEN")
PATH="carte/"

def get_filenames(path=PATH):
    return [f"{path}/{image}" for image in os.listdir(path) if image.endswith("a.png")]

class Bot:

    next_enigma = [[KeyboardButton("Nuovo enigma!")]]
    def __init__(self):
        self.images = get_filenames()

    def welcome(self, update: Update, context: CallbackContext) -> None:
        button = [[KeyboardButton("Premimi!")]]
        update.message.reply_text(
            "Ciao", reply_markup=ReplyKeyboardMarkup(button)
        )

    def send_image(self, update: Update, context: CallbackContext) -> None:
        image = random.choice(self.images)
        reply_markup = None
        if os.path.exists(image.replace("a.png", "b.png")):
            keyboard = [
                [InlineKeyboardButton("Soluzione", callback_data=image)],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

        with open(image, 'rb') as f:
            update.message.reply_photo(
                f,
                reply_markup=reply_markup
            )
    
    def show_soluz(self, update: Update, context: CallbackContext) -> None:
        query = update.callback_query
        query.answer()

        image = query.data.replace("a.png", "b.png")

        with open(image, 'rb') as f:
            update.callback_query.message.reply_photo(
                f
            )
    
    def start(self) -> None:
        # Create the Updater and pass it your bot's token.
        updater = Updater(TOKEN)
        
        # Get the dispatcher to register handlers
        dispatcher = updater.dispatcher
        dispatcher.add_handler(CommandHandler("start", self.welcome))
        updater.dispatcher.add_handler(CallbackQueryHandler(self.show_soluz))
        dispatcher.add_handler(MessageHandler(Filters.all, self.send_image))
        
        PORT = int(os.getenv("PORT", "8443"))

        # Starting bot
        if len(sys.argv) == 2 and sys.argv[1] == "DEV":
            # Developer mode with local instance
            print("Start polling")
            updater.start_polling()
        else:
            # Deployed version with heroku instance
            print("Start webhook")
            updater.start_webhook(listen="0.0.0.0",
                                port=PORT,
                                url_path=TOKEN)
            updater.bot.set_webhook("https://random-cards-bot.herokuapp.com/" + TOKEN)
        updater.idle()

if __name__ == '__main__':
    bot = Bot()
    bot.start()