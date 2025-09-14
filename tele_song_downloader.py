from asyncio import events
from telethon import TelegramClient, events, connection
import asyncio
import codecs
import csv
import os

# import aioconsole
from websocket import send
import pandas


api_id = 20303224
api_hash = "70222f96855ca468a9640ee0feea612c"
proxy = (
    "91.238.92.45",
    8443,
    "EERighJJvXrFGRMCIMJdCQ",
)
connection_type = connection.ConnectionTcpMTProxyRandomizedIntermediate

client = TelegramClient(
    r"Python\Spotify Scraper\Spotify_downloader.session",
    api_id,
    api_hash,
    # connection=connection_type,
    # proxy=proxy,
)

if not os.path.exists(r"Python\Spotify Scraper\remaning_tracks.csv"):
    remaining_df = pandas.read_csv("Python/Spotify Scraper/track_table.csv")
    remaining = remaining_df.values.tolist()
    # remaining = list(csv.reader(f))
else:
    remaining_df = pandas.read_csv("Python/Spotify Scraper/remaning_tracks.csv")
    remaining = remaining_df.values.tolist()


counter = 1


async def save_progress(row):
    global counter
    with codecs.open("Python/Spotify Scraper/downloaded.csv", "a", "utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)
    counter += 1

    if counter % 5 == 0:
        remaning_tracks_df = pandas.DataFrame(remaining)
        remaning_tracks_df.to_csv(
            "Python/Spotify Scraper/remaning_tracks.csv", index=False
        )
        # downloaded_df = pandas.DataFrame(downloaded)
        # downloaded_df.to_csv("Python/Spotify Scraper/downloaded.csv", index=False)


# async def input_listener():
#     global running
#     while True:
#         command = await aioconsole.ainput()
#         if command.strip().lower() == "stop":
#             running = False
#             await save_progress()


flag_value = None
flag_event = asyncio.Event()


@client.on(events.NewMessage(incoming=True, from_users=("@MusicsHuntersbot")))
async def handler(event):
    if event.media:
        global flag_value
        # flag_value = None
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


# downloaded = []


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

            await asyncio.sleep(0.5)

            if flag_value == True:
                print(f"finished downloading {song_index}: {song_name}")
                # downloaded.append(row)
                await save_progress(row)
                remaining.remove(row)
            else:
                print(f"failed downloading {song_index} : {song_name} for {n} times")
        n = 0

    await client.disconnect()  # type: ignore


# async def main():
#     await asyncio.gather(send_url(), input_listener())


# asyncio.run(main())
asyncio.run(send_url())
# asyncio.run(handler(event))


# @MusicsHuntersbot
