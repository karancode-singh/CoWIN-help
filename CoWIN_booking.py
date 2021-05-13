## Assumes that CoWIN_slots.py is running in LookUpType.TOKEN mode

slot = "11:00AM-01:00PM"
dose = 1

from cairosvg import svg2png
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
import requests
from requests.structures import CaseInsensitiveDict
import json
import os

try:
    with open('creds.json') as f:
        creds = json.loads(f.read())
except:
    print('Creds not present')
    exit()

# use_custom_token = False
token = ''
user_captcha = ''
session_id = ''
beneficiary = creds['beneficiary']
beneficiaries = []
if(len(beneficiary)>1):
    beneficiaries.append(beneficiary)
base_url = 'https://cdn-api.co-vin.in/api'

headers = CaseInsensitiveDict()
headers["Accept"] = "*/*"
headers["User-Agent"] = "PostmanRuntime/7.28.0"

def cowin_token_expired_routine():
    os.remove("temp_token.txt")
    return 'cowin token has expired'

def get_captcha():
    ext_url = '/v2/auth/getRecaptcha'
    url = base_url + ext_url
    resp = requests.post(url, headers=headers)
    if resp.status_code != 200:
        print('ERROR')
        print('api: ',ext_url)
        print('code: ',resp.status_code)
        print('message: ',resp.text)
        if resp.status_code==401:
            return cowin_token_expired_routine()
        else:
            return resp.text
    else:
        svg_str = json.loads(resp.text)['captcha']
        svg2png(bytestring=svg_str,write_to='temp_captcha.png')
        return True

def book_session():
    global session_id
    ext_url = '/v2/appointment/schedule'
    url = base_url + ext_url
    data = {
        "dose": dose,
        "session_id": session_id,
        "slot": slot,
        "beneficiaries": beneficiaries,
        "captcha": user_captcha
    }
    print(json.dumps(data))
    resp = requests.post(url, headers=headers, data=json.dumps(data))
    if resp.status_code != 200:
        print('ERROR')
        print('api: ',ext_url)
        print('code: ',resp.status_code)
        print('message: ',resp.text)
        if resp.status_code==401:
            return cowin_token_expired_routine()
        elif resp.status_code==400:
            if json.loads(resp.text)['errorCode']=="APPOIN0045":
                return True
            else:
                return resp.text
        else:
            return resp.text
    else:
        print(resp.text)
        return resp.text


SESSION, BENEFICIARIY, CAPTCHA = range(3)

def start(update: Update, _: CallbackContext) -> int:
    try:
        with open('temp_token.txt','r') as f:
            token = f.readline()
            headers["Authorization"] = "Bearer "+token
            print(token)
    except:
        update.message.reply_text('Token file doesn\'t exist')
        return ConversationHandler.END
    captcha = get_captcha()
    if type(captcha)==str:
        update.message.reply_text(captcha)
        return ConversationHandler.END
    update.message.reply_text("Send session_id")
    return SESSION

def session(update: Update, _: CallbackContext) -> int:
    global session_id
    session_id = update.message.text
    print(session_id)
    if len(beneficiaries)>0:
        update.message.reply_photo(open('temp_captcha.png','rb'))
        return CAPTCHA
    else:
        update.message.reply_text("Send beneficiary_id")
        return BENEFICIARIY

def beneficiary(update: Update, _: CallbackContext) -> int:
    beneficiaries.append(update.message.text)
    return BENEFICIARIY

def captcha(update: Update, _: CallbackContext) -> int:
    global session_id
    global user_captcha
    print(session_id)
    user_captcha = update.message.text
    result = book_session()
    if(result==True):
        captcha = get_captcha()
        if type(captcha)==str:
            update.message.reply_text(captcha)
            return ConversationHandler.END
        else:
            update.message.reply_photo(open('temp_captcha.png','rb'))
            return CAPTCHA
    update.message.reply_text(str(result))
    return ConversationHandler.END

def cancel(update: Update, _: CallbackContext) -> int:
    update.message.reply_text("Operation cancelled")
    return ConversationHandler.END

def main():
    updater = Updater(creds['booking_bot'], use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
        ],
        states={
            SESSION: [MessageHandler(Filters.text & ~Filters.command, session)],
            BENEFICIARIY: [MessageHandler(Filters.text & ~Filters.command, beneficiary)],
            CAPTCHA: [MessageHandler(Filters.text & ~Filters.command, captcha)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()