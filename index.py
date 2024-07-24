from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import PeerUser, users
import pandas as pd

channel = 'https://t.me/shveinidvor'

def get_client():
  # Use your own values from my.telegram.org
  api_id = 28682163
  api_hash = '75dc5f8c3fa7b949f626823ad456402b'
  device_model = 'My Script'

  return TelegramClient(session='client', api_id=api_id, api_hash=api_hash, device_model=device_model)

client = get_client()

async def get_user_ids():
  channel = await client.get_entity(channel)
  offset_id = 0
  limit = 100
  user_ids = []

  while True:
    history = await client(GetHistoryRequest(
      peer=channel,
      offset_id=offset_id,
      offset_date=None,
      add_offset=0,
      limit=limit,
      max_id=0,
      min_id=0,
      hash=0
    ))
    print('history loaded offset ' + str(offset_id))

    if not history.messages:
      break

    messages = history.messages

    for message in messages:
      if message.from_id and message.from_id.user_id and isinstance(message.from_id, PeerUser) and message.from_id.user_id not in user_ids:
        user_ids.append(message.from_id.user_id)

    offset_id = messages[-1].id

    if len(messages) < limit:
      break
  
  return user_ids

async def get_user_data(user_id: str):
  user: users.UserFull = await client(GetFullUserRequest(user_id))
  data = user.users[0]
  return {
    'Идентификатор': data.id,
    'Никнейм': data.username,
    'Имя': data.first_name,
    'Фамилия': data.last_name,
    'Телефон': data.phone
  }

def make_excel_file(user_data: list[dict]):
  df = pd.DataFrame(user_data)

  excel_file_path = 'list.xlsx'
  df.to_excel(excel_file_path, index=False)

async def get_users_by_channel():
  participants = await client.get_participants(channel)
    
  for participant in participants:
      print(participant.id, participant.username, participant.first_name, participant.last_name)

async def main():
  # await get_users_by_channel()
  user_ids = await get_user_ids()
  
  user_data_list = []
  
  for user_id in user_ids:
    user_data = await get_user_data(user_id)
    print('user data loaded' + str(user_id))

    user_data_list.append(user_data)

  print(user_data_list)
    
  make_excel_file(user_data_list)

with client:
    client.loop.run_until_complete(main())