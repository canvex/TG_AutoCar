from pyrogram import Client, idle
import platform
from config import api_id, api_hash
import databaseOP as db_ops

sysos = platform.system()
app_version = "1.7"  # 程式版本
plugins = dict(root="plugins")
# 呼叫 db_ops 來創建資料表
db_ops.create_tables()


# 注意 plugins 參數使用的是相對路徑，並通過 get_path 函數設置
app = Client(
    "my_account",
    api_id=api_id,
    api_hash=api_hash,
    app_version=f"{sysos} {app_version}",
    device_model="AutoCar",
    plugins=plugins)


async def hellome():
    async with app:
        # Send a message, Markdown is enabled by default
        me = await app.get_me()
        print(f"歡迎 {me.first_name}({me.username}) 使用🥳🥳🥳\n")
        await idle()
app.run(hellome())
