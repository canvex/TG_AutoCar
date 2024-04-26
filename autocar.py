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


@app.on_message(filters.command("i") & filters.me)
async def info(client: Client, message: Message):
    if message.reply_to_message_id:
        await app.edit_message_text(message.chat.id, message.id, str(message.reply_to_message)[:4096])
    else:
        await app.edit_message_text(message.chat.id, message.id, str(message)[:4096])


@app.on_message(filters.command("save") & filters.me)
async def saveID(client: Client, message: Message):
    # 將列表轉換為字串
    list_str = str(file_list)

    # 開啟文字檔，使用 'w' 模式以覆蓋舊的檔案
    with open('id.txt', 'w') as f:
        # 將整個列表字串寫入檔案
        f.write(list_str)


# ===================================AutoCar===================================

# media_group
processed_media_groups_ids = []
lock = asyncio.Lock()

# 轉傳media_group類型


@app.on_message((filters.media_group) & filters.chat(allowSendGrp))
async def handle(client: Client, message: Message):
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
    # if (message.chat.id in allowSendGrp):
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
    file = await get_file_information(msg)
    if file is None:  # doesn't have media
        return False, file
    if file['fid'] in file_list[msg.chat.id]:  # have duplicate
        return True, file
    file_list[msg.chat.id].append(file['fid'])  # no duplicate

    return False, file


@app.on_message((filters.media) & filters.chat(checkSameGrp), group=2)
async def delMsg(client: Client, message: Message):
    try:
        msg = await app.get_messages(message.chat.id, message.id)
    except Exception as e:
        logger.error(type(e.__class__, e))
        return

    text = color.PURPLE + "[ Delete ] "  # 將整個文字加上紫色顯示
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 取得當前時間
    is_duplicate, file = await check_duplicate_file(msg)
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

        await app.delete_messages(msg.chat.id, msg.id)
        # await delOldMsg(msg)


async def init():
    async with app:
        bar = tqdm(checkSameGrp)
        try:
            for i in bar:
                chat = await app.get_chat(i)
                file_list[chat.id] = []  # 初始化每個群組檔案列表
                total = 0  # 統計處理訊息數量
                delete = 0  # 統計刪除訊息數量
            # for i in checkSameGrp:
                async for msg in app.search_messages(i):
                    # 讀取群組訊息(由舊到新)
                    is_duplicate, _ = await check_duplicate_file(msg)
                    if is_duplicate:
                        print('群組:{}, 重複檔案進行刪除[{}]'.format(msg.chat.title, msg.id))
                        # 刪除訊息
                        # await delOldMsg(msg)
                        await app.delete_messages(msg.chat.id, msg.id)
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
# app.run()

# print("Enter Yes to start the APP:")
# if (input().lower() == "yes"):
#     print("Initialize checking for duplicate files...")
#     app.run(init())
# else:
#     print("Exit")
