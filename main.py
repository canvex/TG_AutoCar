import asyncio
import platform
from pyrogram import Client, idle, enums
import config
import databaseOP as db_ops

# 系統資訊
sysos = platform.system() + " " + platform.release()
app_version = "1.8"
plugins = dict(root="plugins")

# 資料庫初始化
db_ops.create_tables()


async def hellome():
    async with Client(
        "my_account",
        api_id=config.api_id,
        api_hash=config.api_hash,
        device_model="AutoCarBot",          # 自訂你的設備名稱
        system_version=sysos,               # 系統版本
        app_version=app_version,            # 程式版本
        lang_pack="desktop",                # 語言包
        lang_code="en",                     # 語言代碼
        client_platform=enums.ClientPlatform.DESKTOP,
        plugins=plugins
    ) as app:
        me = await app.get_me()
        print(f"歡迎 {me.first_name}({me.username}) 使用🥳🥳🥳\n")
        await idle()

if __name__ == "__main__":

    asyncio.run(hellome())
