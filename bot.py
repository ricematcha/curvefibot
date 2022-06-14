import logging
from multiprocessing import pool
import telegram
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
from telegram.ext import MessageHandler, Filters
from tracker import get_prices
from curvefi_tracker import get_pools
import re
import os

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    CallbackContext,
    MessageHandler,
    filters,
)

GENDER, PHOTO, LOCATION, BIO = range(4)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

PORT = int(os.environ.get('PORT', 5000))

# //Toggle off for local testing
# TOKEN = os.environ["TOKEN"]

# //Toggle on for local testing, CLEAR token variable
TOKEN = ""

POOLS = range(1)

def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    # dispatcher.add_handler(CommandHandler("start", start))
    # dispatcher.add_handler(CommandHandler("boo", boo))
    dispatcher.add_handler(CommandHandler("ethsteth", ethsteth))
    # dispatcher.add_handler(MessageHandler(Filters.text, unknown))

    # //Toggle off for local testing
    # updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN, webhook_url='https://curvefibot.herokuapp.com/' + TOKEN)
    # updater.bot.setWebhook('https://curvefibot.herokuapp.com/' + TOKEN) 
    # updater.idle()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            POOLS: [MessageHandler(Filters.text & ~Filters.command, ethsteth)],
        },
        fallbacks=[CommandHandler('cancel', cancel), CommandHandler('start', start)],
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(MessageHandler(Filters.text, unknown))

    # //Toggle on for local testing
    updater.start_polling()

    updater.idle()



def start(update: Update, context: CallbackContext) -> int:
    """Starts the conversation and ask user to input commands."""

    update.message.reply_text(
        "Hello! Welcome to the CurveFi Bot\n\n Example: Type '/ethsteth' to see details about the ETH/stETH pool"
    )

    return POOLS

def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

# def start(update, context):
#     chat_id = update.effective_chat.id
#     context.bot.send_message(chat_id=chat_id, text="Hello! Welcome to the CurveFi Bot\n\n Example: Type '/ethsteth' to see details about the ETH/stETH pool")

def unknown(update, context):
    if update.message.text[0] == "/":
        context.bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")

def ethsteth(update, context):
    chat_id = update.effective_chat.id
    message = ""
    context.bot.send_message(chat_id=chat_id, text="Polling data...")

    pool_num = 0

    if 'a' in update.message.text:
        pool_num = 0
    elif 'b' in update.message.text:
        pool_num = 1
    elif 'c' in update.message.text:
        pool_num = 2
    elif 'd' in update.message.text:
        pool_num = 3

    crypto_data = get_pools()
    coins = crypto_data[pool_num]["coins"]
    totalSupply = crypto_data[pool_num]["totalSupply"]
    if int(totalSupply) > 0:
        totalSupplySliced = float(totalSupply[0:-16])/100
    else:
        totalSupplySliced = 0
    coinPriceList = []
    totalCoinSupply = 0
    for coin in coins:
        decimals = int(coin["decimals"])
        coinPrice = coin["usdPrice"]
        coinPriceList.append(coinPrice)
        coinBalance = coin["poolBalance"]
        coinBalanceSliced = float(coinBalance[0:-decimals+2])/100
        coinTicker = coin["symbol"]
        totalCoinSupply += coinBalanceSliced
        if totalSupplySliced == 0:
            message += f"Coin: {coinTicker}\nPrice: ${coinPrice:,.2f}\nBalance: {coinBalanceSliced:,.2f} (NaN%)\n\n"
        else:
            coinPercentage = (coinBalanceSliced/totalSupplySliced)*100
            message += f"Coin: {coinTicker}\nPrice: ${coinPrice:,.2f}\nBalance: {coinBalanceSliced:,.2f} ({coinPercentage:.2f}%)\n\n"
    message += f"Total Supply: {totalCoinSupply:,.2f}\nETH/stETH Ratio: {coinPriceList[0]/coinPriceList[1]:.4f}\nstETH/ETH Ratio: {coinPriceList[1]/coinPriceList[0]:.4f}\n\n"
    context.bot.send_message(chat_id=chat_id, text=message)

def boo(update, context):
    chat_id = update.effective_chat.id
    welcome_message = "The following are the coins prices on..."
    message = ""
    context.bot.send_message(chat_id=chat_id, text=welcome_message)

    crypto_data = get_prices()
    for i in crypto_data:
        coin = crypto_data[i]["coin"]
        price = crypto_data[i]["price"]
        change_day = crypto_data[i]["change_day"]
        change_hour = crypto_data[i]["change_hour"]
        message += f"Coin: {coin}\nPrice: ${price:,.2f}\nHour Change: {change_hour:.3f}%\nDay Change: {change_day:.3f}%\n\n"

    context.bot.send_message(chat_id=chat_id, text=message)

if __name__ == '__main__':
    main()