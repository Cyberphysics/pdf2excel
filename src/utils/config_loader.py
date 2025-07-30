"""
配置加载器模块
负责加载和管理系统配置
"""

import os
import json
from flask import current_app

class ConfigLoader:
    """配置加载器类"""
    
    @staticmethod
    def get_config_path(config_name):
        """
        获取配置文件路径
        
        Args:
            config_name: 配置文件名（不含扩展名）
            
        Returns:
            str: 配置文件的完整路径
        """
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'config',
            f'{config_name}.json'
        )
    
    @staticmethod
    def load_json_config(config_name):
        """
        加载JSON格式的配置文件
        
        Args:
            config_name: 配置文件名（不含路径和扩展名）
            
        Returns:
            dict: 配置数据字典，如果加载失败则返回空字典
        """
        try:
            # 获取配置文件路径
            config_path = ConfigLoader.get_config_path(config_name)
            
            if not os.path.exists(config_path):
                current_app.logger.warning(f"配置文件不存在: {config_path}")
                return {}
                
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                
            return config_data
            
        except Exception as e:
            if current_app:
                current_app.logger.error(f"加载配置文件失败: {str(e)}")
            else:
                print(f"加载配置文件失败: {str(e)}")
            return {}
    
    @staticmethod
    def save_json_config(config_name, config_data):
        """
        保存JSON格式的配置文件
        
        Args:
            config_name: 配置文件名（不含路径和扩展名）
            config_data: 要保存的配置数据字典
            
        Returns:
            bool: 保存是否成功
        """
        try:
            # 获取配置文件路径
            config_path = ConfigLoader.get_config_path(config_name)
            
            # 确保配置目录存在
            config_dir = os.path.dirname(config_path)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            # 保存配置
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
                
            return True
            
        except Exception as e:
            if current_app:
                current_app.logger.error(f"保存配置文件失败: {str(e)}")
            else:
                print(f"保存配置文件失败: {str(e)}")
            return False
    
    @staticmethod
    def get_column_mappings():
        """
        获取列名映射配置
        
        Returns:
            dict: 列名映射配置字典
        """
        config = ConfigLoader.load_json_config('column_mappings')
        return config
    
    @staticmethod
    def save_column_mappings(config_data):
        """
        保存列名映射配置
        
        Args:
            config_data: 列名映射配置字典
            
        Returns:
            bool: 保存是否成功
        """
        # 验证配置数据格式
        if not isinstance(config_data, dict):
            return False
            
        # 确保包含必要的键
        required_keys = ['column_mappings', 'required_columns', 'optional_columns']
        for key in required_keys:
            if key not in config_data:
                return False
        
        # 保存配置
        return ConfigLoader.save_json_config('column_mappings', config_data)
    
    @staticmethod
    def get_default_column_mappings():
        """
        获取默认的列名映射配置
        
        Returns:
            dict: 默认的列名映射配置字典
        """
        return {
            "column_mappings": {
                "item_id": ["产品ID", "商品编号", "货号", "item id", "itemid", "id"],
                "product_name": ["产品名称", "商品名称", "名称", "product name", "productname", "name"],
                "size": ["尺寸", "规格", "型号", "size"],
                "color": ["颜色", "色彩", "color"],
                "standard_unit_price": ["标准单价", "单价", "价格", "price", "unit price", "unitprice"]
            },
            "required_columns": ["item_id", "product_name"],
            "optional_columns": ["size", "color", "standard_unit_price"]
        }