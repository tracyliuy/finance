import os
import sys
from pathlib import Path

def setup_project_path():
    """设置项目根目录到Python路径"""
    # 获取当前文件的绝对路径
    current_file = Path(__file__).resolve()
    # 获取项目根目录（当前文件的上两级目录）
    project_root = current_file.parent.parent.parent
    # 将项目根目录添加到Python路径
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    return project_root

# 自动执行路径设置
setup_project_path() 