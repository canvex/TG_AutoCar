from pyrogram import Client, filters
import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
}


def search_fc2(id):
    # 使用正則表達式檢查是否有符合的7位數字
    matchID = re.findall(r'\b\d{7}\b', str(id))  # 確保 id 是字符串型態
    if not matchID:  # 如果沒有找到符合的番號
        # print("此段文字沒有FC2番號")
        return "此段文字沒有FC2番號"

    try:
        result = ""
        url = 'https://fc2ppvdb.com/articles/' + matchID[0]
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 檢查是否成功回應

        response.encoding = response.apparent_encoding  # 自動偵測編碼

        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(response.text, 'lxml')

        # 提取作品名
        title = soup.find(
            'h2', class_='items-center text-white text-lg title-font font-medium mb-1').find('a').text

        # 提取其他資訊，並檢查是否存在
        id_ = soup.find('span', class_='text-white ml-2').text if soup.find(
            'span', class_='text-white ml-2') else "找不到"

        # 提取販売者資訊
        seller_element = soup.find(
            'a', class_='font-medium text-blue-600 dark:text-blue-500 hover:underline')
        seller = seller_element.text if seller_element else "找不到"
        seller_url = seller_element['href'] if seller_element else "找不到"

        # 提取女優資訊
        actress_span = soup.find_all('span', class_='text-white ml-2')[2] if len(
            soup.find_all('span', class_='text-white ml-2')) > 2 else None
        actress = actress_span.text.strip(
        ) if actress_span and actress_span.text.strip() else "找不到"
        actress_url = actress_span.find(
            'a')['href'] if actress_span and actress_span.find('a') else "找不到"

        # 提取其他資訊（例如 Mosaic, Sale date, Duration）
        mosaic = soup.find_all('span', class_='text-white ml-2')[3].text if len(
            soup.find_all('span', class_='text-white ml-2')) > 3 else "找不到"
        sale_date = soup.find_all('span', class_='text-white ml-2')[4].text if len(
            soup.find_all('span', class_='text-white ml-2')) > 4 else "找不到"
        duration = soup.find_all('span', class_='text-white ml-2')[5].text if len(
            soup.find_all('span', class_='text-white ml-2')) > 5 else "找不到"

        # 構建 result 字符串
        result += f"作品名：{title}\nID：FC2PPV-`{id_}`\n販売者：[{seller}](https://fc2ppvdb.com{seller_url})\n"
        # print(f"作品名：{title}")
        # print(f"ID：FC2PPV-{id_}")
        # print(f"販売者：{seller}")
        # print(f"販売者網址：https://fc2ppvdb.com{seller_url}")

        # 女優網址處理
        # print(f"女優：{actress}")
        if actress_url == "找不到":
            result += "女優：找不到\n"
            # print("女優網址：找不到")
        else:
            result += f"女優：[{actress}](https://fc2ppvdb.com{actress_url})\n"
            # print(f"女優網址：https://fc2ppvdb.com{actress_url}")

        # 其他資訊
        result += f"有碼無碼：{mosaic}\n販売日：{sale_date}\n収録時間：{duration}"
        # print(f"有碼無碼：{mosaic}")
        # print(f"販売日：{sale_date}")
        # print(f"収録時間：{duration}")

        return result

    except requests.exceptions.RequestException as e:
        # print(f"請求失敗: {e}")
        return f"請求失敗: {e}"


@Client.on_message(filters.command("fc2", ",") & filters.me)
async def fc2(client, message):
    # 檢查 message.command 是否有第二個參數，且參數不為空
    if len(message.command) > 1 and message.command[1]:
        text = message.command[1]
    else:
        text = message.reply_to_message.text
    await client.edit_message_text(message.chat.id, message.id, "搜尋中請稍等...")
    # await message.reply_text(search_fc2(str(text)), reply_to_message_id=message.reply_to_message_id, quote=True)
    await client.edit_message_text(message.chat.id, message.id, search_fc2(str(text)))
