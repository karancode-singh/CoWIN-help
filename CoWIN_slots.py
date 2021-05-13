import requests
from requests.structures import CaseInsensitiveDict
import json
from seleniumwire import webdriver
from time import time, sleep
from datetime import datetime, date, timedelta
from enum import Enum

class LookUpBy(Enum):
    DISTRICT = 'DISTRICT'
    PIN = 'PIN'
class LookUpType(Enum):
    TOKEN = 'TOKEN'
    WO_TOKEN = 'WO_TOKEN'
class VaccineType(Enum):
    NO_PREF = ''
    COVAXIN = 'COVAXIN'
    COVISHIELD = 'COVISHIELD'
class FilterType(Enum):
    NONE = ''
    CENTER = 'center_id'
    PIN = 'pincode'

try:
    with open('creds.json') as f:
        creds = json.loads(f.read())
except:
    print('Creds not present')
    exit()

from telethon import TelegramClient, events, sync
## Telegram ##
api_id = creds['api_id']
api_hash = creds['api_hash']
username = creds['username']
client = TelegramClient(username, api_id, api_hash)
client.start()

otp_channel = creds['otp_channel']
notify_channel = creds['notify_channel']
##############

## CoWIN ##
mobile = creds['mobile']
look_up_type = LookUpType.TOKEN
look_up_by = LookUpBy.DISTRICT
look_up_val = '146'
date = (date.today()+timedelta(days=1)).strftime("%d-%m-%Y") #'13-05-2021'
vaccine = VaccineType.COVISHIELD
filter_type = FilterType.PIN
filter_val = [110039]
min_age = 53
min_available_capacity=10
###########

## consts ##
check_interval = 30

max_retry_count = 5
resend_otp_time = 180
try_otp_for_time = 150
otp_length = 6


url = 'https://selfregistration.cowin.gov.in/'

base_url = 'https://cdn-api.co-vin.in/api'

headers = CaseInsensitiveDict()
headers["Accept"] = "*/*"
headers["User-Agent"] = "PostmanRuntime/7.28.0"

############


def delete_messages_from_channel(channel_name):
    for message in client.get_messages(channel_name,limit=None):
        client.delete_messages(channel_name, message)

def notify_result(result):
    # if(len(result)>5):
    #     delete_messages_from_channel(notify_channel) ## OPTIONAL
    #     print("Old messages deleted from "+notify_channel)
    print("TELEGRAM MESSAGE: ", result)
    client.send_message(notify_channel, json.dumps(result,indent=2))

def getOTPfromTelegram():
    # Get last OTP so that the last OTP is not reused if it was received less than 3 minutes ago.
    try:
        with open('last_otp.txt', 'r') as f:
            last_otp = f.readlines()
    except:
        last_otp = ''  
    time_started = time()
    while(True):
        sleep(2)
        sms_date = datetime(2021,1,1)
        for message in client.get_messages(otp_channel, limit=1):
            print(message.message)
            sms = message.text
            sms_date = message.date
        if time()-sms_date.timestamp() < try_otp_for_time:
            text = 'CoWIN is '
            offset = len(text)
            loc = sms.find(text)
            sms_otp = sms[ loc+offset : loc+offset+otp_length ]
            if last_otp==sms_otp:
                continue
            else:
                return sms_otp
        elif time()-time_started > resend_otp_time:
            return ''

def requestOTP():
    while(True):
        try_count = 0
        while(try_count<max_retry_count):
            try:
                driver.get(url)
                sleep(3)
                element = driver.find_element_by_id("mat-input-0")
                element.send_keys(mobile)
                element = driver.find_element_by_class_name("login-btn")
                del driver.requests
                element.click()
                try_count = 99
            except:
                try_count += 1
        if try_count==max_retry_count:
            print('Unable to fetch '+url)
            return False

        sleep(5)
        try_count = 0
        while(try_count<max_retry_count):
            sleep(1)
            for request in driver.requests:
                if request.response and request.url=='https://cdn-api.co-vin.in/api/v2/auth/generateMobileOTP':
                    if 'txnId' in request.response.body.decode():
                        return True
            try_count += 1
        print('Unable to send OTP to '+mobile)
        return False

def get_new_token():
    otp=''
    token=''

    while (otp==''):
        requestOTP()
        sleep(5)
        otp = getOTPfromTelegram()

    with open('last_otp.txt', 'w') as f:
        f.write(otp)

    element = driver.find_element_by_id("mat-input-1")
    flag=True
    while(flag):
        try:
            flag = False
            element.send_keys(otp)
        except:
            sleep(1)
            flag = True
    element = driver.find_element_by_class_name("vac-btn")
    del driver.requests
    element.click()
    sleep(5)

    while(token==''):
        sleep(2)
        for request in driver.requests:
            if request.response and request.url=='https://cdn-api.co-vin.in/api/v2/auth/validateMobileOtp':
                response = json.loads(request.response.body.decode())
                if type(response)==dict and 'token' in response:
                    token = response['token']
                    print(token)
    headers["Authorization"] = "Bearer "+token
    return token

def getBeneficiaryDetails():
    ext_url = '/v2/appointment/beneficiaries'
    url = base_url + ext_url
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print('ERROR')
        print('api: ',ext_url)
        print('code: ',resp.status_code)
        print('message: ',resp.text)
        if resp.status_code==401:
            return False
    else:
        print(resp.json())
        return True

def filter(data):
    result = []
    for center in data['centers']:
        if filter_type.value==FilterType.NONE.value or center[filter_type.value] in filter_val:
            sessions = center['sessions']
            for session in sessions:
                if session['min_age_limit']<=min_age and session['available_capacity']>=min_available_capacity:
                    result.append( {
                        'center_id':center['center_id'],
                        'name':center['name'],
                        'address':center['address'],
                        'district_name':center['district_name'],
                        'pincode':center['pincode'],
                        'session': {
                            'session_id':session['session_id'],
                            'date':session['date'],
                            'available_capacity':session['available_capacity'],
                            'min_age_limit':session['min_age_limit'],
                            'vaccine':session['vaccine'],
                        }
                    })
    return result

def getDataByDistrict():
    ext_url = '/v2/appointment/sessions/calendarByDistrict?district_id='+look_up_val+'&date='+date
    if(look_up_type==LookUpType.TOKEN and vaccine!=VaccineType.NO_PREF):
        ext_url += '&vaccine='+vaccine.value
    url = base_url + ext_url
    # print(url) ##
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print('ERROR')
        print('api: ',ext_url)
        print('code: ',resp.status_code)
        print('message: ',resp.text)
        if resp.status_code==401:
            return False
    else:
        # print(resp.json()) ##
        result = filter(resp.json())
        notify_result(result)
        return True

def getDataByPin():
    ext_url = '/v2/appointment/sessions/calendarByPin?pincode='+look_up_val+'&date='+date
    if(look_up_type==LookUpType.TOKEN and vaccine!=VaccineType.NO_PREF):
        ext_url += '&vaccine='+vaccine.value
    url = base_url + ext_url
    # print(url) ##
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print('ERROR')
        print('api: ',ext_url)
        print('code: ',resp.status_code)
        print('message: ',resp.text)
        if resp.status_code==401:
            return False
    else:
        # print(resp.json()) ##
        print(resp)
        result = filter(resp.json())
        notify_result(result)
        return True

if (look_up_type==LookUpType.TOKEN):
    driver = webdriver.Chrome()
token = ''
sms = ''
sms_date = datetime(2021,1,1)

while(True):
    if (look_up_type==LookUpType.TOKEN):
        print("GETTING NEW TOKEN")
        # token = ''
        # headers["Authorization"] = "Bearer "+token
        token = get_new_token()
        # delete_messages_from_channel(otp_channel) ## OPTIONAL
        # getBeneficiaryDetails()
    if(look_up_by==LookUpBy.DISTRICT):
        while(getDataByDistrict()):
            print("Just checked by district. Waiting for ",check_interval," seconds.")
            sleep(check_interval)
    if(look_up_by==LookUpBy.PIN):
        while(getDataByPin()):
            print("Just checked by pin. Waiting for ",check_interval," seconds.")
            sleep(check_interval)