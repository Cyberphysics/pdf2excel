"""
集成测试 - 完整的上传和验证工作流程
"""

import os
import sys
import unittest
import tempfile
import shutil
import json
import pandas as pd
from unittest.mock import patch, MagicMock
from werkzeug.datastructures import FileStorage
from io import BytesIO

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.enhanced_spec_manager import EnhancedProductSpecManager
from src.utils.config_loader import ConfigLoader

class TestCompleteUploadWorkflow(unittest.TestCase):
    """测试完整的上传和验证工作流程"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.specs_dir = os.path.join(self.temp_dir, 'specs')
        self.config_dir = os.path.join(self.temp_dir, 'config')
        os.makedirs(self.specs_dir)
        os.makedirs(self.config_dir)
        
        # 创建规格管理器实例
        self.spec_manager = EnhancedProductSpecManager(specs_dir=self.specs_dir)
        
        # 备份原始配置路径方法
        self.original_get_config_path = ConfigLoader.get_config_path
        
        # 修改配置路径指向临时目录
        ConfigLoader.get_config_path = lambda config_name: os.path.join(self.config_dir, f'{config_name}.json')
        
        # 创建测试配置
        self.create_test_config()
        
        # 创建测试Excel文件
        self.create_test_excel_files()
    
    def tearDown(self):
        """测试后的清理工作"""
        # 恢复原始配置路径方法
        ConfigLoader.get_config_path = self.original_get_config_path
        
        # 删除临时目录
        shutil.rmtree(self.temp_dir)
    
    def create_test_config(self):
        """创建测试配置"""
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
        
        config_path = os.path.join(self.config_dir, 'column_mappings.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def create_test_excel_files(self):
        """创建测试用的Excel文件"""
        # 1. 完全匹配的规格表
        perfect_data = {
            'item_id': ['ITEM001', 'ITEM002', 'ITEM003'],
            'product_name': ['产品A', '产品B', '产品C'],
            'size': ['M', 'L', 'XL'],
            'color': ['红色', '蓝色', '绿色'],
            'standard_unit_price': [99.99, 129.99, 159.99]
        }
        self.perfect_excel_path = os.path.join(self.temp_dir, 'perfect_spec.xlsx')
        pd.DataFrame(perfect_data).to_excel(self.perfect_excel_path, index=False)
        
        # 2. 需要映射的规格表（中文列名）
        chinese_data = {
            '产品ID': ['ITEM001', 'ITEM002', 'ITEM003'],
            '产品名称': ['产品A', '产品B', '产品C'],
            '尺寸': ['M', 'L', 'XL'],
            '颜色': ['红色', '蓝色', '绿色'],
            '单价': [99.99, 129.99, 159.99]
        }
        self.chinese_excel_path = os.path.join(self.temp_dir, 'chinese_spec.xlsx')
        pd.DataFrame(chinese_data).to_excel(self.chinese_excel_path, index=False)
        
        # 3. 需要映射的规格表（英文列名）
        english_data = {
            'Drawing': ['ITEM001', 'ITEM002', 'ITEM003'],
            'Description': ['产品A', '产品B', '产品C'],
            '1-50': [99.99, 129.99, 159.99]
        }
        self.english_excel_path = os.path.join(self.temp_dir, 'english_spec.xlsx')
        pd.DataFrame(english_data).to_excel(self.english_excel_path, index=False)
        
        # 4. 缺少必需列的规格表
        incomplete_data = {
            'item_id': ['ITEM001', 'ITEM002'],
            'description': ['产品A', '产品B']  # 错误的列名
        }
        self.incomplete_excel_path = os.path.join(self.temp_dir, 'incomplete_spec.xlsx')
        pd.DataFrame(incomplete_data).to_excel(self.incomplete_excel_path, index=False)
        
        # 5. 包含数据错误的规格表
        error_data = {
            'item_id': ['ITEM001', None, 'ITEM003'],  # 包含空值
            'product_name': ['产品A', '产品B', '产品C'],
            'standard_unit_price': [99.99, '无效价格', -50.0]  # 包含无效价格和负价格
        }
        self.error_excel_path = os.path.join(self.temp_dir, 'error_spec.xlsx')
        pd.DataFrame(error_data).to_excel(self.error_excel_path, index=False)
    
    def create_file_storage(self, file_path, filename=None):
        """创建FileStorage对象用于模拟文件上传"""
        if filename is None:
            filename = os.path.basename(file_path)
        
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        return FileStorage(
            stream=BytesIO(file_data),
            filename=filename,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    def test_perfect_spec_upload_workflow(self):
        """测试完美规格表的完整上传工作流程"""
        # 创建文件上传对象
        file_storage = self.create_file_storage(self.perfect_excel_path, 'perfect_spec.xlsx')
        
        # 执行上传
        result = self.spec_manager.upload_spec(file_storage)
        
        # 验证上传成功
        self.assertNotIn('error', result)
        self.assertIn('spec_id', result)
        self.assertIn('filename', result)
        self.assertEqual(result['filename'], 'perfect_spec.xlsx')
        self.assertEqual(result['record_count'], 3)
        self.assertTrue(result['mapping_applied'])
        
        # 验证文件已保存
        spec_id = result['spec_id']
        spec_file_path = self.spec_manager.get_spec_path(spec_id)
        self.assertIsNotNone(spec_file_path)
        self.assertTrue(os.path.exists(spec_file_path))
        
        # 验证元数据文件已创建
        metadata_path = os.path.join(self.specs_dir, f"{spec_id}.json")
        self.assertTrue(os.path.exists(metadata_path))
        
        # 验证元数据内容
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        self.assertEqual(metadata['spec_id'], spec_id)
        self.assertEqual(metadata['original_filename'], 'perfect_spec.xlsx')
        self.assertEqual(metadata['record_count'], 3)
        self.assertIn('column_mapping', metadata)
        
        # 验证映射后的文件内容
        mapped_df = pd.read_excel(spec_file_path)
        self.assertEqual(len(mapped_df), 3)
        self.assertIn('item_id', mapped_df.columns)
        self.assertIn('product_name', mapped_df.columns)
        self.assertIn('standard_unit_price', mapped_df.columns)
    
    def test_chinese_spec_upload_workflow(self):
        """测试中文列名规格表的完整上传工作流程"""
        # 创建文件上传对象
        file_storage = self.create_file_storage(self.chinese_excel_path, 'chinese_spec.xlsx')
        
        # 执行上传
        result = self.spec_manager.upload_spec(file_storage)
        
        # 验证上传成功
        self.assertNotIn('error', result)
        self.assertIn('spec_id', result)
        self.assertEqual(result['filename'], 'chinese_spec.xlsx')
        self.assertEqual(result['record_count'], 3)
        self.assertTrue(result['mapping_applied'])
        
        # 验证列映射
        expected_mapping = {
            '产品ID': 'item_id',
            '产品名称': 'product_name',
            '尺寸': 'size',
            '颜色': 'color',
            '单价': 'standard_unit_price'
        }
        self.assertEqual(result['mapped_columns'], expected_mapping)
        
        # 验证映射后的文件内容
        spec_id = result['spec_id']
        spec_file_path = self.spec_manager.get_spec_path(spec_id)
        mapped_df = pd.read_excel(spec_file_path)
        
        # 验证数据正确映射
        self.assertEqual(mapped_df['item_id'].tolist(), ['ITEM001', 'ITEM002', 'ITEM003'])
        self.assertEqual(mapped_df['product_name'].tolist(), ['产品A', '产品B', '产品C'])
        self.assertEqual(mapped_df['size'].tolist(), ['M', 'L', 'XL'])
        self.assertEqual(mapped_df['color'].tolist(), ['红色', '蓝色', '绿色'])
        self.assertEqual(mapped_df['standard_unit_price'].tolist(), [99.99, 129.99, 159.99])
    
    def test_english_spec_upload_workflow(self):
        """测试英文列名规格表的完整上传工作流程"""
        # 创建文件上传对象
        file_storage = self.create_file_storage(self.english_excel_path, 'english_spec.xlsx')
        
        # 执行上传
        result = self.spec_manager.upload_spec(file_storage)
        
        # 验证上传成功
        self.assertNotIn('error', result)
        self.assertIn('spec_id', result)
        self.assertEqual(result['filename'], 'english_spec.xlsx')
        self.assertEqual(result['record_count'], 3)
        self.assertTrue(result['mapping_applied'])
        
        # 验证列映射
        expected_mapping = {
            'Drawing': 'item_id',
            'Description': 'product_name',
            '1-50': 'standard_unit_price'
        }
        self.assertEqual(result['mapped_columns'], expected_mapping)
    
    def test_incomplete_spec_upload_workflow(self):
        """测试不完整规格表的上传工作流程"""
        # 创建文件上传对象
        file_storage = self.create_file_storage(self.incomplete_excel_path, 'incomplete_spec.xlsx')
        
        # 执行上传
        result = self.spec_manager.upload_spec(file_storage)
        
        # 验证上传失败
        self.assertIn('error', result)
        self.assertIn('error_code', result)
        self.assertEqual(result['error_code'], 'MISSING_REQUIRED_COLUMNS')
        self.assertIn('missing_columns', result)
        self.assertIn('product_name', result['missing_columns'])
        
        # 验证建议信息
        self.assertIn('structured_suggestions', result)
        
        # 验证没有文件被保存
        specs_files = os.listdir(self.specs_dir)
        excel_files = [f for f in specs_files if f.endswith('.xlsx')]
        self.assertEqual(len(excel_files), 0)
    
    def test_error_data_spec_upload_workflow(self):
        """测试包含数据错误的规格表上传工作流程"""
        # 创建文件上传对象
        file_storage = self.create_file_storage(self.error_excel_path, 'error_spec.xlsx')
        
        # 执行上传
        result = self.spec_manager.upload_spec(file_storage)
        
        # 验证上传失败
        self.assertIn('error', result)
        self.assertIn('error_code', result)
        self.assertEqual(result['error_code'], 'DATA_VALIDATION_ERROR')
        
        # 验证数据错误信息
        self.assertIn('data_errors', result)
        self.assertIn('item_id', result['data_errors'])
        self.assertIn('standard_unit_price', result['data_errors'])
        
        # 验证建议信息
        self.assertIn('suggestions', result)
        
        # 验证没有文件被保存
        specs_files = os.listdir(self.specs_dir)
        excel_files = [f for f in specs_files if f.endswith('.xlsx')]
        self.assertEqual(len(excel_files), 0)
    
    def test_spec_list_and_delete_workflow(self):
        """测试规格表列表和删除工作流程"""
        # 上传多个规格表
        file1 = self.create_file_storage(self.perfect_excel_path, 'spec1.xlsx')
        file2 = self.create_file_storage(self.chinese_excel_path, 'spec2.xlsx')
        
        result1 = self.spec_manager.upload_spec(file1)
        result2 = self.spec_manager.upload_spec(file2)
        
        # 验证上传成功
        self.assertNotIn('error', result1)
        self.assertNotIn('error', result2)
        
        spec_id1 = result1['spec_id']
        spec_id2 = result2['spec_id']
        
        # 获取规格表列表
        specs_list = self.spec_manager.list_specs()
        
        # 验证列表内容
        self.assertEqual(len(specs_list), 2)
        
        # 验证列表项内容
        spec_ids = [spec['spec_id'] for spec in specs_list]
        self.assertIn(spec_id1, spec_ids)
        self.assertIn(spec_id2, spec_ids)
        
        # 删除一个规格表
        delete_result = self.spec_manager.delete_spec(spec_id1)
        self.assertNotIn('error', delete_result)
        self.assertIn('message', delete_result)
        
        # 验证文件已删除
        self.assertIsNone(self.spec_manager.get_spec_path(spec_id1))
        
        # 验证列表更新
        updated_specs_list = self.spec_manager.list_specs()
        self.assertEqual(len(updated_specs_list), 1)
        self.assertEqual(updated_specs_list[0]['spec_id'], spec_id2)
    
    def test_spec_validation_workflow(self):
        """测试规格表验证工作流程"""
        # 上传一个规格表
        file_storage = self.create_file_storage(self.perfect_excel_path, 'test_spec.xlsx')
        upload_result = self.spec_manager.upload_spec(file_storage)
        
        self.assertNotIn('error', upload_result)
        spec_id = upload_result['spec_id']
        
        # 获取规格表路径并验证
        spec_path = self.spec_manager.get_spec_path(spec_id)
        validation_result = self.spec_manager.validate_spec_format(spec_path)
        
        # 验证结果
        self.assertTrue(validation_result['valid'])
        self.assertEqual(validation_result['record_count'], 3)
        self.assertIn('columns', validation_result)
        self.assertIn('mapped_columns', validation_result)

class TestConfigurationChangeWorkflow(unittest.TestCase):
    """测试配置更改应用工作流程"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.specs_dir = os.path.join(self.temp_dir, 'specs')
        self.config_dir = os.path.join(self.temp_dir, 'config')
        os.makedirs(self.specs_dir)
        os.makedirs(self.config_dir)
        
        # 备份原始配置路径方法
        self.original_get_config_path = ConfigLoader.get_config_path
        
        # 修改配置路径指向临时目录
        ConfigLoader.get_config_path = lambda config_name: os.path.join(self.config_dir, f'{config_name}.json')
        
        # 创建初始配置
        self.create_initial_config()
        
        # 创建规格管理器实例
        self.spec_manager = EnhancedProductSpecManager(specs_dir=self.specs_dir)
    
    def tearDown(self):
        """测试后的清理工作"""
        # 恢复原始配置路径方法
        ConfigLoader.get_config_path = self.original_get_config_path
        
        # 删除临时目录
        shutil.rmtree(self.temp_dir)
    
    def create_initial_config(self):
        """创建初始配置"""
        config = {
            'column_mappings': {
                'item_id': ['产品ID', '商品编号'],
                'product_name': ['产品名称', '商品名称'],
                'standard_unit_price': ['标准单价', '单价']
            },
            'required_columns': ['item_id', 'product_name'],
            'optional_columns': ['standard_unit_price']
        }
        
        config_path = os.path.join(self.config_dir, 'column_mappings.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def test_config_change_application(self):
        """测试配置更改的应用"""
        # 验证初始配置
        initial_mappings = self.spec_manager.column_mappings
        self.assertEqual(len(initial_mappings['item_id']), 2)
        self.assertIn('产品ID', initial_mappings['item_id'])
        self.assertIn('商品编号', initial_mappings['item_id'])
        
        # 更新配置
        new_config = {
            'column_mappings': {
                'item_id': ['产品ID', '商品编号', '货号', 'Drawing'],
                'product_name': ['产品名称', '商品名称', '名称', 'Description'],
                'size': ['尺寸', '规格'],
                'color': ['颜色', '色彩'],
                'standard_unit_price': ['标准单价', '单价', '价格']
            },
            'required_columns': ['item_id', 'product_name'],
            'optional_columns': ['size', 'color', 'standard_unit_price']
        }
        
        # 保存新配置
        success = ConfigLoader.save_column_mappings(new_config)
        self.assertTrue(success)
        
        # 重新加载配置
        self.spec_manager.load_column_mappings()
        
        # 验证配置已更新
        updated_mappings = self.spec_manager.column_mappings
        self.assertEqual(len(updated_mappings['item_id']), 4)
        self.assertIn('货号', updated_mappings['item_id'])
        self.assertIn('Drawing', updated_mappings['item_id'])
        
        # 验证新的可选列
        self.assertIn('size', updated_mappings)
        self.assertIn('color', updated_mappings)
        self.assertIn('size', self.spec_manager.optional_columns)
        self.assertIn('color', self.spec_manager.optional_columns)
    
    def test_config_change_affects_mapping(self):
        """测试配置更改对映射的影响"""
        # 创建测试数据（使用新的别名）
        test_data = {
            '货号': ['ITEM001', 'ITEM002'],
            'Description': ['产品A', '产品B'],
            '价格': [99.99, 129.99]
        }
        
        test_excel_path = os.path.join(self.temp_dir, 'test_new_aliases.xlsx')
        pd.DataFrame(test_data).to_excel(test_excel_path, index=False)
        
        # 使用初始配置尝试映射（应该失败）
        df = pd.read_excel(test_excel_path)
        initial_result = self.spec_manager.map_columns(df)
        self.assertFalse(initial_result.success)  # 应该失败，因为'货号'和'Description'不在初始配置中
        
        # 更新配置以包含新的别名
        new_config = {
            'column_mappings': {
                'item_id': ['产品ID', '商品编号', '货号', 'Drawing'],
                'product_name': ['产品名称', '商品名称', '名称', 'Description'],
                'standard_unit_price': ['标准单价', '单价', '价格']
            },
            'required_columns': ['item_id', 'product_name'],
            'optional_columns': ['standard_unit_price']
        }
        
        ConfigLoader.save_column_mappings(new_config)
        self.spec_manager.load_column_mappings()
        
        # 使用更新后的配置重新尝试映射（应该成功）
        updated_result = self.spec_manager.map_columns(df)
        self.assertTrue(updated_result.success)
        
        # 验证映射结果
        expected_mapping = {
            '货号': 'item_id',
            'Description': 'product_name',
            '价格': 'standard_unit_price'
        }
        self.assertEqual(updated_result.mapped_columns, expected_mapping)
    
    def test_config_validation_workflow(self):
        """测试配置验证工作流程"""
        # 测试有效配置
        valid_config = {
            'column_mappings': {
                'item_id': ['产品ID'],
                'product_name': ['产品名称']
            },
            'required_columns': ['item_id', 'product_name'],
            'optional_columns': []
        }
        
        success = ConfigLoader.save_column_mappings(valid_config)
        self.assertTrue(success)
        
        # 测试无效配置（缺少必要键）
        invalid_config = {
            'column_mappings': {},
            'required_columns': []
            # 缺少 optional_columns
        }
        
        success = ConfigLoader.save_column_mappings(invalid_config)
        self.assertFalse(success)
        
        # 测试无效配置（非字典类型）
        success = ConfigLoader.save_column_mappings("invalid")
        self.assertFalse(success)

if __name__ == '__main__':
    unittest.main()