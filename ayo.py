from telethon import TelegramClient, events
import re
import asyncio
import os

api_id = '26732439'
api_hash = '6d54f9ccd284f540fcb5f2267866b970'
bot_token = '7134573214:AAGm2WeHbjz3HmKj5NxHBDFpqxSCkV1GROo'
phone_number = '306995127907'  # Your phone number with country code


client = TelegramClient('bot', api_id, api_hash)

async def export_and_clean(channel_username):
    channel = await client.get_entity(channel_username)
    messages = await client.get_messages(channel, limit=None)
    
    combo = f"{channel.title}.txt".replace('/', '_')
    with open(combo, 'w', encoding='utf-8') as f:
        for message in messages:
            if message.message:
                f.write(f'{message.date} - {message.sender_id}: {message.message}\n')

    with open(combo, 'r', encoding='utf-8') as file:
        input_text = file.read()
    
    matches = re.findall(r'\b(\d{14,16})\|(\d{1,2})[\|/](\d{2,4})\|(\d{3,4})\b', input_text)

    cleaned_cc = []
    for match in matches:
        cc, mm, year, cvv = match
        mm = mm.zfill(2)
        if len(year) == 2:
            year = '20' + year
        cleaned_cc.append(f"{cc}|{mm}|{year}|{cvv}")

    output = f"{combo.split('.')[0]}_cleaned.txt"
    with open(output, 'w') as file:
        for cc in cleaned_cc:
            file.write(cc + '\n')

    return output

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond('Welcome to the Telegram Export Bot!\nPlease send the channel username you want to export messages from (e.g., @example_channel).')
    raise events.StopPropagation

@client.on(events.NewMessage)
async def handle_username(event):
    channel_username = event.message.text.strip()
    await event.respond(f'Processing channel: {channel_username}...')
    
    try:
        cleaned_file = await export_and_clean(channel_username)
        await client.send_file(event.chat_id, cleaned_file, caption='Here is the cleaned file.')
        await event.respond('Please send the next channel username you want to export messages from, or type /stop to end.')
        os.remove(cleaned_file)
        
    except Exception as e:
        await event.respond(f"An error occurred: {e}")

@client.on(events.NewMessage(pattern='/stop'))
async def stop(event):
    await event.respond('Thank you for using the bot. Goodbye!')
    raise events.StopPropagation

async def main():
    await client.start()
    
    try:
        await client.run_until_disconnected()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
