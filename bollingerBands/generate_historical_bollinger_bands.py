"""
生成历史布林带数据
"""

from datetime import datetime
from .models import BollingerBandsData
import logging
import os

# 确保logs目录存在
os.makedirs('logs', exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bollinger_bands.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('BollingerBandsGenerator')

def main():
    # 创建数据模型实例
    data_model = BollingerBandsData()
    
    # 设置时间范围（例如：从1980年到2024年）
    start_date = datetime(1980, 1, 1).date()
    end_date = datetime.now().date()
    
    # 处理历史数据
    data_model.process_historical_data(start_date, end_date)

if __name__ == "__main__":
    main() 