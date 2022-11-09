import os, sys, random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    Filters,
    MessageHandler,
    CallbackContext,
    CallbackQueryHandler,
)

TOKEN = os.environ.get("TOKEN")
PATH = "carte/"
PORT = int(os.environ.get("PORT", "8443"))

# Read files from folder
def get_filenames(path=PATH):
    return [f"{path}/{image}" for image in os.listdir(path) if image.endswith("a.png")]

class Bot:
    new_enigma_button = [[KeyboardButton("Nuovo enigma!")]]
    def __init__(self):
        self.images = get_filenames()
        self.new_enigma_markup = ReplyKeyboardMarkup(self.new_enigma_button, resize_keyboard=True)

    def welcome(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text(
            "Ciao", reply_markup=self.new_enigma_markup
        )

    def send_image(self, update: Update, context: CallbackContext) -> None:
        image = random.choice(self.images)
        reply_markup = None
        # Solution button if solution exists
        if os.path.exists(image.replace("a.png", "b.png")):
            keyboard = [
                [InlineKeyboardButton("Soluzione", callback_data=image)],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

        # Send image and solution button 
        with open(image, 'rb') as f:
            update.message.reply_photo(
                f,
                reply_markup=reply_markup
            )
    
    def show_soluz(self, update: Update, context: CallbackContext) -> None:
        query = update.callback_query
        query.answer()

        # Get solution by changing the name of the file
        image = query.data.replace("a.png", "b.png")
        with open(image, 'rb') as f:
            update.callback_query.message.reply_photo(
                f,
                reply_markup=self.new_enigma_markup
            )
    
    def start(self) -> None:
        # Create the Updater and pass it your bot's token.
        updater = Updater(TOKEN)
        
        # Get the dispatcher to register handlers
        dispatcher = updater.dispatcher
        dispatcher.add_handler(CommandHandler("start", self.welcome))
        updater.dispatcher.add_handler(CallbackQueryHandler(self.show_soluz))
        dispatcher.add_handler(MessageHandler(Filters.all, self.send_image))
        
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
                                url_path=TOKEN,
                                webhook_url="https://random-cards-bot.up.railway.app/" + TOKEN)
        updater.idle()

if __name__ == '__main__':
    bot = Bot()
    bot.start()
