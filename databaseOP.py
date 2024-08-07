import sqlite3

# 連接資料庫
conn = sqlite3.connect('telegram.db')
c = conn.cursor()


def create_tables():
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


def close_connection():
    conn.close()


def convert_size(text):
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = 1024
    for i in range(len(units)):
        if (text / size) < 1:
            return "%.2f%s" % (text, units[i])
        text = text / size
    return 0


def insert_message(file):
    # 檢查 name 是否為 None 或空字符串，如果是，則設為空字符串
    name = file.get('name', "") if file.get('name') else ""
    try:
        c.execute('''
            INSERT INTO messages (fid, mid, group_name, type, size, size_text, name, datetime)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            file['fid'],                   # fid
            file['mid'],                   # mid
            file['group'],                 # group_name
            file['type'],                  # type
            file['size'],
            convert_size(file['size']),
            name,                          # name, 若為 None 則設為空字符串
            file['datetime']               # datetime
        ))

        # 提交事務
        conn.commit()
        print("資料插入成功！")
    except sqlite3.IntegrityError:
        print("錯誤：fid 重複，無法插入資料。")
        return True
    except Exception as e:
        print(f"發生錯誤：{e}")
        return False
    return False


def update_message(file):
    try:
        c.execute('''
            UPDATE messages
            SET mid = ?, datetime = ?
            WHERE fid = ? AND group_name = ?
        ''', (
            file['mid'],
            file['datetime'],
            file['fid'],
            file['group']
        ))

        # 提交事務
        conn.commit()
        print("資料更新成功！")
    except Exception as e:
        print(f"發生錯誤：{e}")


def delete_group_data(group_name):
    try:
        if (group_name == "DeleteAllDB"):
            c.execute('DELETE FROM messages')
            conn.commit()
            print(f"群組:{group_name} 的所有資料已刪除。")
        else:
            c.execute('DELETE FROM messages WHERE group_name = ?', (group_name,))
            conn.commit()
            print(f"群組:{group_name} 的所有資料已刪除。")
    except Exception as e:
        print(f"發生錯誤：{e}")


def delete_file(file):
    try:
        c.execute('DELETE FROM messages WHERE fid = ? AND group_name = ?',
                  (file['fid'], file['group']))
        conn.commit()
    except Exception as e:
        print(f"發生錯誤：{e}")


def search_file(file):
    c.execute('SELECT mid FROM messages WHERE fid = ? AND group_name = ?',
              (file['fid'], file['group']))
    result = c.fetchone()
    return result[0] if result else False  # False=沒資料
