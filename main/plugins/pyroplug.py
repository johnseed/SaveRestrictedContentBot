#Github.com-Vasusen-code

import asyncio, time, os

from .. import bot as Drone
from main.plugins.progress import progress_for_pyrogram
from main.plugins.helpers import screenshot

from pyrogram import Client, filters
from pyrogram.errors import ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid, PeerIdInvalid
from pyrogram.enums import MessageMediaType
from ethon.pyfunc import video_metadata
from ethon.telefunc import fast_upload
from telethon.tl.types import DocumentAttributeVideo
from telethon import events

def thumbnail(sender):
    if os.path.exists(f'{sender}.jpg'):
        return f'{sender}.jpg'
    else:
        return None

# 添加获取数字 ID 的函数
async def get_numeric_chat_id(client, chat_identifier):
    try:
        if str(chat_identifier).lstrip('-').isdigit():
            # 如果 chat_identifier 已经是数字 ID，直接返回
            return int(chat_identifier)
        else:
            # 否则，通过 get_chat 获取数字 ID
            chat = await client.get_chat(chat_identifier)
            chat_id = chat.id
            return chat_id
    except Exception as e:
        print(f"Error getting numeric ID for {chat_identifier}: {e}")
        return None

async def get_msg(userbot, client, bot, sender, edit_id, msg_link, i):
    
    """ userbot: PyrogramUserBot
    client: PyrogramBotClient
    bot: TelethonBotClient """
    
    edit = ""
    chat = ""
    round_message = False
    if "?single" in msg_link:
        msg_link = msg_link.split("?single")[0]
    msg_id = int(msg_link.split("/")[-1]) + int(i)
    height, width, duration, thumb_path = 90, 90, 0, None

    if 't.me/' in msg_link:
        # 提取 chat_identifier
        parts = msg_link.split('/')
        if 't.me/c/' in msg_link:
            # 对于 't.me/c/' 链接，添加 '-100' 前缀
            chat_identifier = '-100' + parts[-2]
        else:
            chat_identifier = parts[-2]

        # 获取数字 ID
        chat = await get_numeric_chat_id(userbot, chat_identifier)
        if not chat:
            await client.edit_message_text(sender, edit_id, f"无法获取 {chat_identifier} 的数字 ID")
            return

        try:
            msg = await userbot.get_messages(chat, msg_id)
            if msg.media:
                if msg.media == MessageMediaType.WEB_PAGE:
                    edit = await client.edit_message_text(sender, edit_id, "Cloning.")
                    await client.send_message(sender, msg.text.markdown)
                    await edit.delete()
                    return
            if not msg.media:
                if msg.text:
                    edit = await client.edit_message_text(sender, edit_id, "Cloning.")
                    await client.send_message(sender, msg.text.markdown)
                    await edit.delete()
                    return
            edit = await client.edit_message_text(sender, edit_id, "Trying to Download.")
            file = await userbot.download_media(
                msg,
                progress=progress_for_pyrogram,
                progress_args=(
                    client,
                    "**DOWNLOADING:**\n",
                    edit,
                    time.time()
                )
            )
            print(file)
            await edit.edit('Preparing to Upload!')
            caption = None
            upload_video = False  # Video file too big
            if msg.caption is not None:
                caption = msg.caption
            if msg.media == MessageMediaType.VIDEO_NOTE:
                round_message = True
                print("Trying to get metadata")
                data = video_metadata(file)
                height, width, duration = data["height"], data["width"], data["duration"]
                print(f'd: {duration}, w: {width}, h:{height}')
                try:
                    thumb_path = await screenshot(file, duration, sender)
                except Exception:
                    thumb_path = None
                if upload_video:
                    await client.send_video_note(
                        chat_id=sender,
                        video_note=file,
                        length=height, duration=duration, 
                        thumb=thumb_path,
                        progress=progress_for_pyrogram,
                        progress_args=(
                            client,
                            '**UPLOADING:**\n',
                            edit,
                            time.time()
                        )
                    )
                else:
                    await bot.send_file(sender, thumb_path, caption=caption)
                    print('download complete : ' + file)
                    os.remove(thumb_path)
            elif msg.media == MessageMediaType.VIDEO and msg.video.mime_type in ["video/mp4", "video/x-matroska", "video/quicktime"]:
                print("Trying to get metadata")
                data = video_metadata(file)
                height, width, duration = data["height"], data["width"], data["duration"]
                print(f'd: {duration}, w: {width}, h:{height}')
                try:
                    thumb_path = await screenshot(file, duration, sender)
                except Exception:
                    thumb_path = None
                if upload_video:
                    await client.send_video(
                        chat_id=sender,
                        video=file,
                        caption=caption,
                        supports_streaming=True,
                        height=height, width=width, duration=duration, 
                        thumb=thumb_path,
                        progress=progress_for_pyrogram,
                        progress_args=(
                            client,
                            '**UPLOADING:**\n',
                            edit,
                            time.time()
                        )
                    )
                else:
                    await bot.send_file(sender, thumb_path, caption=caption)
                    print('download complete : ' + file)
                    os.remove(thumb_path)
            elif msg.media == MessageMediaType.PHOTO:
                await edit.edit("Uploading photo.")
                await bot.send_file(sender, file, caption=caption)
            else:
                thumb_path = thumbnail(sender)
                await client.send_document(
                    sender,
                    file,
                    caption=caption,
                    thumb=thumb_path,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        client,
                        '**UPLOADING:**\n',
                        edit,
                        time.time()
                    )
                )

            delete_after = False
            try:
                if delete_after:
                    os.remove(file)
                    if os.path.isfile(file):
                        os.remove(file)
            except Exception:
                pass
            await edit.delete()
        except (ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid):
            await client.edit_message_text(sender, edit_id, "Have you joined the channel?")
            return
        except PeerIdInvalid:
            chat_identifier = msg_link.split("/")[-3]
            # 获取数字 ID
            chat = await get_numeric_chat_id(userbot, chat_identifier)
            if not chat:
                await client.edit_message_text(sender, edit_id, f"无法获取 {chat_identifier} 的数字 ID")
                return
            return await get_msg(userbot, client, bot, sender, edit_id, msg_link, i)
        except Exception as e:
            print(e)
            if "messages.SendMedia" in str(e) \
            or "SaveBigFilePartRequest" in str(e) \
            or "SendMediaRequest" in str(e) \
            or str(e) == "File size equals to 0 B":
                try:
                    if msg.media == MessageMediaType.VIDEO and msg.video.mime_type in ["video/mp4", "video/x-matroska"]:
                        UT = time.time()
                        uploader = await fast_upload(f'{file}', f'{file}', UT, bot, edit, '**UPLOADING:**')
                        attributes = [DocumentAttributeVideo(duration=duration, w=width, h=height, round_message=round_message, supports_streaming=True)]
                        await bot.send_file(sender, uploader, caption=caption, thumb=thumb_path, attributes=attributes, force_document=False)
                    elif msg.media == MessageMediaType.VIDEO_NOTE:
                        uploader = await fast_upload(f'{file}', f'{file}', UT, bot, edit, '**UPLOADING:**')
                        attributes = [DocumentAttributeVideo(duration=duration, w=width, h=height, round_message=round_message, supports_streaming=True)]
                        await bot.send_file(sender, uploader, caption=caption, thumb=thumb_path, attributes=attributes, force_document=False)
                    else:
                        UT = time.time()
                        uploader = await fast_upload(f'{file}', f'{file}', UT, bot, edit, '**UPLOADING:**')
                        await bot.send_file(sender, uploader, caption=caption, thumb=thumb_path, force_document=True)
                    if os.path.isfile(file):
                        os.remove(file)
                except Exception as e:
                    print(e)
                    await client.edit_message_text(sender, edit_id, f'Failed to save: `{msg_link}`\n\nError: {str(e)}')
                    try:
                        os.remove(file)
                    except Exception:
                        return
                    return
            else:
                await client.edit_message_text(sender, edit_id, f'Failed to save: `{msg_link}`\n\nError: {str(e)}')
                try:
                    os.remove(file)
                except Exception:
                    return
                return
        
        # duplicate ?
        # try:
        #     os.remove(file)
        #     if os.path.isfile(file) == True:
        #         os.remove(file)
        # except Exception:
        #     pass
        # await edit.delete()
    else:
        # 原有处理逻辑
        edit = await client.edit_message_text(sender, edit_id, "Cloning.")
        chat_identifier = msg_link.split("t.me")[1].split("/")[1]
        # 获取数字 ID
        chat = await get_numeric_chat_id(userbot, chat_identifier)
        if not chat:
            await client.edit_message_text(sender, edit_id, f"无法获取 {chat_identifier} 的数字 ID")
            return
        try:
            msg = await client.get_messages(chat, msg_id)
            if msg.empty:
                new_link = f't.me/b/{chat}/{int(msg_id)}'
                #recurrsion 
                return await get_msg(userbot, client, bot, sender, edit_id, new_link, i)
            await client.copy_message(sender, chat, msg_id)
        except Exception as e:
            print(e)
            return await client.edit_message_text(sender, edit_id, f'Failed to save: `{msg_link}`\n\nError: {str(e)}')
        await edit.delete()
            
async def get_bulk_msg(userbot, client, sender, msg_link, i):
    x = await client.send_message(sender, "Processing!")
    await get_msg(userbot, client, Drone, sender, x.id, msg_link, i)