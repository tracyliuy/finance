import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# API密钥配置
API_KEYS = {
    'FMP_API_KEY': os.getenv('FMP_API_KEY')  # Financial Modeling Prep API key
}

# 数据库配置
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'finance')
}

# 数据获取器配置
FETCHER_CONFIG = {
    'fmp': {
        'base_url': 'https://financialmodelingprep.com/api/v3',
        'symbol': 'GOLD',  # 黄金现货
        'historical_price': '/historical-price-full/',  # 历史价格端点
        'historical_chart': '/historical-chart/',  # 历史图表端点
        'quote': '/quote/',  # 实时报价端点
        'interval': '1day'  # 数据间隔
    }
} 