import asyncio
import time
import os

from .. import userbot  # 引入已经初始化的 userbot

from pyrogram.enums import MessageMediaType

from main.plugins.helpers import screenshot

async def get_numeric_chat_id(client, chat_identifier):
    try:
        if str(chat_identifier).lstrip('-').isdigit():
            return int(chat_identifier)
        else:
            chat = await client.get_chat(chat_identifier)
            chat_id = chat.id
            return chat_id
    except Exception as e:
        print(f"获取 {chat_identifier} 的数字 ID 时出错：{e}")
        return None

async def get_msg(msg_link, i=0):
    chat = ""
    if "?single" in msg_link:
        msg_link = msg_link.split("?single")[0]
    msg_id = int(msg_link.split("/")[-1]) + int(i)

    if 't.me/' in msg_link:
        parts = msg_link.split('/')
        if 't.me/c/' in msg_link:
            chat_identifier = '-100' + parts[-2]
        else:
            chat_identifier = parts[-2]

        chat = await get_numeric_chat_id(userbot, chat_identifier)
        if not chat:
            print(f"无法获取 {chat_identifier} 的数字 ID")
            return

        try:
            msg = await userbot.get_messages(chat, msg_id)
            if msg.media_group_id:
                # 获取同一媒体组的所有消息
                media_group = await userbot.get_media_group(chat, msg_id)
                print(f"发现媒体组，共有 {len(media_group)} 条消息。")

                for media_msg in media_group:
                    # 下载每条消息的媒体
                    await download_media_message(media_msg)
            else:
                # 单条消息处理
                await download_media_message(msg)

        except Exception as e:
            print(f"下载消息时出错：{e}")
    else:
        print("请输入有效的 t.me 链接。")

async def download_media_message(msg):
    if msg.media:
        print(f"尝试下载媒体文件，消息 ID：{msg.id}")
        file = await userbot.download_media(msg)
        print(f"文件已下载：{file}")

        caption = msg.caption if msg.caption else ""
        print(caption)

        if msg.media == MessageMediaType.PHOTO:
            print("已下载照片。")
            # 在此处添加处理照片的代码
        elif msg.media == MessageMediaType.VIDEO:
            print("已下载视频。")
            # 在此处添加处理视频的代码
        else:
            print("已下载文件。")
            # 在此处添加处理其他文件的代码
    else:
        if msg.text:
            print("文本消息：")
            print(msg.text)