import logging
import configparser

# -------------------
# Logging 設定
# -------------------
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='logfile.log'
)
logger = logging.getLogger(__name__)

# -------------------
# ConfigParser
# -------------------
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

# -------------------
# 讀取逗號分隔清單
# -------------------


def get_list(section, key):
    return [item.strip() for item in config.get(section, key).split(',') if item.strip()]


# -------------------
# 全域變數
# -------------------
captions_blacklist = []
filenames_blacklist = []
allowSendGrp = []
checkSameGrp = []
downloadGrp = []
api_id = ''
api_hash = ''
active_profiles = []  # 轉傳設定集

# -------------------
# 讀 forward_maps 並還原 allowSendGrp / checkSameGrp
# -------------------


def load_forward_maps():
    global active_profiles, allowSendGrp, checkSameGrp
    active_profiles = []
    allowSendGrp = set()
    checkSameGrp = set()

    for section in config.sections():
        if section.startswith("forward_maps_"):
            profile = {}
            for key, value in config.items(section):
                source_id = int(key)
                target_id, topic_id = map(int, value.split(":"))
                profile[source_id] = {"target": target_id, "topic": topic_id}
                allowSendGrp.add(source_id)
                checkSameGrp.add(target_id)
            active_profiles.append(profile)

    # 轉回 list 方便程式使用
    allowSendGrp = list(allowSendGrp)
    checkSameGrp = list(checkSameGrp)

# -------------------
# 讀取其他設定
# -------------------


def load_config():
    global captions_blacklist, filenames_blacklist
    global downloadGrp, api_id, api_hash

    captions_blacklist = get_list('blacklist', 'captions')
    filenames_blacklist = get_list('blacklist', 'files')
    downloadGrp = [int(x) for x in get_list('groups', 'downloadGrp')]

    api_id = config.get('api', 'api_id', fallback='')
    api_hash = config.get('api', 'api_hash', fallback='')
    if not api_id or not api_hash:
        api_id = config.get('public_apis', 'default_api_id')
        api_hash = config.get('public_apis', 'default_api_hash')

    logger.info("✅ Config reloaded successfully.")

# -------------------
# 重新讀取設定
# -------------------


def reload_config():
    global active_profiles, allowSendGrp, checkSameGrp

    # 清空舊設定
    config.clear()
    config.read('config.ini', encoding='utf-8')

    # 讀其他設定
    load_config()

    # 讀 forward_maps 並重建 active_profiles
    active_profiles = []
    allowSendGrp = set()
    checkSameGrp = set()
    for section in config.sections():
        if section.startswith("forward_maps_"):
            profile = {}
            for key, value in config.items(section):
                source_id = int(key)
                target_id, topic_id = map(int, value.split(":"))
                profile[source_id] = {"target": target_id, "topic": topic_id}
                allowSendGrp.add(source_id)
                checkSameGrp.add(target_id)
            active_profiles.append(profile)

    # 轉回 list
    allowSendGrp = list(allowSendGrp)
    checkSameGrp = list(checkSameGrp)

    logger.info("✅ Config reloaded successfully.")


# -------------------
# 初始讀取
# -------------------
load_config()
load_forward_maps()

# -------------------
# 顏色設定
# -------------------


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
