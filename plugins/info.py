from pyrogram import Client, filters
import config


@Client.on_message(filters.command("cmd") & filters.me)
async def cmd(client, message):
    cmdinfo = "`/cmd` - 顯示機器人指令 \n`/i` - 回覆訊息或群組顯示簡短資訊 \n`/fi` - 回覆訊息或群組顯示完整資訊 \n`/reload` - 重新紀錄該群組的訊息\n`/reloadall` - 重新紀錄所有群組的訊息"
    await client.edit_message_text(message.chat.id, message.id, cmdinfo)


@Client.on_message(filters.command("pin") & filters.me)
async def pin(client, message):
    print(message.text)
    pinned = await client.pin_chat_message(message.chat.id, message_id=int(message.command[1]), disable_notification=True)
    await pinned.delete(revoke=True)


@Client.on_message(filters.command("fi") & filters.me)
async def fullInfo(client, message):
    # print(message)
    if message.reply_to_message_id:
        await client.edit_message_text(message.chat.id, message.id, str(message.reply_to_message)[:4096])
    else:
        await client.edit_message_text(message.chat.id, message.id, str(message)[:4096])


@Client.on_message(filters.command("i") & filters.me)
async def simpleInfo(client, message):
    if message.reply_to_message_id:
        msg = await client.get_messages(message.chat.id, message.reply_to_message_id)
    else:
        msg = message

    info = {
        "Message ID": msg.id,
        "Chat Title": msg.chat.title if msg.chat else None,
        "Chat ID": msg.chat.id if msg.chat else None,
        "First Name": msg.from_user.first_name if msg.from_user else None,
        "Username": msg.from_user.username if msg.from_user else None,
        "User ID": msg.from_user.id if msg.from_user else None,
        "Photo Unique ID": msg.photo.file_unique_id if msg.photo else None,
        "Document Unique ID": msg.document.file_unique_id if msg.document else None,
        "Video Unique ID": msg.video.file_unique_id if msg.video else None,
        "Message Time": msg.date
    }

    info_text = "\n".join(f"{key}: `{value}`" for key,
                          value in info.items() if value is not None)

    await client.edit_message_text(message.chat.id, message.id, info_text)


@Client.on_message(filters.command("showcfg") & filters.me)
async def show_config(client, message):
    cfg_text = (
        f"⚙️ Current Config Values:\n\n"
        f"`allowSendGrp` = `{config.allowSendGrp}`\n"
        f"`checkSameGrp` = `{config.checkSameGrp}`\n"
        f"`downloadGrp` = `{config.downloadGrp}`\n"
        f"`captions_blacklist` = `{config.captions_blacklist}`\n"
        f"`filenames_blacklist` = `{config.filenames_blacklist}`\n"
        f"`active_profiles` = `{config.active_profiles}`\n"
    )
    # print(cfg_text)
    await client.edit_message_text(message.chat.id, message.id, cfg_text)


@Client.on_message(filters.command("reloadcfg") & filters.me)
async def reload_config_handler(client, message):
    # 重新讀設定
    config.reload_config()

    # print("✅ 設定已重新讀取")

    # 編輯訊息回覆
    await client.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.id,
        text="✅ 重新讀取設定完成"
    )
