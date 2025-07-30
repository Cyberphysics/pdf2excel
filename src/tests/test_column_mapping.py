"""
测试列名映射功能
"""

import os
import sys
import unittest
import pandas as pd
import numpy as np

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.enhanced_spec_manager import EnhancedProductSpecManager, MappingResult

class TestColumnMapping(unittest.TestCase):
    """测试列名映射功能"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.spec_manager = EnhancedProductSpecManager()
    
    def test_exact_match(self):
        """测试精确匹配"""
        # 创建测试数据
        data = {
            'item_id': ['ITEM001', 'ITEM002'],
            'product_name': ['产品A', '产品B'],
            'size': ['M', 'L'],
            'color': ['红色', '蓝色'],
            'standard_unit_price': [99.99, 129.99]
        }
        df = pd.DataFrame(data)
        
        # 测试映射
        result = self.spec_manager.map_columns(df)
        
        # 验证结果
        self.assertTrue(result.success)
        self.assertEqual(len(result.mapped_columns), 5)
        self.assertEqual(len(result.missing_required), 0)
        self.assertEqual(len(result.unmapped_columns), 0)
    
    def test_alias_match(self):
        """测试别名匹配"""
        # 创建测试数据
        data = {
            '产品ID': ['ITEM001', 'ITEM002'],
            '产品名称': ['产品A', '产品B'],
            '尺寸': ['M', 'L'],
            '颜色': ['红色', '蓝色'],
            '单价': [99.99, 129.99]
        }
        df = pd.DataFrame(data)
        
        # 测试映射
        result = self.spec_manager.map_columns(df)
        
        # 验证结果
        self.assertTrue(result.success)
        self.assertEqual(len(result.mapped_columns), 5)
        self.assertEqual(result.mapped_columns['产品ID'], 'item_id')
        self.assertEqual(result.mapped_columns['产品名称'], 'product_name')
        self.assertEqual(result.mapped_columns['尺寸'], 'size')
        self.assertEqual(result.mapped_columns['颜色'], 'color')
        self.assertEqual(result.mapped_columns['单价'], 'standard_unit_price')
        self.assertEqual(len(result.missing_required), 0)
        self.assertEqual(len(result.unmapped_columns), 0)
    
    def test_missing_required(self):
        """测试缺少必需列"""
        # 创建测试数据
        data = {
            'product_name': ['产品A', '产品B'],
            'size': ['M', 'L'],
            'color': ['红色', '蓝色']
        }
        df = pd.DataFrame(data)
        
        # 测试映射
        result = self.spec_manager.map_columns(df)
        
        # 验证结果
        self.assertFalse(result.success)
        self.assertEqual(len(result.mapped_columns), 3)
        self.assertEqual(len(result.missing_required), 2)
        self.assertTrue('item_id' in result.missing_required)
        self.assertTrue('standard_unit_price' in result.missing_required)
    
    def test_unmapped_columns(self):
        """测试无法映射的列"""
        # 创建测试数据
        data = {
            'item_id': ['ITEM001', 'ITEM002'],
            'product_name': ['产品A', '产品B'],
            'size': ['M', 'L'],
            'color': ['红色', '蓝色'],
            'standard_unit_price': [99.99, 129.99],
            'extra_column': ['额外1', '额外2'],
            'another_extra': ['其他1', '其他2']
        }
        df = pd.DataFrame(data)
        
        # 测试映射
        result = self.spec_manager.map_columns(df)
        
        # 验证结果
        self.assertTrue(result.success)  # 仍然成功，因为所有必需列都存在
        self.assertEqual(len(result.mapped_columns), 5)
        self.assertEqual(len(result.unmapped_columns), 2)
        self.assertTrue('extra_column' in result.unmapped_columns)
        self.assertTrue('another_extra' in result.unmapped_columns)
    
    def test_create_mapped_dataframe(self):
        """测试创建映射后的DataFrame"""
        # 创建测试数据
        data = {
            '产品ID': ['ITEM001', 'ITEM002'],
            '产品名称': ['产品A', '产品B'],
            '尺寸': ['M', 'L'],
            '颜色': ['红色', '蓝色'],
            '单价': [99.99, 129.99]
        }
        df = pd.DataFrame(data)
        
        # 测试映射
        result = self.spec_manager.map_columns(df)
        mapped_df = self.spec_manager.create_mapped_dataframe(df, result)
        
        # 验证结果
        self.assertEqual(len(mapped_df.columns), 5)
        self.assertTrue('item_id' in mapped_df.columns)
        self.assertTrue('product_name' in mapped_df.columns)
        self.assertTrue('size' in mapped_df.columns)
        self.assertTrue('color' in mapped_df.columns)
        self.assertTrue('standard_unit_price' in mapped_df.columns)
        
        # 验证数据是否正确映射
        self.assertEqual(mapped_df['item_id'].tolist(), ['ITEM001', 'ITEM002'])
        self.assertEqual(mapped_df['product_name'].tolist(), ['产品A', '产品B'])
        self.assertEqual(mapped_df['size'].tolist(), ['M', 'L'])
        self.assertEqual(mapped_df['color'].tolist(), ['红色', '蓝色'])
        self.assertEqual(mapped_df['standard_unit_price'].tolist(), [99.99, 129.99])

class TestColumnMappingExamples(unittest.TestCase):
    """测试列名映射示例功能"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.spec_manager = EnhancedProductSpecManager()
    
    def test_generate_column_mapping_examples(self):
        """测试生成列名映射示例"""
        examples = self.spec_manager.generate_column_mapping_examples()
        
        # 验证结果
        self.assertTrue(isinstance(examples, dict))
        self.assertTrue('item_id' in examples)
        self.assertTrue('product_name' in examples)
        self.assertTrue('standard_unit_price' in examples)
        
        # 验证示例格式
        for col, example in examples.items():
            self.assertIn('standard', example)
            self.assertIn('aliases', example)
            self.assertIn('required', example)
            self.assertEqual(example['standard'], col)
            self.assertTrue(isinstance(example['aliases'], list))
    
    def test_generate_sample_excel(self):
        """测试生成示例Excel"""
        # 默认行数
        df = self.spec_manager.generate_sample_excel()
        self.assertEqual(len(df), 5)
        
        # 自定义行数
        df = self.spec_manager.generate_sample_excel(10)
        self.assertEqual(len(df), 10)
        
        # 验证列
        for col in self.spec_manager.required_columns + self.spec_manager.optional_columns:
            self.assertIn(col, df.columns)
        
        # 验证数据类型
        if 'item_id' in df.columns:
            self.assertTrue(all(isinstance(x, str) for x in df['item_id']))
        
        if 'standard_unit_price' in df.columns:
            self.assertTrue(all(isinstance(x, (int, float)) for x in df['standard_unit_price']))class
 TestAdvancedColumnMapping(unittest.TestCase):
    """测试高级列名映射功能"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.spec_manager = EnhancedProductSpecManager()
    
    def test_fuzzy_matching(self):
        """测试模糊匹配"""
        # 创建包含相似列名的测试数据
        data = {
            'itemid': ['ITEM001', 'ITEM002'],  # 缺少下划线
            'productname': ['产品A', '产品B'],  # 缺少下划线
            'unitprice': [99.99, 129.99]  # 缺少下划线和前缀
        }
        df = pd.DataFrame(data)
        
        # 测试映射
        result = self.spec_manager.map_columns(df)
        
        # 验证结果
        self.assertTrue(result.success)
        self.assertEqual(len(result.mapped_columns), 3)
        self.assertEqual(result.mapped_columns['itemid'], 'item_id')
        self.assertEqual(result.mapped_columns['productname'], 'product_name')
        self.assertEqual(result.mapped_columns['unitprice'], 'standard_unit_price')
    
    def test_case_insensitive_matching(self):
        """测试大小写不敏感匹配"""
        # 创建包含不同大小写的测试数据
        data = {
            'ITEM_ID': ['ITEM001', 'ITEM002'],
            'Product_Name': ['产品A', '产品B'],
            'STANDARD_UNIT_PRICE': [99.99, 129.99]
        }
        df = pd.DataFrame(data)
        
        # 测试映射
        result = self.spec_manager.map_columns(df)
        
        # 验证结果
        self.assertTrue(result.success)
        self.assertEqual(len(result.mapped_columns), 3)
        self.assertEqual(result.mapped_columns['ITEM_ID'], 'item_id')
        self.assertEqual(result.mapped_columns['Product_Name'], 'product_name')
        self.assertEqual(result.mapped_columns['STANDARD_UNIT_PRICE'], 'standard_unit_price')
    
    def test_mixed_language_mapping(self):
        """测试中英文混合映射"""
        # 创建包含中英文混合列名的测试数据
        data = {
            'Drawing': ['ITEM001', 'ITEM002'],  # 英文别名
            'Description': ['产品A', '产品B'],  # 英文别名
            '1-50': [99.99, 129.99]  # 数字范围别名
        }
        df = pd.DataFrame(data)
        
        # 测试映射
        result = self.spec_manager.map_columns(df)
        
        # 验证结果
        self.assertTrue(result.success)
        self.assertEqual(len(result.mapped_columns), 3)
        self.assertEqual(result.mapped_columns['Drawing'], 'item_id')
        self.assertEqual(result.mapped_columns['Description'], 'product_name')
        self.assertEqual(result.mapped_columns['1-50'], 'standard_unit_price')
    
    def test_partial_mapping_with_suggestions(self):
        """测试部分映射并生成建议"""
        # 创建包含部分可映射列的测试数据
        data = {
            'item_id': ['ITEM001', 'ITEM002'],
            'product_name': ['产品A', '产品B'],
            'unknown_column': ['值1', '值2'],  # 无法映射的列
            'price_maybe': [99.99, 129.99]  # 可能是价格的列
        }
        df = pd.DataFrame(data)
        
        # 测试映射
        result = self.spec_manager.map_columns(df)
        
        # 验证结果
        self.assertFalse(result.success)  # 缺少必需列
        self.assertEqual(len(result.mapped_columns), 2)
        self.assertEqual(len(result.unmapped_columns), 2)
        self.assertIn('unknown_column', result.unmapped_columns)
        self.assertIn('price_maybe', result.unmapped_columns)
        
        # 检查建议
        self.assertIn('price_maybe', result.suggestions)
        self.assertIn('standard_unit_price', result.suggestions['price_maybe']['suggestions'])
    
    def test_mapping_with_extra_columns(self):
        """测试包含额外列的映射"""
        # 创建包含额外列的测试数据
        data = {
            'item_id': ['ITEM001', 'ITEM002'],
            'product_name': ['产品A', '产品B'],
            'standard_unit_price': [99.99, 129.99],
            'extra1': ['额外1', '额外2'],
            'extra2': ['其他1', '其他2'],
            'extra3': ['更多1', '更多2']
        }
        df = pd.DataFrame(data)
        
        # 测试映射
        result = self.spec_manager.map_columns(df)
        
        # 验证结果
        self.assertTrue(result.success)
        self.assertEqual(len(result.mapped_columns), 3)
        self.assertEqual(len(result.unmapped_columns), 3)
        self.assertEqual(len(result.missing_required), 0)
    
    def test_create_mapped_dataframe_with_missing_columns(self):
        """测试创建包含缺失列的映射DataFrame"""
        # 创建测试数据
        data = {
            'item_id': ['ITEM001', 'ITEM002'],
            'product_name': ['产品A', '产品B']
        }
        df = pd.DataFrame(data)
        
        # 创建映射结果
        mapping_result = MappingResult()
        mapping_result.success = False
        mapping_result.mapped_columns = {'item_id': 'item_id', 'product_name': 'product_name'}
        mapping_result.missing_required = ['standard_unit_price']
        
        # 创建映射后的DataFrame
        mapped_df = self.spec_manager.create_mapped_dataframe(df, mapping_result)
        
        # 验证结果
        self.assertEqual(len(mapped_df.columns), 3)
        self.assertTrue('item_id' in mapped_df.columns)
        self.assertTrue('product_name' in mapped_df.columns)
        self.assertTrue('standard_unit_price' in mapped_df.columns)
        
        # 验证缺失列包含NaN值
        self.assertTrue(mapped_df['standard_unit_price'].isna().all())

class TestConfigurationLoading(unittest.TestCase):
    """测试配置加载功能"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.spec_manager = EnhancedProductSpecManager()
    
    def test_load_column_mappings(self):
        """测试加载列名映射配置"""
        # 重新加载配置
        self.spec_manager.load_column_mappings()
        
        # 验证配置已加载
        self.assertIsInstance(self.spec_manager.column_mappings, dict)
        self.assertIsInstance(self.spec_manager.required_columns, list)
        self.assertIsInstance(self.spec_manager.optional_columns, list)
        
        # 验证必需列
        self.assertIn('item_id', self.spec_manager.required_columns)
        self.assertIn('product_name', self.spec_manager.required_columns)
        
        # 验证列映射
        self.assertIn('item_id', self.spec_manager.column_mappings)
        self.assertIn('product_name', self.spec_manager.column_mappings)
    
    def test_default_configuration(self):
        """测试默认配置"""
        # 创建新的管理器实例
        spec_manager = EnhancedProductSpecManager()
        
        # 验证默认配置
        self.assertTrue(len(spec_manager.column_mappings) > 0)
        self.assertTrue(len(spec_manager.required_columns) > 0)
        self.assertTrue(len(spec_manager.optional_columns) >= 0)
        
        # 验证默认必需列
        self.assertIn('item_id', spec_manager.required_columns)
        self.assertIn('product_name', spec_manager.required_columns)

if __name__ == '__main__':
    unittest.main()