"""
测试配置管理功能
"""

import os
import sys
import unittest
import json
import tempfile
import shutil

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.config_loader import ConfigLoader

class TestConfigLoader(unittest.TestCase):
    """测试配置加载器"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建临时目录用于测试
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, 'config')
        os.makedirs(self.config_dir)
        
        # 备份原始配置路径方法
        self.original_get_config_path = ConfigLoader.get_config_path
        
        # 修改配置路径指向临时目录
        ConfigLoader.get_config_path = lambda config_name: os.path.join(self.config_dir, f'{config_name}.json')
    
    def tearDown(self):
        """测试后的清理工作"""
        # 恢复原始配置路径方法
        ConfigLoader.get_config_path = self.original_get_config_path
        
        # 删除临时目录
        shutil.rmtree(self.temp_dir)
    
    def test_load_existing_config(self):
        """测试加载现有配置"""
        # 创建测试配置文件
        test_config = {
            'test_key': 'test_value',
            'test_number': 123,
            'test_list': ['item1', 'item2']
        }
        
        config_path = os.path.join(self.config_dir, 'test_config.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(test_config, f, ensure_ascii=False, indent=2)
        
        # 测试加载
        loaded_config = ConfigLoader.load_json_config('test_config')
        
        # 验证结果
        self.assertEqual(loaded_config, test_config)
    
    def test_load_nonexistent_config(self):
        """测试加载不存在的配置"""
        # 测试加载不存在的配置
        loaded_config = ConfigLoader.load_json_config('nonexistent_config')
        
        # 验证结果
        self.assertEqual(loaded_config, {})
    
    def test_save_config(self):
        """测试保存配置"""
        # 创建测试配置
        test_config = {
            'column_mappings': {
                'item_id': ['产品ID', '商品编号'],
                'product_name': ['产品名称', '商品名称']
            },
            'required_columns': ['item_id', 'product_name'],
            'optional_columns': ['size', 'color']
        }
        
        # 测试保存
        success = ConfigLoader.save_json_config('test_save_config', test_config)
        
        # 验证保存成功
        self.assertTrue(success)
        
        # 验证文件存在
        config_path = os.path.join(self.config_dir, 'test_save_config.json')
        self.assertTrue(os.path.exists(config_path))
        
        # 验证内容正确
        with open(config_path, 'r', encoding='utf-8') as f:
            saved_config = json.load(f)
        
        self.assertEqual(saved_config, test_config)
    
    def test_save_column_mappings(self):
        """测试保存列名映射配置"""
        # 创建测试配置
        test_config = {
            'column_mappings': {
                'item_id': ['产品ID', '商品编号'],
                'product_name': ['产品名称', '商品名称'],
                'standard_unit_price': ['标准单价', '单价']
            },
            'required_columns': ['item_id', 'product_name'],
            'optional_columns': ['standard_unit_price']
        }
        
        # 测试保存
        success = ConfigLoader.save_column_mappings(test_config)
        
        # 验证保存成功
        self.assertTrue(success)
        
        # 验证可以重新加载
        loaded_config = ConfigLoader.get_column_mappings()
        self.assertEqual(loaded_config, test_config)
    
    def test_save_invalid_column_mappings(self):
        """测试保存无效的列名映射配置"""
        # 测试保存非字典类型
        success = ConfigLoader.save_column_mappings("invalid")
        self.assertFalse(success)
        
        # 测试保存缺少必要键的配置
        invalid_config = {
            'column_mappings': {},
            'required_columns': []
            # 缺少 optional_columns
        }
        success = ConfigLoader.save_column_mappings(invalid_config)
        self.assertFalse(success)
    
    def test_get_default_column_mappings(self):
        """测试获取默认列名映射配置"""
        default_config = ConfigLoader.get_default_column_mappings()
        
        # 验证配置结构
        self.assertIn('column_mappings', default_config)
        self.assertIn('required_columns', default_config)
        self.assertIn('optional_columns', default_config)
        
        # 验证必要的列存在
        self.assertIn('item_id', default_config['column_mappings'])
        self.assertIn('product_name', default_config['column_mappings'])
        
        # 验证必需列配置
        self.assertIn('item_id', default_config['required_columns'])
        self.assertIn('product_name', default_config['required_columns'])

class TestColumnMappingsConfig(unittest.TestCase):
    """测试列名映射配置功能"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建临时目录用于测试
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, 'config')
        os.makedirs(self.config_dir)
        
        # 备份原始配置路径方法
        self.original_get_config_path = ConfigLoader.get_config_path
        
        # 修改配置路径指向临时目录
        ConfigLoader.get_config_path = lambda config_name: os.path.join(self.config_dir, f'{config_name}.json')
    
    def tearDown(self):
        """测试后的清理工作"""
        # 恢复原始配置路径方法
        ConfigLoader.get_config_path = self.original_get_config_path
        
        # 删除临时目录
        shutil.rmtree(self.temp_dir)
    
    def test_complete_column_mappings_config(self):
        """测试完整的列名映射配置"""
        # 创建完整的配置
        config = {
            'column_mappings': {
                'item_id': ['产品ID', '商品编号', '货号', 'Drawing'],
                'product_name': ['产品名称', '商品名称', '名称', 'Description'],
                'size': ['尺寸', '规格', '型号'],
                'color': ['颜色', '色彩', 'Supplier'],
                'standard_unit_price': ['标准单价', '单价', '价格', '1-50']
            },
            'required_columns': ['item_id', 'product_name'],
            'optional_columns': ['size', 'color', 'standard_unit_price']
        }
        
        # 保存配置
        success = ConfigLoader.save_column_mappings(config)
        self.assertTrue(success)
        
        # 重新加载配置
        loaded_config = ConfigLoader.get_column_mappings()
        
        # 验证配置完整性
        self.assertEqual(loaded_config, config)
        
        # 验证所有必需列都在映射中定义
        for col in loaded_config['required_columns']:
            self.assertIn(col, loaded_config['column_mappings'])
        
        # 验证所有可选列都在映射中定义
        for col in loaded_config['optional_columns']:
            self.assertIn(col, loaded_config['column_mappings'])
    
    def test_minimal_column_mappings_config(self):
        """测试最小的列名映射配置"""
        # 创建最小配置
        config = {
            'column_mappings': {
                'item_id': ['item_id'],
                'product_name': ['product_name']
            },
            'required_columns': ['item_id', 'product_name'],
            'optional_columns': []
        }
        
        # 保存配置
        success = ConfigLoader.save_column_mappings(config)
        self.assertTrue(success)
        
        # 重新加载配置
        loaded_config = ConfigLoader.get_column_mappings()
        
        # 验证配置
        self.assertEqual(loaded_config, config)
    
    def test_config_with_unicode_characters(self):
        """测试包含Unicode字符的配置"""
        # 创建包含Unicode字符的配置
        config = {
            'column_mappings': {
                'item_id': ['产品ID', '商品編號', '貨號'],
                'product_name': ['產品名稱', '商品名稱', '名稱'],
                'standard_unit_price': ['標準單價', '單價', '價格']
            },
            'required_columns': ['item_id', 'product_name'],
            'optional_columns': ['standard_unit_price']
        }
        
        # 保存配置
        success = ConfigLoader.save_column_mappings(config)
        self.assertTrue(success)
        
        # 重新加载配置
        loaded_config = ConfigLoader.get_column_mappings()
        
        # 验证Unicode字符正确保存和加载
        self.assertEqual(loaded_config, config)

if __name__ == '__main__':
    unittest.main()