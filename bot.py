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
from transformers import AutoTokenizer, AutoModel
import torch
from model import BinaryClassifier
import os

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

angry_emojis = ['😠', '😒', '💩', '🤡', '💀', '👮', '🚨', '💣']
angry_responses = [ 'FAKE NEWS,', 
                    'Lüg mich nicht an,', 
                    'Ich zensier dich gleich,', 
                    'Recherchier lieber nochmal,',
                    'Wie kommst du auf so einen Unsinn,',
                    'So will ich nicht nochmal sehen,']

happy_emojis = ['😎', '☺️', '🐮']
happy_responses = ['Sieht gut aus,', 'Alles klar soweit,', 'Ich sehe da kein Problem,']

excluded_phrases = ['uhh', 'uni hamburg', 'tuhh', 'tu harburg', 'haw hamburg', 'haw ']
excluded_response = [   ' 😒 Über so was möchte ich lieber nicht reden,', 
                        ' 😒 Bitte nur sinnvolle Anfragen,', 
                        ' 😒 Verschwende meine Zeit nicht mit solchen Sachen,']


# setup the ml stuff
## pre-trained
tokenizer = AutoTokenizer.from_pretrained("DeepPavlov/bert-base-multilingual-cased-sentence")
device = "cpu"
model = AutoModel.from_pretrained("DeepPavlov/bert-base-multilingual-cased-sentence").to(device)
## our classifier
classifier = BinaryClassifier(768, 2).to(device)
classifier.load_state_dict(torch.load('classifier.pt'))

threshold = float(os.environ["threshold"])

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
    text = update.message.text.replace('/check', '')
    text = text.replace('/Check', '')
    name = update.message.chat.first_name
    if name is None:
        name = 'du Lümmel'
    reply_text = ', '+name+':\n_'+text+'_'
    if check_exclusion(text):
        update.message.reply_text(random.choice(excluded_response)+reply_text, parse_mode="Markdown")
    else:
        probability = check(text)
        reply_text = reply_text +'\n ist zu '+str(int(probability*100))+'% eine Verschwörungstheorie'
        if(probability > threshold):
            
            update.message.reply_text(random.choice(angry_emojis)+' '+random.choice(angry_responses)+reply_text, parse_mode="Markdown")
        elif force_reply:
            update.message.reply_text(random.choice(happy_emojis)+' '+random.choice(happy_responses)+reply_text, parse_mode="Markdown")

def check_exclusion(theory: str):
    """return if it should later be ignored"""
    theory_lower_case = theory.lower()
    for phrase in excluded_phrases:
        if phrase in theory_lower_case:
            return True
    
    return False

def check(theory: str):
    """return if theory is fake or not"""
    logger.info('checking: '+theory)
    inp = tokenizer(theory, padding = True, truncation= True, return_tensors = "pt").to(device)
    embedding = model(**inp)[1]
    classifier.eval()
    a = torch.nn.Softmax()
    x = a(classifier(embedding)[1])
    x = x.tolist()[0]
    logger.info(x)
    return x[0]

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary

    token = os.environ["token"]
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