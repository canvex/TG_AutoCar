from pyrogram import Client
import platform
from config import api_id, api_hash
import databaseOP as db_ops

sysos = platform.system()
app_version = "1.5"  # 程式版本
plugins = dict(root="plugins")
# 呼叫 db_ops 來創建資料表
db_ops.create_tables()

print("Start...")
Client(
    "my_account",
    api_id=api_id,
    api_hash=api_hash,
    app_version=f"{sysos} {app_version}",
    device_model="AutoCar",
    plugins=plugins).run()
