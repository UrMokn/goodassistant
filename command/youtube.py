import discord
import feedparser
import asyncio
import json
import os
import config

SERVER_NOTICE_ROLE_ID = config.SERVER_NOTICE_ROLE_ID
POSTED_LINKS_FILE = config.POSTED_LINKS_FILE
YOUTUBE_NOTICE_CHANNEL_ID = config.YOUTUBE_NOTICE_CHANNEL_ID
YOUTUBE_CHANNEL_ID = config.YOUTUBE_CHANNEL_ID
YOUTUBE_CHECK_INTERVAL = config.YOUTUBE_CHECK_INTERVAL

def load_posted_links():
    if os.path.exists(POSTED_LINKS_FILE):
        with open(POSTED_LINKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_posted_links(links):
    with open(POSTED_LINKS_FILE, "w", encoding="utf-8") as f:
        json.dump(links, f, indent=4)

async def check_youtube(client):
    await client.wait_until_ready()
    channel = client.get_channel(YOUTUBE_NOTICE_CHANNEL_ID)

    if channel is None:
        print("指定したチャンネルが見つかりません")
        return

    posted_links = load_posted_links()

    while not client.is_closed():
        feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={YOUTUBE_CHANNEL_ID}"
        feed = feedparser.parse(feed_url)

        for entry in reversed(feed.entries):
            link = entry.link

            if link not in posted_links:
                is_community_post = any(tag["term"] == "yt:community" for tag in entry.get("tags", []))

                if is_community_post:
                    message = f"<@&{SERVER_NOTICE_ROLE_ID}> ぐっど様がが投稿を投稿しました \n{link}"
                else:
                    message = f"<@&{SERVER_NOTICE_ROLE_ID}> ぐっど様がが動画を投稿しました \n{link}"

                await channel.send(message)

                posted_links.append(link)
                save_posted_links(posted_links)

        await asyncio.sleep(YOUTUBE_CHECK_INTERVAL)
