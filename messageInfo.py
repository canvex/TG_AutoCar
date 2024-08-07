import databaseOP as db_ops
from pyrogram.enums import MessageMediaType


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

    dupe = db_ops.search_file(file)
    if (dupe and (dupe != file['mid'])):  # message id is different
        removeID = dupe
        db_ops.update_message(file)  # update new message id
        return True, file, removeID
    else:
        db_ops.insert_message(file)
        return False, file, -1
