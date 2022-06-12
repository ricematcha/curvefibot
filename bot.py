import telegram
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
from tracker import get_prices
from curvefi_tracker import get_pools
import re
import os

PORT = int(os.environ.get('PORT', 5000))
TOKEN = os.environ["TOKEN"]

def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    # dispatcher.add_handler(CommandHandler("boo", boo))
    dispatcher.add_handler(CommandHandler("ethsteth", ethsteth))
    # updater.start_polling()
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN, webhook_url='https://curvefibot.herokuapp.com/' + TOKEN)
    updater.bot.setWebhook('https://curvefibot.herokuapp.com/' + TOKEN) 
    updater.idle()

def start(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text="Hello! Welcome to the CurveFi Bot")

def ethsteth(update, context):
    chat_id = update.effective_chat.id
    message = ""

    crypto_data = get_pools()
    coins = crypto_data[14]["coins"]
    totalSupply = crypto_data[14]["totalSupply"]
    totalSupplySliced = float(totalSupply[0:-16])/100
    coinPriceList = []
    for coin in coins:
        coinPrice = coin["usdPrice"]
        coinPriceList.append(coinPrice)
        coinBalance = coin["poolBalance"]
        coinBalanceSliced = float(coinBalance[0:-16])/100
        coinPercentage = (coinBalanceSliced/totalSupplySliced)*100
        coinTicker = coin["symbol"]
        message += f"Coin: {coinTicker}\nPrice: ${coinPrice:,.2f}\nBalance: {coinBalanceSliced:,.2f} ({coinPercentage:.2f}%)\n\n"
    message += f"Total Supply: {totalSupplySliced}\nETH/stETH Ratio: {coinPriceList[0]/coinPriceList[1]:.4f}\nstETH/ETH Ratio: {coinPriceList[1]/coinPriceList[0]:.4f}\n\n"
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