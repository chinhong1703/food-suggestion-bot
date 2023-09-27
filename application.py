"""
Food suggestion bot
"""

import logging
import os
import sys
from dbhelper import DBHelperFood, DBHelperLog
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ApplicationBuilder
from datetime import datetime, timedelta
import random

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
db = DBHelperFood()
db_log = DBHelperLog()
# Load food suggestions from db.txt file 
with open('db.txt', 'r') as f:
    allFoods = [line.strip() for line in f]


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
async def start(update, context):
    features = [
        [InlineKeyboardButton("Suggest Food For Me", callback_data="suggest")],
        [InlineKeyboardButton("View Food Suggestions List", callback_data="view")],
        [InlineKeyboardButton("Add/Delete/Log Food", callback_data="edit")],
        [InlineKeyboardButton("View Personal Food Log", callback_data="view-log")]]
    reply_markup = InlineKeyboardMarkup(features)
    await context.bot.send_message(chat_id=update.effective_chat.id,text="Hi! Welcome to Food Suggestions Bot!")
    await context.bot.send_message(chat_id=update.effective_chat.id,text="What do you want to do?", reply_markup=reply_markup)
    logger.info("/start Command triggered")


async def button(update, context):
    query = update.callback_query
    chat_id = query.from_user['id']

    if query.data == "edit":
        await query.edit_message_text(text="You chose: {}".format("Add/Delete Food"))
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Use /add <food> to add food suggestion \n" \
                                          "Use /delete to delete food suggestion \n" \
                                          "Use /log <food> to log and add your custom food to suggestions")
        logger.info("Edit option selected")

    if query.data == "suggest":
        await query.edit_message_text(text="You chose: {}".format("Suggest Food For Me"))
        '''To do: fetch and send food suggestion'''
        personalList = db.get_items(chat_id)
        foodList = allFoods.copy()
        foodList.extend(personalList)
        suggestions = random.sample(foodList, 5)
        message = "Here's your suggestions for your meal. \n \n"
        newFunc = True
        if newFunc:
            # new function to remember note food suggested into table
            keyboard = []
            for food in suggestions:
                temp = [InlineKeyboardButton(food.title(), callback_data="log " + food)]
                keyboard.append(temp)
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_markup)
            await context.bot.send_message(chat_id=update.effective_chat.id, text="If my suggestion helped you, choose what you had and I will log your meal! \n \nYou can also use /suggest to suggest again.")
        else:
            # old function, just returns a message
            i = 0
            for food in suggestions:
                i += 1
                message += "%d. %s" % (i, food.title())
                if i < 5:
                    message += "\n"
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        logger.info("Food suggestion sent to user: {}".format(chat_id))

    if query.data == "view":
        await query.edit_message_text(text="You chose: {}".format("View Food Suggestions List"))
        '''view personal food suggestions'''
        resultsPersonalList = db.get_items(chat_id)
        if resultsPersonalList == []:
            context.bot.send_message(chat_id, "You have not added any food yet.")
            return
        resultsPersonal = ", ".join(resultsPersonalList).title()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=
                                 "Your Personal Food Suggestions are currently: {}. \n==== \nUse /viewall to view the full list of built in food suggestions.".format(
                                     resultsPersonal))

    if query.data == "view-log":
        await query.edit_message_text(text="You chose: {}".format("View Personal Food Log"))
        '''view food log'''
        result = db_log.get_items(chat_id)
        if result == []:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="You have not logged any food yet.")
            return
        message = "Your food log is as follows: \n"
        message += "Date" + " " * 27 + "Food \n"
        for log in result:
            date = log[2].strftime("%m/%d/%Y, %H:%M")
            food = log[0].title()
            message += "%s \t %s \n" % (date, food)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        logger.info("User:%d viewed personal log." % (chat_id))

    if query.data[:2] == "d ":
        '''delete selection'''
        food = query.data[2:]
        db.delete_item(food, chat_id)
        await query.edit_message_text(text='"{}" deleted successfully.'.format(food.title()))
        logger.info('"{}" deleted by user {}'.format(food, chat_id))

    if query.data[:4] == "log ":
        '''Inline logging of food'''
        food = query.data[4:].lower()
        # convert to GMT +8 time
        now = datetime.now() + timedelta(hours=8)
        date_time = now.strftime("%d/%m/%Y, %H:%M")
        date_time_sql = now.strftime('%Y-%m-%d %H:%M:%S')
        # add to sql
        db_log.add_item(food, chat_id, date_time_sql)
        await query.edit_message_text(text='Food logged successfully: "%s" at %s' % (food.title(), date_time))
        logger.info("Food logged: %s at %s by user: %d" % (food, date_time, chat_id))


async def add_food(update, context):
    chat_id = update.message.chat_id
    food_db = db.get_items(chat_id)
    try:
        # Fetch user argument

        food = " ".join(context.args).lower()
        # check if food is already in the user's list
        if food == "":
            update.message.reply_text('Usage: /add <food>')
            logger.info("Empty keyword detected")
            return
        if food in food_db:
            update.message.reply_text("Sorry the food is already in your suggestions list.")
            return
        # add food to user's list.
        db.add_item(food, chat_id)
        update.message.reply_text('New food "{}" added succcessfully! '.format(food))
        logger.info("New food added: %s by user: %d" % (food, chat_id))

    except(IndexError, ValueError):
        update.message.reply_text('Usage: /add <food>')
        logger.info("Invalid keyword added")


async def log_food(update, context):
    food = " ".join(context.args).lower()
    chat_id = update.message.chat_id
    # check for improper usage
    if food == "":
        update.message.reply_text('Usage: /log <food>')
        logger.info("Empty keyword detected")
        return
    # add to log table
    now = datetime.now() + timedelta(hours=8)
    date_time = now.strftime("%d/%m/%Y, %H:%M")
    date_time_sql = now.strftime('%Y-%m-%d %H:%M:%S')
    db_log.add_item(food, chat_id, date_time_sql)

    update.message.reply_text(text="Food logged successfully: %s at %s" % (food.title(), date_time))
    logger.info("Food logged: %s at %s by user: %d" % (food, date_time, chat_id))
    # pass to add food
    add_food(update, context)


async def del_food(update, context):
    '''Display food for deleting'''
    chat_id = update.message.chat_id
    food_db = db.get_items(chat_id)
    if food_db == []:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You have not added any food yet.")
        return
    keyboard = []
    for food in food_db:
        temp = [InlineKeyboardButton(food.title(), callback_data="d " + food)]
        keyboard.append(temp)
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Select food to be deleted:', reply_markup=reply_markup)
    logger.info("/delete triggered by user: {}".format(chat_id))


async def view_all_food(update, context):
    """Display all food suggestions from txt."""
    chat_id = update.message.chat_id
    resultsGlobal = ", ".join(allFoods)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Global Food Suggestions are currently: \n{}.".format(resultsGlobal))
    logger.info("/viewall triggered by user: %d" % (chat_id))


async def suggest_food(update, context):
    '''Suggest command'''
    chat_id = update.message.chat_id
    personalList = db.get_items(chat_id)
    foodList = allFoods.copy()
    foodList.extend(personalList)
    suggestions = random.sample(foodList, 5)
    message = "Here's your suggestions for your meal. \n \n"

    keyboard = []
    for food in suggestions:
        temp = [InlineKeyboardButton(food.title(), callback_data="log " + food)]
        keyboard.append(temp)
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_markup)
    logger.info("/suggest command triggered by user: %d" % (chat_id))


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Run bot."""
    mode = os.getenv("MODE")
    TOKEN = os.getenv("TOKEN")

    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    application = ApplicationBuilder().token(TOKEN).build()

    # Get the dispatcher to register handlers
    # dp = updater.dispatcher

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("add", add_food))
    application.add_handler(CommandHandler("delete", del_food))
    application.add_handler(CommandHandler("viewall", view_all_food))
    application.add_handler(CommandHandler("suggest", suggest_food))
    application.add_handler(CommandHandler("log", log_food))
    # log all errors
    application.add_error_handler(error)

    # Start the Bot
    logger.info("Starting bot")
    db.setup()
    db_log.setup()
    if mode == "dev":
        application.run_polling()
    else:
        logger.error("No MODE specified!")
        sys.exit(1)

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.


if __name__ == '__main__':
    main()
