import requests
import pandas as pd
from datetime import datetime, timedelta
import logging
import os

# 确保logs目录存在
os.makedirs('logs', exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/fmp_fetcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('FMPFetcher') 