from pyrogram import Client, filters, idle
from pyrogram.types import Message
from datetime import datetime
from pyrogram.errors import FloodWait
import asyncio
import asyncio.subprocess
import logging
from tqdm import tqdm
from pyrogram.enums import MessageMediaType, MessagesFilter
from datetime import datetime


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
api_id = 'YourID'
api_hash = 'YourHash'

app = Client(
    "my_forPC",
    api_id=api_id,
    api_hash=api_hash,
    app_version="OnPC 1.2.1",
    device_model="AutoCar",
    system_version="Windows 11 Pro"
)
# =======================  自己用  =======================


# =======================  Test Server用  =======================
# 公用API
# api_id = 21724
# api_hash = "3e0cb5efcd52300aec5994fdfc5bdc16"

# app = Client(
#     "my_account_test",
#     api_id=api_id,
#     api_hash=api_hash,
#     device_model="Test",
#     test_mode=True,
#     system_version="Windows 11 Pro"
# )
# =======================  Test Server用  =======================


TestServer = [-4004465584, -4069257192]  # 測試伺服器 AAA,BBB

allowSendGrp = ["自行加入"]  # 允許轉發群組
checkSameGrp = ["自行加入"]  # 偵測重複檔案群組
captions_blacklist = ["自行加入"]


@app.on_message(filters.command("save") & filters.me)
async def saveID(client: Client, message: Message):
    # 將列表轉換為字串
    list_str = str(file_list)

    # 開啟文字檔，使用 'w' 模式以覆蓋舊的檔案
    with open('id.txt', 'w') as f:
        # 將整個列表字串寫入檔案
        f.write(list_str)


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
        "Video Unique ID": msg.video.file_unique_id if msg.video else None
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
                    'datetime': photo.date.astimezone().strftime("%Y/%m/%d %H:%M:%S")
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
                    'datetime': document.date.astimezone().strftime("%Y/%m/%d %H:%M:%S")
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
                    'datetime': video.date.astimezone().strftime("%Y/%m/%d %H:%M:%S")
                }
        except:
            print("發生錯誤")
            print(msg)
            return None

    return file

# 檢查是否有存在相同檔案id


async def check_duplicate_file(msg):
    removeID = None  # 暫存重複的 mid

    file = await get_file_information(msg)
    if file is None:  # doesn't have media
        return False, file, -1
    if file['fid'] in [x[1] for x in file_list[msg.chat.id]]:  # 如果 fid 在 file_list 中已經存在（即有重複）
        # 檢查 file 的 fid 是否存在於 file_list 中，同時將重複的 mid 放入 removeID
        for f_id, f_unique_id in file_list[msg.chat.id]:
            if f_unique_id == file['fid']:
                removeID = f_id
                break
        # 將與重複的 fid 相對應的 mid 存入 removeID 中後，將重複的 fid 從 file_list 中刪除
        file_list[msg.chat.id] = [(f_id, f_unique_id) for f_id,
                                  f_unique_id in file_list[msg.chat.id] if f_unique_id != file['fid']]
        # 將新的 (mid, fid) 加入 file_list
        file_list[msg.chat.id].append((file['mid'], file['fid']))
        return True, file, removeID
    # 如果 fid 在 file_list 中不存在（即沒有重複）
    file_list[msg.chat.id].append((file['mid'], file['fid']))
    # 回傳 False 代表沒有處理重複的 fid，並回傳 file
    return False, file, -1


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
        bar = tqdm(checkSameGrp)
        try:
            for i in bar:
                chat = await app.get_chat(i)
                file_list[chat.id] = []  # 初始化每個群組檔案列表
                total = 0  # 統計處理訊息數量
                delete = 0  # 統計刪除訊息數量
                async for msg in app.search_messages(i):
                    # 讀取群組訊息(由舊到新)
                    is_duplicate, _, removeID = await check_duplicate_file(msg)
                    if is_duplicate:
                        print('群組:{}, 重複檔案進行刪除[{}]'.format(msg.chat.title, removeID))
                        # 刪除訊息
                        await app.delete_messages(msg.chat.id, removeID)
                        delete += 1
                    total += 1
                    bar.set_description('群組:{} 初始化檢查重複檔案, 檢查數量:{}, 刪除:{}'.format(
                        msg.chat.title, total, delete))
        except FloodWait as e:
            print(color.RED + "Wait {} seconds before continuing".format(e.value)+color.END)
            logger.error(type(e.__class__, e))
            await asyncio.sleep(e.value)  # Wait "value" seconds before continuing
        except Exception as e:
            logger.error(type(e.__class__, e))
            return

        print("Start listening for new messages:")
        await idle()
        return False

print("Initialize checking for duplicate files...")
app.run(init())
