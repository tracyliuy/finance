import logging
import os

def setup_logger(name, log_file=None):
    """
    设置日志配置
    
    Args:
        name (str): 日志记录器名称
        log_file (str, optional): 日志文件路径，如果为None则只输出到控制台
    
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 确保logs目录存在
    os.makedirs('logs', exist_ok=True)
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 如果指定了日志文件，添加文件处理器
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger 