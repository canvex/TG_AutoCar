import asyncio
import time
from pyrogram import Client, filters
import databaseOP as db_ops
from pyrogram.errors import FloodWait
from plugins.delete import delMsg

import config

def find_blacklisted_word(text, blacklist):
    for word in blacklist:
        if word in text:
            return word
    return None


# media_group
processed_media_groups_ids = []
lock = asyncio.Lock()

# 轉傳media_group類型


@Client.on_message((filters.media_group) & filters.chat(config.allowSendGrp))
async def handle(client, message):
   # 檢查標題
    if message.caption:
        detected_word = find_blacklisted_word(
            message.caption, config.captions_blacklist)
        if detected_word:
            detected_word = config.color.RED + detected_word + config.color.END
            print(f"標題包含黑名單中的單字 '{detected_word}' 已忽略該訊息。")
            return

    # 檢查檔案名稱
    if message.document:
        detected_word = find_blacklisted_word(
            message.document.file_name, config.filenames_blacklist)
        if detected_word:
            detected_word = config.color.RED + detected_word + config.color.END
            print(
                f"檔案名稱 {message.document.file_name} 偵測黑名單中 '{detected_word}' 已忽略該訊息。")
            return
    try:
        async with lock:
            if message.media_group_id in processed_media_groups_ids:
                return
            processed_media_groups_ids.append(message.media_group_id)

        print(config.color.CYAN + "[Received] Time:", message.date, ",Group:",
              message.chat.title, ",Type: media_group" + config.color.END)
        for group in config.checkSameGrp:
            result = await client.copy_media_group(chat_id=group, from_chat_id=message.chat.id, message_id=message.id)
            for times in result:
                await delMsg(client, times)
        processed_media_groups_ids.clear()
    except Exception as e:
        config.logger.error(type(e.__class__, e))
        return


# 轉傳單一檔案


@Client.on_message(((filters.photo | filters.document | filters.video) & ~filters.media_group) & filters.chat(config.allowSendGrp), group=1)
async def quicksend(client, message):
    # 檢查標題
    if message.caption:
        detected_word = find_blacklisted_word(
            message.caption, config.captions_blacklist)
        if detected_word:
            detected_word = config.color.RED + detected_word + config.color.END
            print(f"標題包含黑名單中的單字 '{detected_word}' 已忽略該訊息。")
            return

    # 檢查檔案名稱
    if message.document:
        detected_word = find_blacklisted_word(
            message.document.file_name, config.filenames_blacklist)
        if detected_word:
            detected_word = config.color.RED + detected_word + config.color.END
            print(
                f"檔案名稱 {message.document.file_name} 偵測黑名單中 '{detected_word}' 已忽略該訊息。")
            return
    try:
        file_type = message.media.value
        if (file_type == "photo"):
            print(config.color.CYAN + "[Received] Time:", message.date, ",Group:",
                  message.chat.title, ",Type:", file_type, ",Size:", db_ops.convert_size(message.photo.file_size) + config.color.END)
        if (file_type == "document"):
            print(config.color.CYAN + "[Received] Time:", message.date, ",Group:", message.chat.title, ",Type:", message.document.mime_type,
                  ",File Name:", message.document.file_name, ",Size:", db_ops.convert_size(message.document.file_size) + config.color.END)
        if (file_type == "video"):
            print(config.color.CYAN + "[Received] Time:", message.date, ",Group:", message.chat.title, ",Type:", message.video.mime_type,
                  ",File Name:", message.video.file_name, ",Size:", db_ops.convert_size(message.video.file_size) + config.color.END)
        for group in config.checkSameGrp:
            result = await message.copy(group)
            await delMsg(client, result)
    except FloodWait as e:
        print(config.color.RED + "Wait {} seconds before continuing".format(e.value)+config.color.END)
        config.logger.error(type(e.__class__, e))
        await asyncio.sleep(e.value)  # Wait "value" seconds before continuing
    except Exception as e:
        config.logger.error(type(e.__class__, e))
        return


@Client.on_message((filters.media) & filters.chat(config.downloadGrp))
async def download(client, message):
    for dlgrp in config.downloadGrp:
        if message.sender_chat.id == dlgrp:
            start = time.time()
            # Keep track of the progress while downloading

            async def progress(current, total):
                print(f"{current * 100 / total:.2f}%")
            # await client.download_media(message, progress=progress)
            if message.document is not None:
                await client.send_message("me", f"爆大剛剛分享了 `{message.document.file_name}` ")
            await client.download_media(message)
            end = time.time()
            usetime = end - start
            print(f"下載共耗時{usetime:.2f}秒")


# @Client.on_message(filters.command("reloadcfg") & filters.me)
# async def reload_handler(client, message):
#     reload_config()
#     await message.reply("✅ 設定已重新讀取！")


@Client.on_message(filters.command("showcfg2") & filters.me)
async def fullInfo(client, message):
    await client.edit_message_text(message.chat.id, message.id, str(config.captions_blacklist))
