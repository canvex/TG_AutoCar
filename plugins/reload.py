from pyrogram import Client, filters
import time
from pyrogram.errors import FloodWait
import databaseOP as db_ops
import asyncio
import messageInfo
import shutil
from .delete import delDirect
from config import logger, checkSameGrp


@Client.on_message(filters.command("reload") & filters.me)
async def reload(client, message):
    if (message.chat.id in checkSameGrp):
        start_time = time.time()  # 記錄開始時間
        await client.edit_message_text(message.chat.id, message.id, f"重新紀錄 {message.chat.title} 檔案...")
        db_ops.delete_group_data(message.chat.title)
        try:
            total = 0  # count message
            async for msg in client.search_messages(message.chat.id):
                result = await messageInfo.check_duplicate_file(msg)
                if result[2] > 0:  # 資料庫有找到舊資料
                    await delDirect(client, message, result[1], result[2])
                total += 1
                print(f'群組:{msg.chat.title} 開始紀錄檔案, 檢查數量:{total}')
        except FloodWait as e:
            print(f"等待 {e.value} 秒後繼續")
            logger.error(f"FloodWait: {e}")
            await asyncio.sleep(e.value)  # 等待 "value" 秒後繼續
        except Exception as e:
            logger.error(f"{type(e).__name__}: {e}")
        end_time = time.time()  # 記錄結束時間
        elapsed_time = end_time - start_time  # 計算耗費時間
        await client.edit_message_text(message.chat.id, message.id, f"群組 {message.chat.title} 重整完成✅\n耗費時間: {elapsed_time:.2f} 秒")
        print(f"群組 {message.chat.title} 重整完成✅ 耗費時間: {elapsed_time:.2f} 秒")
    else:
        await client.edit_message_text(message.chat.id, message.id, "該群組不在檢查群組內")


@Client.on_message(filters.command("reloadall") & filters.me)
async def reloadall(client, message):
    src = 'telegram.db'
    dst = 'telegram.db.bak'
    shutil.copyfile(src, dst)  # 刪除前先備份
    db_ops.delete_group_data("DeleteAllDB")
    num = 0
    start_time = time.time()  # 記錄開始時間
    try:
        for group in checkSameGrp:
            num += 1
            total = 0  # 統計處理訊息數量
            await client.edit_message_text(message.chat.id, message.id, f"重新紀錄第{num}個群組{group}資料")
            async for msg in client.search_messages(group):
                result = await messageInfo.check_duplicate_file(msg)
                if result[2] > 0:  # 資料庫有找到舊資料
                    await delDirect(client, message, result[1], result[2])
                total += 1
                print(f'群組:{group} 開始紀錄檔案, 檢查數量:{total}')
    except FloodWait as e:
        print(f"等待 {e.value} 秒後繼續")
        logger.error(f"FloodWait: {e}")
        await asyncio.sleep(e.value)  # 等待 "value" 秒後繼續
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
    end_time = time.time()  # 記錄結束時間
    elapsed_time = end_time - start_time  # 計算耗費時間
    await client.edit_message_text(message.chat.id, message.id, f"全部群組重整完成✅\n耗費時間: {elapsed_time:.2f} 秒")
    print(f"全部群組重整完成✅\n耗費時間: {elapsed_time:.2f} 秒")
