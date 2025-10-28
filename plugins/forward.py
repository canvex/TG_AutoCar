import asyncio
import time
from pyrogram import Client, filters
import databaseOP as db_ops
from pyrogram.errors import FloodWait
from plugins.delete import delMsg
from collections import deque

import config

# media_group
lock = asyncio.Lock()

# 最大保留 50 組黑名單 group_id
MAX_GROUPS = 50

# 使用 deque 限制長度
blacklisted_media_groups_ids = deque(maxlen=MAX_GROUPS)
processed_media_groups_ids = set()


def find_blacklisted_word(text, blacklist):
    for word in blacklist:
        if word in text:
            return word
    return None

# --------------------------
# 轉傳 media_group 類型
# --------------------------


@Client.on_message((filters.media_group))
async def quicksend_group(client, message):
    if message.chat.id not in config.allowSendGrp:
        return
    if not message.media_group_id:
        return

    group_id = str(message.media_group_id)

    # 如果整組已被黑名單擋掉
    if group_id in blacklisted_media_groups_ids:
        return

    # 檢查 caption 黑名單
    if message.caption:
        detected_word = find_blacklisted_word(
            message.caption, config.captions_blacklist)
        if detected_word:
            print(config.color.RED +
                  f"標題包含黑名單中的單字 '{detected_word}' 已忽略該媒體群組。" + config.color.END)
            blacklisted_media_groups_ids.append(group_id)
            return

    # 檢查檔案名稱黑名單
    if message.document:
        detected_word = find_blacklisted_word(
            message.document.file_name, config.filenames_blacklist)
        if detected_word:
            print(config.color.RED +
                  f"檔案名稱 {message.document.file_name} 偵測黑名單單字「{detected_word}」，已忽略該媒體群組。" + config.color.END)
            blacklisted_media_groups_ids.append(group_id)
            return

    try:
        async with lock:
            if group_id in processed_media_groups_ids:
                return
            processed_media_groups_ids.add(group_id)

        print(config.color.CYAN +
              f"[Received] Time: {message.date}, Group: {message.chat.title}, Type: media_group" + config.color.END)

        # 轉傳相簿，遍歷多設定集
        source_id = message.chat.id
        for profile in config.active_profiles:
            mapping = profile.get(source_id)
            if mapping:
                target_group = mapping["target"]
                topic_id = mapping["topic"]
                try:
                    result = await client.copy_media_group(chat_id=target_group, from_chat_id=source_id, message_id=message.id, message_thread_id=topic_id)
                    for m in result:
                        await delMsg(client, m)
                    print(
                        f"[轉傳] {message.chat.title} → {target_group} topic {topic_id}")
                except Exception as e:
                    print(f"[錯誤] 轉傳失敗: {e}")

        processed_media_groups_ids.remove(group_id)

    except Exception as e:
        config.logger.error(f"{type(e).__name__}: {e}")


# --------------------------
# 轉傳單一檔案
# --------------------------
@Client.on_message(((filters.photo | filters.document | filters.video) & ~filters.media_group), group=1)
async def quicksend(client, message):
    if message.chat.id not in config.allowSendGrp:
        return
    # 黑名單檢查
    if message.caption:
        detected_word = find_blacklisted_word(
            message.caption, config.captions_blacklist)
        if detected_word:
            print(config.color.RED +
                  f"標題包含黑名單中的單字 '{detected_word}' 已忽略該訊息。" + config.color.END)
            return

    if message.document:
        detected_word = find_blacklisted_word(
            message.document.file_name, config.filenames_blacklist)
        if detected_word:
            print(config.color.RED +
                  f"檔案名稱 {message.document.file_name} 偵測黑名單中 '{detected_word}' 已忽略該訊息。" + config.color.END)
            return

    # 判斷檔案類型
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
    # 多設定集轉傳
    source_id = message.chat.id
    for profile in config.active_profiles:
        mapping = profile.get(source_id)
        if mapping:
            target_group = mapping["target"]
            topic_id = mapping["topic"]
            try:
                result = await message.copy(chat_id=target_group, message_thread_id=topic_id)
                await delMsg(client, result)
                print(
                    f"[轉傳] {message.chat.title} → {target_group} topic {topic_id}")
            except Exception as e:
                print(f"[錯誤] 轉傳失敗: {e}")


# --------------------------
# 下載檔案
# --------------------------
@Client.on_message((filters.media) & filters.chat(config.downloadGrp))
async def download(client, message):
    for dlgrp in config.downloadGrp:
        if message.sender_chat.id == dlgrp:
            start = time.time()

            async def progress(current, total):
                print(f"{current * 100 / total:.2f}%")

            if message.document is not None:
                await client.send_message("me", f"爆大剛剛分享了 `{message.document.file_name}` ")

            await client.download_media(message)
            end = time.time()
            usetime = end - start
            print(f"下載共耗時{usetime:.2f}秒")
