#!/usr/bin/env python3

import telegram
from flask import Flask, request

# Configuration
BOTNAME = 'examplebot'  # The name of the bot, without @
TOKEN = ''  # Security Token given from the @BotFather
BASE_URL = 'sub.example.com'  # Domain name of your server, without protocol. You may include a port, if you dont want to use 443.
HOST = '0.0.0.0'  # IP Address on which Flask should listen on
PORT = 5000  # Port on which Flask should listen on

CERT     = '/etc/pki/tls/certs/examplebot.pem'
CERT_KEY = '/etc/pki/tls/certs/examplebot.key'

ABOTNAME = '@' + BOTNAME
CONTEXT = (CERT, CERT_KEY)

app = Flask(__name__)

global bot
bot = telegram.Bot(token=TOKEN)

global helptext_en
helptext_en  = 'Receive Telegram messages on push events in your GitLab- and GitHub-Repositories \n\n'
helptext_en += '*Usage:* \n\n'
helptext_en += '*1.* Optional: Invite me to a group!\n'
helptext_en += '*2.* Run the command /register\\_git\n'
helptext_en += '*3.* Copy the URL you get and add it as a webhook in your project under _Settings_ ➡️ _Web Hooks_. Only push events are supported right now.\n'
helptext_en += '*4.* From GitHub, you\'ll receive a message, with GitLab you can test the functionality of the bot with _Test Hook_\n\n'
helptext_en += "Thanks for using _Jannes' GitBot_!\n"
helptext_en += 'PS: You can always read this again with the command /help. Questions? Message my creator @jh0ker :)'

# Helper function to escape telegram markup symbols
def escape_markdown(text):
    text = text.replace('_', '\\_')
    text = text.replace('*', '\\*')
    return text

# The Webhook for GitLab and GitHub
@app.route('/webhook_git/<chat_id>', methods=['GET', 'POST'])
def git_webhook_handler(chat_id):
    try:
        if request.method == "POST":
        
            data = request.get_json(force=True)
            
            # Adjust for differences in GitLab and GitHub
            name = None
            if 'object_kind' in data and data['object_kind'] == 'push':  # GitLab
                name = data['user_name']
            elif 'pusher' in data:  # GitLab
                name = data['pusher']['name']
            elif 'hook' in data:  # GitHub-Webhook activated
                bot.sendMessage(chat_id=int(chat_id), text='GitHub-Hook for %s activated!' % data['repository']['full_name'])
                return ''
                
            if 'name' in data['repository']:  # GitLab
                repo = data['repository']['name']
            elif 'full_name' in data['repository']:  # GitHub
                repo = data['repository']['full_name']
            else:
                repo = '<unknown>'
            
            repo += '/' + data['ref'].split('/')[-1]
                
            # Construct message and send it to the chat
            if name is not None:
                text = '⬆️ *%s* pushed to %s:\n' % (escape_markdown(name), escape_markdown(repo))
                
                for commit in data['commits']:
                    text += '*%s*: %s%s' % (escape_markdown(commit['author']['name']), escape_markdown(commit['message']), 
                            ('\n' if commit['message'][-1] != '\n' else ''))
                
                text += '[Check last commit...](%s)' % escape_markdown(data['commits'][-1]['url'])
                
                bot.sendMessage(chat_id=int(chat_id), text=text, parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True)
            
            else:
                print('WARNING: Unknown git request!')
                print(data)
                
    except:
        traceback.print_exc()

    return ''
        
# Generate git webhook. No persistence needed, we just use the chat_id
def register_git(update):
    chat_id = update.message.chat.id
    
    text = 'Your personal Webhook: https://%s/webhook_git/%d' % (BASE_URL, chat_id)
    bot.sendMessage(chat_id=chat_id, text=text)
    
    return 'ok'
    
# Print help text
def help(update):
    chat_id = update.message.chat.id
    
    bot.sendMessage(chat_id=chat_id, text=helptext_en, parse_mode=telegram.ParseMode.MARKDOWN)
    
    return 'ok'

# The webhook for Telegram messages
@app.route('/webhook_tg', methods=['POST'])
def tg_webhook_handler():
    if request.method == "POST":
        
        # retrieve the message in JSON and then transform it to Telegram object
        update = telegram.Update.de_json(request.get_json(force=True))
        # Message is empty
        
        text = update.message.text
        
        # split command into list of words and remove mentions of botname
        text = list([word.replace(ABOTNAME, '') for word in filter(lambda word2: word2 != ABOTNAME, text.split())])
        
        # Bot was invited to a group chat
        if update.message.new_chat_participant is not None and update.message.new_chat_participant.username == BOTNAME:
            return help(update)
        # Run commands
        elif len(text) is 0:
            return 'ok'
        elif text[0] == '/register_git':
            return register_git(update)
        elif text[0] == '/help' or text[0] == '/start':
            return help(update)
            
    return 'ok'


# Go to https://BASE_URL/set_webhook with your browser to register the telegram webhook of your bot
# You may want to comment out this route after triggering it once
@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('https://%s/%s' % (BASE_URL, TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"

# Confirm that the bot is running and accessible by going to https://BASE_URL/ with your browser
@app.route('/')
def index():
    return 'Gitbot is running!'
    
# Start Flask with SSL handling
app.run(host=HOST,port=PORT, ssl_context=CONTEXT, threaded=True, debug=False)

# Start Flask without SSL handling
#app.run(host=HOST,port=PORT, threaded=True, debug=False)

