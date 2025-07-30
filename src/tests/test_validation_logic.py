"""
测试改进的验证逻辑
"""

import os
import sys
import unittest
import pandas as pd
import numpy as np

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.enhanced_spec_manager import EnhancedProductSpecManager

class TestValidationLogic(unittest.TestCase):
    """测试改进的验证逻辑"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.spec_manager = EnhancedProductSpecManager()
    
    def test_valid_dataframe(self):
        """测试有效的DataFrame"""
        # 创建测试数据
        data = {
            'item_id': ['ITEM001', 'ITEM002'],
            'product_name': ['产品A', '产品B'],
            'standard_unit_price': [99.99, 129.99]
        }
        df = pd.DataFrame(data)
        
        # 测试验证
        result = self.spec_manager.validate_mapped_dataframe(df)
        
        # 验证结果
        self.assertTrue(result['valid'])
        self.assertEqual(result['record_count'], 2)
        self.assertEqual(len(result['columns']), 3)
    
    def test_missing_required_columns(self):
        """测试缺少必需列"""
        # 创建测试数据
        data = {
            'item_id': ['ITEM001', 'ITEM002'],
            'product_name': ['产品A', '产品B']
        }
        df = pd.DataFrame(data)
        
        # 测试验证
        result = self.spec_manager.validate_mapped_dataframe(df)
        
        # 验证结果
        self.assertFalse(result['valid'])
        self.assertTrue('缺少必需的列: standard_unit_price' in result['error'])
        self.assertIn('suggestions', result)
        self.assertIn('missing_columns', result['suggestions'])
    
    def test_empty_item_id(self):
        """测试item_id为空"""
        # 创建测试数据
        data = {
            'item_id': ['ITEM001', None],
            'product_name': ['产品A', '产品B'],
            'standard_unit_price': [99.99, 129.99]
        }
        df = pd.DataFrame(data)
        
        # 测试验证
        result = self.spec_manager.validate_mapped_dataframe(df)
        
        # 验证结果
        self.assertFalse(result['valid'])
        self.assertTrue('item_id列存在空值' in result['error'])
        self.assertIn('data_errors', result)
        self.assertIn('item_id', result['data_errors'])
        self.assertEqual(result['data_errors']['item_id']['type'], 'null_values')
        self.assertEqual(result['data_errors']['item_id']['rows'], [2])
    
    def test_non_numeric_price(self):
        """测试非数字价格"""
        # 创建测试数据
        data = {
            'item_id': ['ITEM001', 'ITEM002'],
            'product_name': ['产品A', '产品B'],
            'standard_unit_price': [99.99, '非数字']
        }
        df = pd.DataFrame(data)
        
        # 测试验证
        result = self.spec_manager.validate_mapped_dataframe(df)
        
        # 验证结果
        self.assertFalse(result['valid'])
        self.assertTrue('standard_unit_price列包含非数字值' in result['error'])
        self.assertIn('data_errors', result)
        self.assertIn('standard_unit_price', result['data_errors'])
        self.assertEqual(result['data_errors']['standard_unit_price']['type'], 'invalid_type')
        self.assertEqual(result['data_errors']['standard_unit_price']['rows'], [2])
    
    def test_optional_columns(self):
        """测试可选列"""
        # 创建测试数据 - 包含所有可选列
        data = {
            'item_id': ['ITEM001', 'ITEM002'],
            'product_name': ['产品A', '产品B'],
            'standard_unit_price': [99.99, 129.99],
            'size': ['M', 'L'],
            'color': ['红色', '蓝色']
        }
        df = pd.DataFrame(data)
        
        # 测试验证
        result = self.spec_manager.validate_mapped_dataframe(df)
        
        # 验证结果
        self.assertTrue(result['valid'])
        self.assertEqual(result['record_count'], 2)
        self.assertEqual(len(result['columns']), 5)
        
        # 创建测试数据 - 只包含部分可选列
        data = {
            'item_id': ['ITEM001', 'ITEM002'],
            'product_name': ['产品A', '产品B'],
            'standard_unit_price': [99.99, 129.99],
            'size': ['M', 'L']
        }
        df = pd.DataFrame(data)
        
        # 测试验证
        result = self.spec_manager.validate_mapped_dataframe(df)
        
        # 验证结果
        self.assertTrue(result['valid'])
        self.assertEqual(result['record_count'], 2)
        self.assertEqual(len(result['columns']), 4)
    
    def test_multiple_errors(self):
        """测试多个错误"""
        # 创建测试数据
        data = {
            'item_id': ['ITEM001', None],
            'product_name': ['产品A', '产品B'],
            'standard_unit_price': [99.99, '非数字']
        }
        df = pd.DataFrame(data)
        
        # 测试验证
        result = self.spec_manager.validate_mapped_dataframe(df)
        
        # 验证结果
        self.assertFalse(result['valid'])
        self.assertTrue('item_id列存在空值' in result['error'])
        self.assertTrue('standard_unit_price列包含非数字值' in result['error'])
        self.assertIn('data_errors', result)
        self.assertIn('item_id', result['data_errors'])
        self.assertIn('standard_unit_price', result['data_errors'])
    
    def test_warnings(self):
        """测试警告信息"""
        # 创建测试数据 - 包含重复的item_id
        data = {
            'item_id': ['ITEM001', 'ITEM001', 'ITEM002'],
            'product_name': ['产品A', '产品A副本', '产品B'],
            'standard_unit_price': [99.99, 99.99, 129.99]
        }
        df = pd.DataFrame(data)
        
        # 测试验证
        result = self.spec_manager.validate_mapped_dataframe(df)
        
        # 验证结果 - 应该有效但有警告
        self.assertTrue(result['valid'])
        self.assertIn('warnings', result)
        self.assertTrue(any('item_id列存在重复值' in warning for warning in result['warnings']))
        self.assertIn('data_errors', result)
        self.assertIn('item_id', result['data_errors'])
        self.assertEqual(result['data_errors']['item_id']['type'], 'duplicate_values')
    
    def test_negative_price(self):
        """测试负价格"""
        # 创建测试数据
        data = {
            'item_id': ['ITEM001', 'ITEM002'],
            'product_name': ['产品A', '产品B'],
            'standard_unit_price': [99.99, -10.5]
        }
        df = pd.DataFrame(data)
        
        # 测试验证
        result = self.spec_manager.validate_mapped_dataframe(df)
        
        # 验证结果 - 应该有效但有警告
        self.assertTrue(result['valid'])
        self.assertIn('warnings', result)
        self.assertTrue(any('standard_unit_price列包含负值' in warning for warning in result['warnings']))
        self.assertIn('data_errors', result)
        self.assertIn('standard_unit_price', result['data_errors'])
        self.assertEqual(result['data_errors']['standard_unit_price']['type'], 'negative_values')

class TestCorrectionSuggestions(unittest.TestCase):
    """测试修改建议功能"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.spec_manager = EnhancedProductSpecManager()
    
    def test_suggest_corrections_for_missing_columns(self):
        """测试缺少列的修改建议"""
        # 创建测试数据
        data = {
            'item_id': ['ITEM001', 'ITEM002'],
            'product_name': ['产品A', '产品B']
        }
        df = pd.DataFrame(data)
        
        # 获取验证结果
        validation_result = self.spec_manager.validate_mapped_dataframe(df)
        
        # 生成修改建议
        suggestions = self.spec_manager.suggest_corrections(df, validation_result)
        
        # 验证结果
        self.assertIn('missing_columns', suggestions)
        self.assertIn('column_template', suggestions)
        self.assertIn('standard_unit_price', suggestions['column_template']['template'])
    
    def test_suggest_corrections_for_data_errors(self):
        """测试数据错误的修改建议"""
        # 创建测试数据
        data = {
            'item_id': ['ITEM001', None],
            'product_name': ['产品A', '产品B'],
            'standard_unit_price': [99.99, '非数字']
        }
        df = pd.DataFrame(data)
        
        # 获取验证结果
        validation_result = self.spec_manager.validate_mapped_dataframe(df)
        
        # 生成修改建议
        suggestions = self.spec_manager.suggest_corrections(df, validation_result)
        
        # 验证结果
        self.assertIn('item_id_null', suggestions)
        self.assertEqual(suggestions['item_id_null']['rows'], [2])
        
        self.assertIn('price_invalid', suggestions)
        self.assertEqual(suggestions['price_invalid']['rows'], [2])
        self.assertEqual(suggestions['price_invalid']['values'], ['非数字'])

if __name__ == '__main__':
    unittest.main()
cl
ass TestEnhancedValidationLogic(unittest.TestCase):
    """测试增强的验证逻辑"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.spec_manager = EnhancedProductSpecManager()
    
    def test_validate_with_all_columns(self):
        """测试包含所有列的验证"""
        # 创建包含所有必需和可选列的测试数据
        data = {
            'item_id': ['ITEM001', 'ITEM002', 'ITEM003'],
            'product_name': ['产品A', '产品B', '产品C'],
            'size': ['M', 'L', 'XL'],
            'color': ['红色', '蓝色', '绿色'],
            'standard_unit_price': [99.99, 129.99, 159.99]
        }
        df = pd.DataFrame(data)
        
        # 测试验证
        result = self.spec_manager.validate_mapped_dataframe(df)
        
        # 验证结果
        self.assertTrue(result['valid'])
        self.assertEqual(result['record_count'], 3)
        self.assertEqual(len(result['columns']), 5)
        self.assertNotIn('warnings', result)
        self.assertNotIn('data_errors', result)
    
    def test_validate_with_mixed_data_types(self):
        """测试混合数据类型的验证"""
        # 创建包含不同数据类型的测试数据
        data = {
            'item_id': ['ITEM001', 'ITEM002', 'ITEM003'],
            'product_name': ['产品A', '产品B', '产品C'],
            'standard_unit_price': [99.99, 129, '159.99']  # 混合数字和字符串
        }
        df = pd.DataFrame(data)
        
        # 测试验证
        result = self.spec_manager.validate_mapped_dataframe(df)
        
        # 验证结果 - 应该有效，因为字符串数字可以转换
        self.assertTrue(result['valid'])
        self.assertEqual(result['record_count'], 3)
    
    def test_validate_with_empty_dataframe(self):
        """测试空DataFrame的验证"""
        # 创建空DataFrame
        df = pd.DataFrame()
        
        # 测试验证
        result = self.spec_manager.validate_mapped_dataframe(df)
        
        # 验证结果
        self.assertFalse(result['valid'])
        self.assertIn('缺少必需的列', result['error'])
    
    def test_validate_with_zero_price(self):
        """测试零价格的验证"""
        # 创建包含零价格的测试数据
        data = {
            'item_id': ['ITEM001', 'ITEM002'],
            'product_name': ['产品A', '产品B'],
            'standard_unit_price': [0.0, 129.99]
        }
        df = pd.DataFrame(data)
        
        # 测试验证
        result = self.spec_manager.validate_mapped_dataframe(df)
        
        # 验证结果 - 应该有效，零价格是允许的
        self.assertTrue(result['valid'])
        self.assertEqual(result['record_count'], 2)
    
    def test_validate_with_large_dataset(self):
        """测试大数据集的验证"""
        # 创建大数据集
        size = 1000
        data = {
            'item_id': [f'ITEM{i:04d}' for i in range(1, size + 1)],
            'product_name': [f'产品{i}' for i in range(1, size + 1)],
            'standard_unit_price': [99.99 + i for i in range(size)]
        }
        df = pd.DataFrame(data)
        
        # 测试验证
        result = self.spec_manager.validate_mapped_dataframe(df)
        
        # 验证结果
        self.assertTrue(result['valid'])
        self.assertEqual(result['record_count'], size)
    
    def test_validate_with_unicode_characters(self):
        """测试包含Unicode字符的验证"""
        # 创建包含Unicode字符的测试数据
        data = {
            'item_id': ['ITEM001', 'ITEM002', 'ITEM003'],
            'product_name': ['产品A 🎯', '产品B ★', '产品C ♦'],
            'standard_unit_price': [99.99, 129.99, 159.99]
        }
        df = pd.DataFrame(data)
        
        # 测试验证
        result = self.spec_manager.validate_mapped_dataframe(df)
        
        # 验证结果
        self.assertTrue(result['valid'])
        self.assertEqual(result['record_count'], 3)
    
    def test_validate_with_special_characters_in_item_id(self):
        """测试item_id中包含特殊字符的验证"""
        # 创建包含特殊字符的测试数据
        data = {
            'item_id': ['ITEM-001', 'ITEM_002', 'ITEM.003'],
            'product_name': ['产品A', '产品B', '产品C'],
            'standard_unit_price': [99.99, 129.99, 159.99]
        }
        df = pd.DataFrame(data)
        
        # 测试验证
        result = self.spec_manager.validate_mapped_dataframe(df)
        
        # 验证结果
        self.assertTrue(result['valid'])
        self.assertEqual(result['record_count'], 3)

class TestSuggestionGeneration(unittest.TestCase):
    """测试建议生成功能"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.spec_manager = EnhancedProductSpecManager()
    
    def test_suggest_corrections_for_null_item_id(self):
        """测试为空item_id生成建议"""
        # 创建包含空item_id的测试数据
        data = {
            'item_id': ['ITEM001', None, 'ITEM003'],
            'product_name': ['产品A', '产品B', '产品C'],
            'standard_unit_price': [99.99, 129.99, 159.99]
        }
        df = pd.DataFrame(data)
        
        # 获取验证结果
        validation_result = self.spec_manager.validate_mapped_dataframe(df)
        
        # 生成修改建议
        suggestions = self.spec_manager.suggest_corrections(df, validation_result)
        
        # 验证结果
        self.assertIn('item_id_null', suggestions)
        self.assertEqual(suggestions['item_id_null']['rows'], [3])  # 第3行（索引2）
        self.assertIn('suggested_values', suggestions['item_id_null'])
        self.assertEqual(len(suggestions['item_id_null']['suggested_values']), 1)
    
    def test_suggest_corrections_for_duplicate_item_id(self):
        """测试为重复item_id生成建议"""
        # 创建包含重复item_id的测试数据
        data = {
            'item_id': ['ITEM001', 'ITEM001', 'ITEM003'],
            'product_name': ['产品A', '产品B', '产品C'],
            'standard_unit_price': [99.99, 129.99, 159.99]
        }
        df = pd.DataFrame(data)
        
        # 获取验证结果
        validation_result = self.spec_manager.validate_mapped_dataframe(df)
        
        # 生成修改建议
        suggestions = self.spec_manager.suggest_corrections(df, validation_result)
        
        # 验证结果
        self.assertIn('item_id_duplicate', suggestions)
        self.assertEqual(suggestions['item_id_duplicate']['rows'], [3])  # 第3行（索引1）
        self.assertEqual(suggestions['item_id_duplicate']['values'], ['ITEM001'])
        self.assertIn('suggested_values', suggestions['item_id_duplicate'])
    
    def test_suggest_corrections_for_invalid_price(self):
        """测试为无效价格生成建议"""
        # 创建包含无效价格的测试数据
        data = {
            'item_id': ['ITEM001', 'ITEM002', 'ITEM003'],
            'product_name': ['产品A', '产品B', '产品C'],
            'standard_unit_price': [99.99, '无效价格', 159.99]
        }
        df = pd.DataFrame(data)
        
        # 获取验证结果
        validation_result = self.spec_manager.validate_mapped_dataframe(df)
        
        # 生成修改建议
        suggestions = self.spec_manager.suggest_corrections(df, validation_result)
        
        # 验证结果
        self.assertIn('price_invalid', suggestions)
        self.assertEqual(suggestions['price_invalid']['rows'], [3])  # 第3行（索引1）
        self.assertEqual(suggestions['price_invalid']['values'], ['无效价格'])

if __name__ == '__main__':
    unittest.main()