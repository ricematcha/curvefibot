import logging
from multiprocessing import pool
from tracker import get_prices
import telegram
from curvefi_tracker import get_pools
import os

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    ConversationHandler,
    CallbackContext,
    MessageHandler,
    Filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

PORT = int(os.environ.get('PORT', 5000))

# //Toggle off for local testing
TOKEN = os.environ["TOKEN"]

# //Toggle on for local testing, CLEAR token variable
# TOKEN = ""

POOLS = range(1)

def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            POOLS: [MessageHandler(Filters.text & ~Filters.command, pools)],
        },
        fallbacks=[CommandHandler('cancel', cancel), CommandHandler('start', start)],
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(MessageHandler(Filters.text, unknown))

    # //Toggle on for local testing
    # updater.start_polling()
    # updater.idle()

    # //Toggle off for local testing
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN, webhook_url='https://curvefibot.herokuapp.com/' + TOKEN)
    updater.bot.setWebhook('https://curvefibot.herokuapp.com/' + TOKEN) 
    updater.idle()



def start(update: Update, context: CallbackContext) -> int:
    """Starts the conversation and ask user to input commands."""
    user = update.message.from_user
    logger.info("User %s has started the conversation.", user.first_name)
    update.message.reply_text(
        "Hello! Welcome to the CurveFi Bot\n\nExample: Type 'ETH STETH' to see details about the ETH/stETH pool"
    )

    return POOLS

def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! Thank you for using CurveFi Bot, do let us know if you have any feedback', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def unknown(update, context):
    if update.message.text[0] == "/":
        context.bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")

def pools(update, context):
    chat_id = update.effective_chat.id
    message = ""

    # pool_num = 0

    dict_of_pools = {'DAI USDC USDT': 0, 'ADAI AUSDC AUSDT': 1, 'ETH AETHC': 2, 'YDAI YUSDC YUSDT YBUSD': 3, 'CDAI CUSDC': 4, 'EURS SEUR': 5, 'HBTC WBTC': 6,
                    'IDAI IUSDC IUSDT': 7, 'LINK SLINK': 8, 'YCDAI YCUSDC YCUSDT USDP': 9, 'RENBTC WBTC': 10, 'ADAI ASUSD': 11, 'RENBTC WBTC SBTC': 12, 'ETH SETH': 13,
                    'ETH STETH': 14, 'DAI USDC USDT SUSD': 15, 'CDAI CUSDC CUSDT': 16, 'YDAI YUSDC YUSDT YTUSD': 17, 'DUSD 3CRV': 18, 'GUSD 3CRV': 19,
                    'HUSD 3CRV': 20, 'LINKUSD 3CRV': 21, 'MUSD 3CRV': 22, 'RSV 3CRV': 23, 'USDK 3CRV': 24, 'USDN 3CRV': 25, 'USDP 3CRV': 26, 'UST 3CRV': 27,
                    'BBTC CRVRENWSBTC': 28, 'OBTC CRVRENWSBTC': 29, 'PBTC CRVRENWSBTC': 30, 'TBTC CRVRENWSBTC': 31, 'TUSD 3CRV': 32, 'LUSD 3CRV': 33,
                    'FRAX 3CRV': 34, 'BUSD 3CRV': 35, 'ETH RETH': 36, 'ALUSD 3CRV': 37, 'USDT WBTC WETH': 38, 'RAI 3CRV': 39, 'MIM 3CRV': 40, 'EURT SEUR': 41,
                    'USDC USDT UST FRAX': 42, 'USDC USDT': 43}

    if update.message.text.upper() not in dict_of_pools:
        poolCannotBeFound_message = f"The pool you have listed cannot be found: {update.message.text}\n\nPlease make sure it is the right pool. Naming of pools are all case-insensitive\n\nThese are the list of pools:\n\n"
        poolsDictMessage = ""
        for key in dict_of_pools:
            poolsDictMessage += f"{dict_of_pools[key]+1}: {key}\n"
        context.bot.send_message(chat_id=chat_id, text=poolCannotBeFound_message)
        context.bot.send_message(chat_id=chat_id, text=poolsDictMessage)
    elif update.message.text.upper() in dict_of_pools:
        pool_num = dict_of_pools[update.message.text.upper()]

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
                message += f"*{coinTicker}*\nPrice: ${coinPrice:,.2f}\nBalance: {coinBalanceSliced:,.2f} (NaN%)\n\n"
            else:
                coinPercentage = (coinBalanceSliced/totalSupplySliced)*100
                message += f"*{coinTicker}*\nPrice: ${coinPrice:,.2f}\nBalance: {coinBalanceSliced:,.2f} ({coinPercentage:.2f}%)\n\n"
        message += f"Total Supply: {totalCoinSupply:,.2f}\n"
        # ratioMessage += f"ETH/stETH Ratio: {coinPriceList[0]/coinPriceList[1]:.4f}\nstETH/ETH Ratio: {coinPriceList[1]/coinPriceList[0]:.4f}\n\n"
        context.bot.send_message(chat_id=chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN)

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