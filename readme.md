#### This repo contains code to help book vaccine slot on CoWIN.
#### Can be used to:
### 1. Check for slot availability in realtime
### 2. Booking appointment using bot

<br><br>

# Realtime Slot Availability Notification on Telegram Channel
Use 'CoWIN_slots.py' to get notified about slot availability on your telegram channel.

### Important info
- Public API for checking slot availability can send results upto 30 minutes late.
- This script generates a token for using protected APIs that give realtime info about slot availability.
- This token is good for about 30 minutes after which it expires and needs to be generated again.
- Since authentication process requires OTP which is sent on SMS, this script picks OTP from a telegram channel where you will need to forward that OTP.
- For forwarding OTP message from SMS to telegram channel, you can use automation apps like IFTTT on android. You can filter the SMS to check if they contain the word 'CoWIN' so that only the required SMS are forwarded to the telegram channel. (I have not been able to find any automation for iOS.)
- The available slots are pushed to another telegram channel that you can specify.
- For using telegram in python (telethon) you will need to get your api_id and api_hash.
- You can filter the results by setting variables for district_ids, pincodes, center_ids, vaccine, age, date and number of available slots.
- If you don't want to go through the hassle of setting up to get token, you can get results without getting token as well. Just change the corresponding variable. However, the results might not be realtime.

### Miscellanious info
- Slots generally get available for a few seconds (for 18+ age-group) i.e. the slots get booked very fast. Use the companion telegram bot for booking slot quickly.
- Best way to search is to lookup slots in a particular disctrict for which you will need district_id (info on that later) and then filter by pincodes that are close to you.

#### Getting district_id
1. Get your state_id from https://cdn-api.co-vin.in/api/v2/admin/location/states.
2. Use the state_id from step 1 to get districts in the state by going to https://cdn-api.co-vin.in/api/v2/admin/location/districts/{state_id}.

### Setup help
1. Install libraries that don't come included with python using 'pip install' command. These libraries would probably be selenium-wire, telethon and requests.

    ``` pip install selenium-wire telethon requests ```

2. This script uses chrome drivers for selenium. Download the driver from https://sites.google.com/a/chromium.org/chromedriver/home and place the file in your python installation directory.
3. I recommend using separate telegram channels for sending OTP and receiving notifications. So create two separate channels on telegram and set the 'otp_channel' and 'notify_channel' with respective channel ids in creds.json.
4. Setup IFTTT or other automations on your android phone to forward SMS that contain 'CoWIN' to the OTP telegram channel.
5. Get 'api_id' and 'api_hash' for your telegram account. https://core.telegram.org/api/obtaining_api_id should help. Set your telegram 'api_id', 'api_hash' and 'username' in respective fields in creds.json.
6. Set 'mobile' in creds.json to the mobile number which you will use to authenticate on CoWIN portal.
7. Set other variables to your preference in '## CoWIN ##' section of code.
8. Run the script and keep a check on telegram for notifications.

<br>

# Vaccination Appointment Booking using Telegram Bot
Use 'CoWIN_booking.py' to book appointments for vaccination from telegram bot.

### Important info
- 'CoWIN_slots.py' should be running in LookUpType.TOKEN mode alongside since it uses the same token.
- Everything is interactive and thus, using the bot will be self explanatory.
- Use session_id obtained from 'CoWIN_slots.py' on your telegram channel.
- Set preffered time slot and dose in py file before running.
- Set beneficiary (for whom the appointment needs to be booked) in creds.json before running.

### Setup help
1. Get Bot Token using BotFather on telegram. Follow instructions at https://sendpulse.com/knowledge-base/chatbot/create-telegram-chatbot. Set 'booking_bot' field in cred.json with the token obtained.
2. Set beneficiary_id in 'beneficiary' field in cred.json. (Hint: get beneficiary_id using getBeneficiaryDetails() function in CoWIN_slots.py)
3. Set time-slot and dose number in CoWIN_booking.py at the top.
4. Install libraries python-telegram-bot and cairosvg. You might need to install telethon and requests also if you didn't setup 'Realtime Slot Availability'. (Assuming you already did the aformentioned setup)

    ``` pip install python-telegram-bot cairosvg ```

5. Install GTK3+. Follow instructions at https://weasyprint.readthedocs.io/en/stable/install.html. Might require reboot after installation to work.
6. Run the script and send '/start' on the telegram bot chat to begin.