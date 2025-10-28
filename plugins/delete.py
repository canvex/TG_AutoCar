import messageInfo
from datetime import datetime
from pyrogram import Client, filters
import databaseOP as db_ops
import config


# 新訊息來檢查
@Client.on_message((filters.media), group=2)
async def delMsg(client, message):
    if message.chat.id not in config.checkSameGrp:
        return
    try:
        msg = await client.get_messages(message.chat.id, message.id)
    except Exception as e:
        config.logger.error(type(e.__class__, e))
        return

    text = config.color.PURPLE + "[ Delete ] "  # 將整個文字加上紫色顯示
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 取得當前時間
    is_duplicate, file, removeID = await messageInfo.check_duplicate_file(msg)
    if is_duplicate:
        text += "Time: {} ".format(current_time)
        text += ",Group: {} ".format(file['group'])
        if 'type' in file:
            text += ",Type: {} ".format(file['type'])
        if 'name' in file:
            text += ",File Name: {} ".format(file['name'])
        text += ",Size: {}".format(db_ops.convert_size(file['size']))
        if 'w' in file and 'h' in file:
            text += " ,Resolution: {}x{}".format(file['w'], file['h'])
        print(text + config.color.END)

        await client.delete_messages(msg.chat.id, removeID)


async def delDirect(client, message, file, removeID):  # reload用
    text = config.color.PURPLE + "[ Delete ] "  # 將整個文字加上紫色顯示
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 取得當前時間
    text += "Time: {} ".format(current_time)
    text += ",Group: {} ".format(file['group'])
    if 'type' in file:
        text += ",Type: {} ".format(file['type'])
    if 'name' in file:
        text += ",File Name: {} ".format(file['name'])
    text += ",Size: {}".format(db_ops.convert_size(file['size']))
    if 'w' in file and 'h' in file:
        text += " ,Resolution: {}x{}".format(file['w'], file['h'])
    print(text + config.color.END)
    await client.delete_messages(message.chat.id, removeID)
