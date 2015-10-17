# Simple-Echo-Telegram-Bot
_A Python Telegram bot that notifies you via Telegram if there is a push event in one of your repositories_

It uses the Flask microframework and the [python-telegram-bot](https://github.com/leandrotoledo/python-telegram-bot) library. It's based on this [example](https://github.com/sooyhwang/Simple-Echo-Telegram-Bot).

The file is prepared to be run by anyone by filling out the blanks in the configuration.

## Required
* Python 3.4 (may work with earlier versions, untested)
* [python-telegram-bot](https://github.com/leandrotoledo/python-telegram-bot) module (tested with version 2.5)
* [Flask](http://flask.pocoo.org/) microframework (tested with version 0.10.1)

## How to use
* Install the script
* Edit BOTNAME, TOKEN, BASE_URL, HOST and PORT in bot.py
* Visit https://BASE_URL/set_webhook on your web browser to set up webhook.
* Follow Bot instructions

_Important: You need to have a working SSL setup to use the Telegram API_
