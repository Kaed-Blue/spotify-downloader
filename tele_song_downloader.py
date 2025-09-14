from asyncio import events
from telethon import TelegramClient, events, connection
import asyncio
import codecs
import csv
import os
from dotenv import load_dotenv
import pandas

load_dotenv()

api_id = os.getenv("API_ID")    #get your api_id and api_hash from telegram (give it a search)
api_hash = os.getenv("API_HASH")
proxy = (
    os.getenv("PROXY_IP"),
    os.getenv("PROXY_PORT"),
    os.getenv("PROXY_SECRET"),
)
connection_type = connection.ConnectionTcpMTProxyRandomizedIntermediate

client = TelegramClient(
    "Spotify Scraper/Spotify_downloader.session",
    api_id,  # type: ignore
    api_hash,  # type: ignore
    # connection=connection_type,    #uncomment to use MTproto proxy (you should fill the PROXY_IP, PROXY_PORT and PROXY_SECRET in the .env file)
    # proxy=proxy,
)

if not os.path.exists(r"Spotify Scraper\remaning_tracks.csv"):
    try:
        remaining_df = pandas.read_csv("Spotify Scraper/track_table.csv")
        remaining = remaining_df.values.tolist()
    except FileNotFoundError:
        print("make a track_table.csv file using the spotify_scraper")
else:
    remaining_df = pandas.read_csv("Spotify Scraper/remaning_tracks.csv")
    remaining = remaining_df.values.tolist()


counter = 1


async def save_progress(row):
    global counter
    with codecs.open("Spotify Scraper/downloaded.csv", "a", "utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)
    counter += 1

    if counter % 5 == 0:
        remaning_tracks_df = pandas.DataFrame(remaining)
        remaning_tracks_df.to_csv("Spotify Scraper/remaning_tracks.csv", index=False)


flag_value = None
flag_event = asyncio.Event()


@client.on(events.NewMessage(incoming=True, from_users=("@MusicsHuntersbot")))    #if you want you can use other bots as long as they send just a media file in reply
async def handler(event):
    if event.media:
        global flag_value
        path = await event.download_media(file="E:/Music")
        if path:
            print(f"media saved at{path}")
            flag_value = True
        else:
            print("download failed")
            flag_value = False
        flag_event.set()
    else:
        flag_value = False
        flag_event.set()


async def send_url():
    await client.start()  # type: ignore
    n = 0
    global flag_value
    for row in remaining[:]:
        flag_value = False
        while (flag_value == None or flag_value == False) and n < 2:
            song_url = row[2]
            song_name = row[1]
            song_index = row[0]
            flag_event.clear()
            flag_value = False
            await client.send_message("@MusicsHuntersbot", song_url)
            n += 1

            try:
                await asyncio.wait_for(flag_event.wait(), timeout=50)
            except asyncio.TimeoutError:
                print(f"timed out for {song_index}:{song_name}")

            await asyncio.sleep(0.5)    #if your internet is really fast you may want to increase this by a bit so telegram won't get mad

            if flag_value == True:
                print(f"finished downloading {song_index}: {song_name}")
                await save_progress(row)
                remaining.remove(row)
            else:
                print(f"failed downloading {song_index} : {song_name} for {n} times")
        n = 0

    await client.disconnect()  # type: ignore


asyncio.run(send_url())


