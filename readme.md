# CoWIN Help
This repo contains code to help book vaccine slot on CoWIN. Currently, this can be used to check for slot availability in realtime.

## Realtime Slots

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
- Slots generally get available for a few seconds (for 18+ age-group) i.e. the slots get booked very fast. Therefore, I have NOT implemented any check that prevents multiple notifications from being sent.
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

Pro-tip: Find '#$' and set those variables. They will be unique to you.