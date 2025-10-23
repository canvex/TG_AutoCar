import logging
import configparser

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename='logfile.log')
logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')


def get_list(section, key):
    return [item.strip() for item in config.get(section, key).split(',') if item.strip()]


def load_config():
    """讀取設定檔並回傳字典形式"""
    global captions_blacklist, filenames_blacklist
    global allowSendGrp, checkSameGrp, downloadGrp
    global api_id, api_hash

    captions_blacklist = get_list('blacklist', 'captions')
    filenames_blacklist = get_list('blacklist', 'files')
    allowSendGrp = [int(x) for x in get_list('groups', 'allowSendGrp')]
    checkSameGrp = [int(x) for x in get_list('groups', 'checkSameGrp')]
    downloadGrp = [int(x) for x in get_list('groups', 'downloadGrp')]

    api_id = config.get('api', 'api_id', fallback='')
    api_hash = config.get('api', 'api_hash', fallback='')
    if not api_id or not api_hash:
        api_id = config.get('public_apis', 'default_api_id')
        api_hash = config.get('public_apis', 'default_api_hash')

    logger.info("✅ Config reloaded successfully.")


def reload_config():
    """重新讀取設定檔"""
    config.read('config.ini', encoding='utf-8')
    load_config()


# 初始讀取
load_config()

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
