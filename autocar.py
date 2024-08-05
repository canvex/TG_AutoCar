import platform
import sqlite3
from pyrogram.enums import MessageMediaType, MessagesFilter
import logging
import asyncio.subprocess
import asyncio
from pyrogram.errors import FloodWait
from datetime import datetime
from pyrogram.types import Message
from pyrogram import Client, filters, idle
import configparser

# 連接到 SQLite 資料庫，如果資料庫檔案不存在，會自動創建
conn = sqlite3.connect('messages.db')
c = conn.cursor()

# 創建資料表，將 fid 設為主鍵
c.execute('''
    CREATE TABLE IF NOT EXISTS messages (
    fid TEXT NOT NULL,
    group_name TEXT NOT NULL,
    mid INTEGER,
    name TEXT,
    type TEXT,
    size_text TEXT,
    size INTEGER,
    datetime TEXT,
    PRIMARY KEY (group_name, fid)
    )
''')
conn.commit()

sysos = platform.system()
app_version = "1.3"  # 程式版本

config = configparser.ConfigParser()
# 讀取 INI 檔案，指定編碼為 'utf-8'
with open('config.ini', encoding='utf-8') as f:
    config.read_file(f)

captions_blacklist_string = config.get('blacklist', 'captions')
captions_blacklist = [item.strip() for item in captions_blacklist_string.split(',')]

allowSendGrp_string = config.get('groups', 'allowSendGrp')
allowSendGrp = [int(item.strip()) for item in allowSendGrp_string.split(',')]

checkSameGrp_string = config.get('groups', 'checkSameGrp')
checkSameGrp = [int(item.strip()) for item in checkSameGrp_string.split(',')]
api_id = config.get('api', 'api_id', fallback=None)
api_hash = config.get('api', 'api_hash', fallback=None)

# 如果 api 部分的值為空，則使用 public_apis 部分的值
if not api_id or not api_hash:
    api_id = config.get('public_apis', 'default_api_id')
    api_hash = config.get('public_apis', 'default_api_hash')


class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename='logfile.log')
logger = logging.getLogger(__name__)
queue = asyncio.Queue()

file_list = {}  # 紀錄檔案id


# =======================  自己用  =======================
app = Client(
    "my_account",
    api_id=api_id,
    api_hash=api_hash,
    app_version=f"{sysos} {app_version}",
    device_model="AutoCar"
)
# =======================  自己用  =======================


# ===================  Test Server 用  ===================
# 公用APIs
# api_id = 21724
# api_hash = "3e0cb5efcd52300aec5994fdfc5bdc16"

# app = Client(
#     "my_account_test",
#     api_id=api_id,
#     api_hash=api_hash,
#     device_model="Test",
#     test_mode=True
# )
# ===================  Test Server 用  ===================


@app.on_message(filters.command("cmd") & filters.me)
async def cmd(client: Client, message: Message):
    cmdinfo = "`/cmd` - 顯示機器人指令 \n`/i` - 回覆訊息或群組顯示簡短資訊 \n`/fi` - 回覆訊息或群組顯示完整資訊 \n`/reload` - 重新紀錄該群組的訊息\n`/reloadall` - 重新紀錄所有群組的訊息"
    await app.edit_message_text(message.chat.id, message.id, cmdinfo)


@app.on_message(filters.command("reload") & filters.me)
async def reload(client: Client, message: Message):
    if (message.chat.id in checkSameGrp):
        await app.edit_message_text(message.chat.id, message.id, f"重新紀錄 {message.chat.title} 資料...")
        try:
            total = 0  # 統計處理訊息數量
            async for msg in app.search_messages(message.chat.id):
                await check_duplicate_file(msg)
                total += 1
                print(f'群組:{msg.chat.title} 開始紀錄檔案, 檢查數量:{total}')
        except FloodWait as e:
            print(f"等待 {e.value} 秒後繼續")
            logger.error(f"FloodWait: {e}")
            await asyncio.sleep(e.value)  # 等待 "value" 秒後繼續
        except Exception as e:
            logger.error(f"{type(e).__name__}: {e}")
        await app.edit_message_text(message.chat.id, message.id, f"群組 {message.chat.title} 重整完成✅")
        print(f"群組 {message.chat.title} 重整完成✅")
    else:
        await app.edit_message_text(message.chat.id, message.id, "該群組不在檢查群組內")


@app.on_message(filters.command("reloadall") & filters.me)
async def reloadall(client: Client, message: Message):
    num = 0
    try:
        for group in checkSameGrp:
            num += 1
            total = 0  # 統計處理訊息數量
            await app.edit_message_text(message.chat.id, message.id, f"重新紀錄第{num}個群組{group}資料")
            async for msg in app.search_messages(group):
                await check_duplicate_file(msg)
                total += 1
                print(f'群組: {group} 開始紀錄檔案, 檢查數量:{total}')

    except FloodWait as e:
        print(f"等待 {e.value} 秒後繼續")
        logger.error(f"FloodWait: {e}")
        await asyncio.sleep(e.value)  # 等待 "value" 秒後繼續
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
    await app.edit_message_text(message.chat.id, message.id, f"全部群組重整完成✅")
    print(f"全部群組重整完成✅")


@app.on_message(filters.command("fi") & filters.me)
async def fullInfo(client: Client, message: Message):
    if message.reply_to_message_id:
        await app.edit_message_text(message.chat.id, message.id, str(message.reply_to_message)[:4096])
    else:
        await app.edit_message_text(message.chat.id, message.id, str(message)[:4096])


@app.on_message(filters.command("i") & filters.me)
async def simpleInfo(client: Client, message: Message):
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

    info_text = "\n".join(f"{key}: `{value}`" for key, value in info.items() if value is not None)

    await app.edit_message_text(message.chat.id, message.id, info_text)

# ===================================AutoCar===================================


# media_group
processed_media_groups_ids = []
lock = asyncio.Lock()

# 轉傳media_group類型


@app.on_message((filters.media_group) & filters.chat(allowSendGrp))
async def handle(client: Client, message: Message):
    if (message.caption and not any(word in message.caption for word in captions_blacklist)) or (not message.caption):
        try:
            async with lock:
                if message.media_group_id in processed_media_groups_ids:
                    return
                processed_media_groups_ids.append(message.media_group_id)

            print(color.CYAN + "[Received] Time:", message.date, ",Group:",
                  message.chat.title, ",Type: media_group" + color.END)
            for group in checkSameGrp:
                result = await app.copy_media_group(chat_id=group, from_chat_id=message.chat.id, message_id=message.id)
                for times in result:
                    await delMsg(client, times)

            processed_media_groups_ids.clear()
        except Exception as e:
            logger.error(type(e.__class__, e))
            return


# 轉傳單一檔案


@app.on_message(((filters.photo | filters.document | filters.video) & ~filters.media_group) & filters.chat(allowSendGrp), group=1)
async def quicksend(client, message):
    if (message.caption and not any(word in message.caption for word in captions_blacklist)) or (not message.caption):
        try:
            file_type = message.media.value
            if (file_type == "photo"):
                print(color.CYAN + "[Received] Time:", message.date, ",Group:",
                      message.chat.title, ",Type:", file_type, ",Size:", convert_size(message.photo.file_size) + color.END)
            if (file_type == "document"):
                print(color.CYAN + "[Received] Time:", message.date, ",Group:", message.chat.title, ",Type:", message.document.mime_type,
                      ",File Name:", message.document.file_name, ",Size:", convert_size(message.document.file_size) + color.END)
            if (file_type == "video"):
                print(color.CYAN + "[Received] Time:", message.date, ",Group:", message.chat.title, ",Type:", message.video.mime_type,
                      ",File Name:", message.video.file_name, ",Size:", convert_size(message.video.file_size) + color.END)
            for group in checkSameGrp:
                result = await message.copy(group)
                await delMsg(client, result)
        except FloodWait as e:
            print(color.RED + "Wait {} seconds before continuing".format(e.value)+color.END)
            logger.error(type(e.__class__, e))
            await asyncio.sleep(e.value)  # Wait "value" seconds before continuing
        except Exception as e:
            logger.error(type(e.__class__, e))
            return


# ===================================DelSameFile===================================


# 計算檔案大小
def convert_size(text):
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = 1024
    for i in range(len(units)):
        if (text / size) < 1:
            return "%.2f%s" % (text, units[i])
        text = text / size
    return 0

# 取得檔案資訊


async def get_file_information(msg):
    file = None
    if msg.media is not None:
        try:
            if msg.media is MessageMediaType.PHOTO:  # 圖片
                photo = msg.photo
                file = {
                    'mid': msg.id,
                    'group': msg.chat.title,
                    'fid': photo.file_unique_id,
                    'type': 'photo',
                    'w': photo.width,
                    'h': photo.height,
                    'size': photo.file_size,
                    'datetime': msg.date.astimezone().strftime("%Y/%m/%d %H:%M:%S")
                }
            elif msg.media is MessageMediaType.DOCUMENT:  # 檔案
                document = msg.document
                file = {
                    'mid': msg.id,
                    'group': msg.chat.title,
                    'fid': document.file_unique_id,
                    'type': document.mime_type,  # 檔案類型
                    'size': document.file_size,  # 檔案尺寸
                    'name': document.file_name,
                    'datetime': msg.date.astimezone().strftime("%Y/%m/%d %H:%M:%S")
                }
            elif msg.media is MessageMediaType.VIDEO:  # 影片
                video = msg.video
                file = {
                    'mid': msg.id,
                    'group': msg.chat.title,
                    'fid': video.file_unique_id,
                    'type': video.mime_type,
                    'w': video.width,
                    'h': video.height,
                    'size': video.file_size,
                    'name': video.file_name,
                    'datetime': msg.date.astimezone().strftime("%Y/%m/%d %H:%M:%S")
                }
        except:
            print("發生錯誤")
            print(msg)
            return None

    return file

# 檢查是否有存在相同檔案id


async def check_duplicate_file(msg):

    file = await get_file_information(msg)
    if file is None:  # doesn't have media
        return False, file, -1

    dupe = search_file(file)
    if (dupe):
        if (dupe != file['mid']):  # 訊息ID不一樣才更新
            removeID = dupe
            update_message(file)
            return True, file, removeID

    else:
        insert_message(file)
        return False, file, -1


def insert_message(file):
    # 檢查 name 是否為 None 或空字符串，如果是，則設為空字符串
    name = file.get('name', "") if file.get('name') else ""
    try:
        c.execute('''
            INSERT INTO messages (fid, mid, group_name, type,size, size_text, name, datetime)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            file['fid'],                   # fid
            file['mid'],                   # mid
            file['group'],                 # group_name
            file['type'],                 # type
            file['size'],
            convert_size(file['size']),    # size
            name,                        # name, 若為 None 則設為空字符串
            file['datetime']              # datetime
        ))

        # 提交事務
        conn.commit()
        print("資料插入成功！")
        return 0
    except sqlite3.IntegrityError:
        print("錯誤：fid 重複，無法插入資料。")
        return 1
    except Exception as e:
        print(f"發生錯誤：{e}")


def search_file(file):
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()

    try:
        # 查詢資料庫中是否存在指定的 group_name 和 fid
        c.execute('''
            SELECT mid FROM messages WHERE group_name = ? AND fid = ?
        ''', (file['group'], file['fid']))
        result = c.fetchone()
        if result:
            return result[0]
        else:
            return 0

    except sqlite3.Error as e:
        print(f"發生錯誤：{e}")

    finally:
        conn.close()


def update_message(file):
    try:
        c.execute('''
            UPDATE messages
            SET mid = ?, datetime = ?
            WHERE fid = ? and group_name= ?
        ''', (
            file['mid'],
            file['datetime'],
            file['fid'],
            file['group']
        ))

        conn.commit()
        print("資料更新成功！")
        return 0
    except Exception as e:
        print(f"發生錯誤：{e}")
        return 1


def delete_group_data(group_name):
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    try:
        if (group_name == "all"):
            c.execute('''
            DELETE FROM messages 
            ''')
            conn.commit()
            print(f"所有群組的所有資料已刪除。")
        else:
            c.execute('''
                DELETE FROM messages WHERE group_name = ?
            ''', (group_name,))
            conn.commit()
            print(f"群組 '{group_name}' 的所有資料已刪除。")

    except sqlite3.Error as e:
        print(f"發生錯誤：{e}")

    finally:
        conn.close()


@app.on_message((filters.media) & filters.chat(checkSameGrp), group=2)
async def delMsg(client: Client, message: Message):
    try:
        msg = await app.get_messages(message.chat.id, message.id)
    except Exception as e:
        logger.error(type(e.__class__, e))
        return

    text = color.PURPLE + "[ Delete ] "  # 將整個文字加上紫色顯示
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 取得當前時間
    is_duplicate, file, removeID = await check_duplicate_file(msg)
    if is_duplicate:
        text += "Time: {} ".format(current_time)
        text += ",Group: {} ".format(file['group'])
        if 'type' in file:
            text += ",Type: {} ".format(file['type'])
        if 'name' in file:
            text += ",File Name: {} ".format(file['name'])
        text += ",Size: {}".format(convert_size(file['size']))
        if 'w' in file and 'h' in file:
            text += " ,Resolution: {}x{}".format(file['w'], file['h'])
        print(text + color.END)

        await app.delete_messages(msg.chat.id, removeID)


async def init():
    async with app:
        print("Start listening for new messages:")
        await idle()
        return False

app.run(init())
