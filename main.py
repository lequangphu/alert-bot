import json
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import telebot

# load secrets to connect to google sheets and telegram
with open('/Users/phu/alert-bot-for-Tris/Secrets/secrets.json') as f:
    secrets = json.load(f)

# g-sheets credentials
scope = ['https://www.googleapis.com/auth/spreadsheets.readonly']
creds_json = secrets['GOOGLE_SHEETS_CREDENTIALS']
creds_dict = json.loads(creds_json)
creds = Credentials.from_service_account_info(info=creds_dict, scopes=scope)

# g-sheets id, range
sheet_id = secrets['GOOGLE_SHEETS_ID']
SHEET_NAME = 'Current'
SHEET_RANGE = 'A1:I'

# Authenticate with the Google Sheets API
client = gspread.authorize(creds)

# read data to a dataframe
sheet = client.open_by_key(sheet_id).worksheet(SHEET_NAME)
data = sheet.get(SHEET_RANGE)
df = pd.DataFrame(data=data[1:], columns=data[0])

df = df[
    # drop null URLs & null End time
    df['URLs'].notnull() & df['End time'].notnull()
    # drop status Done or Completed by others
    & ~df['Status'].isin(('Done', 'Completed by others'))
]

# create col message
df['Message'] = [f"Appeal no: {row['Appeal Number']}, expired at: {row['End time']}, visit: {row['URLs']}" for index, row in df.iterrows()]

# telegram bot
bot_token = secrets['TELEGRAM_BOT_TOKEN']
group_chat_id = secrets['TELEGRAM_GROUP_CHAT_ID']
bot = telebot.TeleBot(bot_token)

# filter the dataframe to get rows where End time is less than 5 minutes before current time
time_delta = pd.Timestamp.now() - pd.to_datetime(df['End time'], format='%m/%d/%Y %H:%M:%S') # type: ignore
# print(time_delta)
expired_filter = time_delta.apply(lambda x: pd.Timedelta('0 minutes') < x < pd.Timedelta('5 minutes'))
# print(expired_filter)
df_filtered = df[expired_filter]

# check if df is empty or not
if df_filtered.empty:
    print("No expired appeal.")
else:
    # iterate over the rows of the filtered dataframe and send messages to the group chat
    for index, row in df_filtered.iterrows():
        bot.send_message(chat_id=group_chat_id, text=row['Message'])