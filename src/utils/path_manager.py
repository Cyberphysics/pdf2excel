#!/usr/bin/env python3
"""
路径管理器模块 - 统一管理项目中的所有路径引用
符合业界标准的目录结构：src/为源代码，数据存储目录与src同级
"""
import os
import logging
from typing import Optional, Dict, List
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class PathConfig:
    """路径配置数据类"""
    project_root: str
    uploads_dir: str
    outputs_dir: str
    data_dir: str
    logs_dir: str
    config_dir: str
    
    @classmethod
    def from_project_root(cls, root: str) -> 'PathConfig':
        """从项目根目录创建路径配置"""
        return cls(
            project_root=root,
            uploads_dir=os.path.join(root, 'uploads'),
            outputs_dir=os.path.join(root, 'outputs'),
            data_dir=os.path.join(root, 'data'),
            logs_dir=os.path.join(root, 'logs'),
            config_dir=os.path.join(root, 'config')
        )

class PathManager:
    """统一的路径管理器"""
    
    def __init__(self, project_root: Optional[str] = None):
        """
        初始化路径管理器
        
        Args:
            project_root: 项目根目录，如果为None则自动检测
        """
        self.project_root = project_root or self._detect_project_root()
        self.config = PathConfig.from_project_root(self.project_root)
        
        logger.info(f"PathManager initialized with project root: {self.project_root}")
    
    def _detect_project_root(self) -> str:
        """
        自动检测项目根目录
        
        检测策略：
        1. 查找包含src目录的父目录
        2. 查找包含requirements.txt或setup.py的目录
        3. 查找包含.git目录的目录
        4. 使用当前工作目录作为后备选项
        
        Returns:
            项目根目录的绝对路径
        """
        # 从当前文件位置开始向上查找
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # 项目根目录的标识文件/目录
        root_markers = ['src', 'requirements.txt', 'setup.py', '.git', 'pyproject.toml']
        
        # 向上查找项目根目录
        search_dir = current_dir
        while search_dir != os.path.dirname(search_dir):  # 直到到达文件系统根目录
            # 检查是否包含任何根目录标识
            if any(os.path.exists(os.path.join(search_dir, marker)) for marker in root_markers):
                logger.info(f"Project root detected: {search_dir}")
                return search_dir
            search_dir = os.path.dirname(search_dir)
        
        # 如果没有找到，使用当前工作目录
        fallback_root = os.getcwd()
        logger.warning(f"Could not detect project root, using current directory: {fallback_root}")
        return fallback_root
    
    def ensure_directories(self) -> Dict[str, bool]:
        """
        确保所有必要目录存在
        
        Returns:
            字典，键为目录名，值为是否成功创建
        """
        results = {}
        directories = {
            'uploads': self.config.uploads_dir,
            'outputs': self.config.outputs_dir,
            'data': self.config.data_dir,
            'logs': self.config.logs_dir,
            'config': self.config.config_dir
        }
        
        for name, directory in directories.items():
            try:
                os.makedirs(directory, exist_ok=True)
                # 验证目录是否可写
                if os.access(directory, os.W_OK):
                    results[name] = True
                    logger.info(f"Directory ensured: {directory}")
                else:
                    results[name] = False
                    logger.error(f"Directory not writable: {directory}")
            except Exception as e:
                results[name] = False
                logger.error(f"Failed to create directory {directory}: {e}")
        
        return results
    
    def get_upload_path(self, filename: str) -> str:
        """
        获取上传文件的完整路径
        
        Args:
            filename: 文件名
            
        Returns:
            上传文件的完整路径
        """
        return os.path.join(self.config.uploads_dir, filename)
    
    def get_output_path(self, filename: str) -> str:
        """
        获取输出文件的完整路径
        
        Args:
            filename: 文件名
            
        Returns:
            输出文件的完整路径
        """
        return os.path.join(self.config.outputs_dir, filename)
    
    def get_database_path(self, db_name: str = 'database.db') -> str:
        """
        获取数据库文件路径
        
        Args:
            db_name: 数据库文件名
            
        Returns:
            数据库文件的完整路径
        """
        return os.path.join(self.config.data_dir, db_name)
    
    def get_log_path(self, log_name: str) -> str:
        """
        获取日志文件路径
        
        Args:
            log_name: 日志文件名
            
        Returns:
            日志文件的完整路径
        """
        return os.path.join(self.config.logs_dir, log_name)
    
    def get_config_path(self, config_name: str) -> str:
        """
        获取配置文件路径
        
        Args:
            config_name: 配置文件名
            
        Returns:
            配置文件的完整路径
        """
        return os.path.join(self.config.config_dir, config_name)
    
    def validate_paths(self) -> Dict[str, Dict[str, bool]]:
        """
        验证所有路径的状态
        
        Returns:
            验证结果字典，包含每个目录的存在性和权限信息
        """
        validation_results = {}
        directories = {
            'project_root': self.config.project_root,
            'uploads': self.config.uploads_dir,
            'outputs': self.config.outputs_dir,
            'data': self.config.data_dir,
            'logs': self.config.logs_dir,
            'config': self.config.config_dir
        }
        
        for name, directory in directories.items():
            validation_results[name] = {
                'exists': os.path.exists(directory),
                'is_directory': os.path.isdir(directory),
                'readable': os.access(directory, os.R_OK) if os.path.exists(directory) else False,
                'writable': os.access(directory, os.W_OK) if os.path.exists(directory) else False,
                'path': directory
            }
        
        return validation_results
    
    def get_relative_path(self, absolute_path: str) -> str:
        """
        将绝对路径转换为相对于项目根目录的路径
        
        Args:
            absolute_path: 绝对路径
            
        Returns:
            相对于项目根目录的路径
        """
        try:
            return os.path.relpath(absolute_path, self.config.project_root)
        except ValueError:
            # 如果路径不在同一个驱动器上（Windows），返回绝对路径
            return absolute_path
    
    def normalize_path(self, path: str) -> str:
        """
        规范化路径，处理路径分隔符和相对路径
        
        Args:
            path: 原始路径
            
        Returns:
            规范化后的路径
        """
        # 如果是相对路径，基于项目根目录解析
        if not os.path.isabs(path):
            path = os.path.join(self.config.project_root, path)
        
        # 规范化路径
        return os.path.normpath(path)
    
    def list_files(self, directory_type: str, pattern: str = '*') -> List[str]:
        """
        列出指定目录中的文件
        
        Args:
            directory_type: 目录类型 ('uploads', 'outputs', 'data', 'logs', 'config')
            pattern: 文件匹配模式
            
        Returns:
            文件列表
        """
        directory_map = {
            'uploads': self.config.uploads_dir,
            'outputs': self.config.outputs_dir,
            'data': self.config.data_dir,
            'logs': self.config.logs_dir,
            'config': self.config.config_dir
        }
        
        if directory_type not in directory_map:
            raise ValueError(f"Unknown directory type: {directory_type}")
        
        directory = directory_map[directory_type]
        if not os.path.exists(directory):
            return []
        
        try:
            from glob import glob
            pattern_path = os.path.join(directory, pattern)
            files = glob(pattern_path)
            # 只返回文件，不包括目录
            return [f for f in files if os.path.isfile(f)]
        except Exception as e:
            logger.error(f"Error listing files in {directory}: {e}")
            return []
    
    def cleanup_old_files(self, directory_type: str, max_age_days: int = 7) -> int:
        """
        清理指定目录中的旧文件
        
        Args:
            directory_type: 目录类型
            max_age_days: 文件最大保留天数
            
        Returns:
            清理的文件数量
        """
        import time
        
        files = self.list_files(directory_type)
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        cleaned_count = 0
        
        for file_path in files:
            try:
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > max_age_seconds:
                    os.remove(file_path)
                    cleaned_count += 1
                    logger.info(f"Cleaned old file: {file_path}")
            except Exception as e:
                logger.error(f"Error cleaning file {file_path}: {e}")
        
        return cleaned_count
    
    def get_directory_size(self, directory_type: str) -> int:
        """
        获取指定目录的总大小（字节）
        
        Args:
            directory_type: 目录类型
            
        Returns:
            目录大小（字节）
        """
        directory_map = {
            'uploads': self.config.uploads_dir,
            'outputs': self.config.outputs_dir,
            'data': self.config.data_dir,
            'logs': self.config.logs_dir,
            'config': self.config.config_dir
        }
        
        if directory_type not in directory_map:
            raise ValueError(f"Unknown directory type: {directory_type}")
        
        directory = directory_map[directory_type]
        if not os.path.exists(directory):
            return 0
        
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
        except Exception as e:
            logger.error(f"Error calculating directory size for {directory}: {e}")
        
        return total_size

# 全局路径管理器实例
_path_manager_instance = None

def get_path_manager() -> PathManager:
    """
    获取全局路径管理器实例（单例模式）
    
    Returns:
        PathManager实例
    """
    global _path_manager_instance
    if _path_manager_instance is None:
        _path_manager_instance = PathManager()
        # 确保目录存在
        _path_manager_instance.ensure_directories()
    return _path_manager_instance

def reset_path_manager():
    """重置全局路径管理器实例（主要用于测试）"""
    global _path_manager_instance
    _path_manager_instance = None