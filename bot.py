#!/usr/bin/env python
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

import configparser

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import random

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

angry_emojis = ['😠', '😒', '💩', '🤡', '💀']
angry_responses = [ 'FAKE NEWS von', 
                    'Lüg mich nicht an', 
                    'Ich zensier dich gleich', 
                    'Recherchier lieber nochmal',
                    'Wie kommst du auf sowas Unsinniges']

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Moin! Versuche /help um herauszufinden was ich alles kann')


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Versuche /check um herauszufinden, ob etwas eine Verschwörungstheorie ist oder nicht.')


def no_command_reply(update: Update, context: CallbackContext) -> None:
    """Default reply"""
    reply(False, update, context)

def check_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    reply(True, update, context)

def reply(force_reply: bool, update: Update, context: CallbackContext) -> None:
    text = update.message.text
    name = update.message.chat.first_name
    text = text.replace('/check', '')
    text = ':\n_'+text+'_'
    text = ' '+name+text
    if(check(text)):
        update.message.reply_text(random.choice(angry_emojis)+random.choice(angry_responses)+text, parse_mode="Markdown")
    elif force_reply:
        update.message.reply_text('😎Sieht gut aus'+text, parse_mode="Markdown")


def check(theory: str):
    """return if theory is fake or not"""
    return random.choice([True, False])


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    config = configparser.ConfigParser()
    config.read('config.txt')
    token = config['TELEGRAM']['token']
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("check", check_command))

    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, no_command_reply))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()