# main/plugins/pyroplug_manual.py
# Github.com-Vasusen-code

import asyncio, time, os

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
    """手动下载模式下的 get_msg 函数"""
    chat = ""
    round_message = False
    if "?single" in msg_link:
        msg_link = msg_link.split("?single")[0]
    msg_id = int(msg_link.split("/")[-1]) + int(i)
    height, width, duration, thumb_path = 90, 90, 0, None

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
            if msg.media:
                if msg.media == MessageMediaType.WEB_PAGE:
                    print("克隆网页内容：")
                    print(msg.text)
                    return
            if not msg.media:
                if msg.text:
                    print("克隆文本消息：")
                    print(msg.text)
                    return

            print("尝试下载媒体文件...")
            file = await userbot.download_media(msg)
            print(f"文件已下载：{file}")

            caption = msg.caption if msg.caption else ""

            if msg.media == MessageMediaType.PHOTO:
                print("已下载照片。")
                # 在此处添加处理照片的代码，例如保存到特定目录
            elif msg.media == MessageMediaType.VIDEO:
                print("已下载视频。")
                # 在此处添加处理视频的代码
            else:
                print("已下载文件。")
                # 在此处添加处理其他文件的代码

        except Exception as e:
            print(f"下载消息时出错：{e}")
    else:
        print("请输入有效的 t.me 链接。")