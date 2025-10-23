# config.py
import logging
import configparser

# 設置日誌
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename='logfile.log')
logger = logging.getLogger(__name__)

# 讀取 INI 檔案，指定編碼為 'utf-8'
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

# 讀取配置項


def get_list(section, key):
    return [item.strip() for item in config.get(section, key).split(',')]


captions_blacklist = get_list('blacklist', 'captions')
filenames_blacklist = get_list('blacklist', 'files')
allowSendGrp = [int(item.strip()) for item in get_list('groups', 'allowSendGrp')]
checkSameGrp = [int(item.strip()) for item in get_list('groups', 'checkSameGrp')]
downloadGrp = [int(item.strip()) for item in get_list('groups', 'downloadGrp')]

# 獲取 API 配置
api_id = config.get('api', 'api_id', fallback='')
api_hash = config.get('api', 'api_hash', fallback='')
# 如果 api 部分的值為空，則使用 public_apis 部分的值
if not api_id or not api_hash:
    api_id = config.get('public_apis', 'default_api_id')
    api_hash = config.get('public_apis', 'default_api_hash')


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
