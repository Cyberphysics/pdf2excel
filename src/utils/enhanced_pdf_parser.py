#!/usr/bin/env python3
"""
增强的PDF解析器 - 提取PDF的三个部分：客户信息、订单表格、总结信息
"""
import os
import re
import logging
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np

# PDF文本提取库
try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    from pdfminer.high_level import extract_text
    HAS_PDFMINER = True
except ImportError:
    HAS_PDFMINER = False

# 表格提取库
try:
    import camelot
    HAS_CAMELOT = True
except ImportError:
    HAS_CAMELOT = False

try:
    import tabula
    HAS_TABULA = True
except ImportError:
    HAS_TABULA = False

logger = logging.getLogger(__name__)

class EnhancedPDFParser:
    """增强的PDF解析器"""
    
    def __init__(self):
        """初始化解析器"""
        self.available_libraries = self._check_available_libraries()
        logger.info(f"Available PDF libraries: {self.available_libraries}")
    
    def _check_available_libraries(self) -> Dict[str, bool]:
        """检查可用的PDF处理库"""
        return {
            'pypdf2': HAS_PYPDF2,
            'pdfplumber': HAS_PDFPLUMBER,
            'pdfminer': HAS_PDFMINER,
            'camelot': HAS_CAMELOT,
            'tabula': HAS_TABULA
        }
    
    def extract_pdf_content(self, pdf_path: str) -> Dict[str, Any]:
        """
        提取PDF的完整内容，包括三个部分
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            包含三个部分的字典
        """
        try:
            # 1. 提取全文本
            full_text = self._extract_full_text(pdf_path)
            
            # 2. 提取表格
            tables = self._extract_tables(pdf_path)
            
            # 3. 分析PDF结构
            structure = self._analyze_pdf_structure(full_text, tables)
            
            # 4. 分离三个部分
            sections = self._separate_sections(full_text, tables, structure)
            
            return {
                'success': True,
                'sections': sections,
                'full_text': full_text,
                'tables': tables,
                'structure': structure,
                'library_info': self.available_libraries
            }
            
        except Exception as e:
            logger.error(f"PDF content extraction failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'library_info': self.available_libraries
            }
    
    def _extract_full_text(self, pdf_path: str) -> str:
        """提取PDF的全部文本内容"""
        text = ""
        
        # 尝试使用pdfplumber（推荐）
        if HAS_PDFPLUMBER:
            try:
                import pdfplumber
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n\n"
                if text.strip():
                    logger.info("Successfully extracted text using pdfplumber")
                    return text.strip()
            except Exception as e:
                logger.warning(f"pdfplumber text extraction failed: {e}")
        
        # 尝试使用pdfminer
        if HAS_PDFMINER:
            try:
                from pdfminer.high_level import extract_text
                text = extract_text(pdf_path)
                if text.strip():
                    logger.info("Successfully extracted text using pdfminer")
                    return text.strip()
            except Exception as e:
                logger.warning(f"pdfminer text extraction failed: {e}")
        
        # 尝试使用PyPDF2
        if HAS_PYPDF2:
            try:
                import PyPDF2
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n\n"
                if text.strip():
                    logger.info("Successfully extracted text using PyPDF2")
                    return text.strip()
            except Exception as e:
                logger.warning(f"PyPDF2 text extraction failed: {e}")
        
        logger.error("All text extraction methods failed")
        return ""
    
    def _extract_tables(self, pdf_path: str) -> List[Dict[str, Any]]:
        """提取PDF中的表格"""
        tables = []
        
        # 尝试使用Camelot
        if HAS_CAMELOT:
            try:
                import camelot
                # 尝试lattice模式
                camelot_tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
                if len(camelot_tables) == 0:
                    # 尝试stream模式
                    camelot_tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')
                
                for i, table in enumerate(camelot_tables):
                    df = table.df
                    if not df.empty:
                        df = df.dropna(how='all').dropna(axis=1, how='all')
                        if not df.empty:
                            accuracy = table.accuracy if hasattr(table, 'accuracy') else 80.0
                            if accuracy > 1:
                                accuracy = accuracy / 100.0
                            
                            tables.append({
                                'table_index': i + 1,
                                'page': table.page,
                                'data': df,
                                'accuracy': accuracy,
                                'method': 'camelot'
                            })
                
                if tables:
                    logger.info(f"Successfully extracted {len(tables)} tables using Camelot")
                    return tables
                    
            except Exception as e:
                logger.warning(f"Camelot table extraction failed: {e}")
        
        # 尝试使用Tabula
        if HAS_TABULA:
            try:
                import tabula
                tabula_tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True, pandas_options={'header': None})
                
                for i, df in enumerate(tabula_tables):
                    if not df.empty:
                        df = df.dropna(how='all').dropna(axis=1, how='all')
                        if not df.empty:
                            tables.append({
                                'table_index': i + 1,
                                'page': i + 1,
                                'data': df,
                                'accuracy': 0.8,  # 默认准确率
                                'method': 'tabula'
                            })
                
                if tables:
                    logger.info(f"Successfully extracted {len(tables)} tables using Tabula")
                    return tables
                    
            except Exception as e:
                logger.warning(f"Tabula table extraction failed: {e}")
        
        logger.warning("No tables extracted from PDF")
        return tables
    
    def _analyze_pdf_structure(self, full_text: str, tables: List[Dict]) -> Dict[str, Any]:
        """分析PDF结构，识别三个部分的边界"""
        structure = {
            'has_customer_info': False,
            'has_order_tables': len(tables) > 0,
            'has_summary': False,
            'customer_info_keywords': [],
            'summary_keywords': [],
            'estimated_sections': 1
        }
        
        if not full_text:
            return structure
        
        # 客户信息关键词
        customer_keywords = [
            'invoice to', 'bill to', 'ship to', 'customer', 'address',
            'invoice', 'order', 'purchase order', 'po', 'date',
            '发票', '客户', '地址', '订单', '采购订单'
        ]
        
        # 总结信息关键词
        summary_keywords = [
            'total', 'subtotal', 'tax', 'discount', 'grand total',
            'net amount', 'final amount', 'payment', 'terms',
            '总计', '小计', '税费', '折扣', '总金额', '支付'
        ]
        
        text_lower = full_text.lower()
        
        # 检查客户信息
        found_customer_keywords = []
        for keyword in customer_keywords:
            if keyword.lower() in text_lower:
                found_customer_keywords.append(keyword)
        
        if found_customer_keywords:
            structure['has_customer_info'] = True
            structure['customer_info_keywords'] = found_customer_keywords
        
        # 检查总结信息
        found_summary_keywords = []
        for keyword in summary_keywords:
            if keyword.lower() in text_lower:
                found_summary_keywords.append(keyword)
        
        if found_summary_keywords:
            structure['has_summary'] = True
            structure['summary_keywords'] = found_summary_keywords
        
        # 估算部分数量
        sections = 0
        if structure['has_customer_info']:
            sections += 1
        if structure['has_order_tables']:
            sections += 1
        if structure['has_summary']:
            sections += 1
        
        structure['estimated_sections'] = sections
        
        return structure
    
    def _separate_sections(self, full_text: str, tables: List[Dict], structure: Dict) -> Dict[str, Any]:
        """分离PDF的三个部分"""
        sections = {
            'customer_info': {
                'content': '',
                'data': {},
                'found': False
            },
            'order_tables': {
                'content': '',
                'data': tables,
                'found': len(tables) > 0
            },
            'summary': {
                'content': '',
                'data': {},
                'found': False
            }
        }
        
        if not full_text:
            return sections
        
        # 分割文本为段落
        paragraphs = [p.strip() for p in full_text.split('\n\n') if p.strip()]
        
        # 简单的启发式分离方法
        customer_info_text = []
        summary_text = []
        
        # 查找客户信息（通常在开头）
        if structure['has_customer_info']:
            for i, paragraph in enumerate(paragraphs[:5]):  # 检查前5段
                paragraph_lower = paragraph.lower()
                if any(keyword in paragraph_lower for keyword in structure['customer_info_keywords']):
                    customer_info_text.extend(paragraphs[:i+3])  # 包含相关段落
                    break
        
        # 查找总结信息（通常在结尾）
        if structure['has_summary']:
            for i, paragraph in enumerate(reversed(paragraphs[-5:])):  # 检查后5段
                paragraph_lower = paragraph.lower()
                if any(keyword in paragraph_lower for keyword in structure['summary_keywords']):
                    summary_text.extend(paragraphs[-(i+3):])  # 包含相关段落
                    break
        
        # 更新sections
        if customer_info_text:
            sections['customer_info']['content'] = '\n\n'.join(customer_info_text)
            sections['customer_info']['found'] = True
            sections['customer_info']['data'] = self._parse_customer_info(sections['customer_info']['content'])
        
        if summary_text:
            sections['summary']['content'] = '\n\n'.join(summary_text)
            sections['summary']['found'] = True
            sections['summary']['data'] = self._parse_summary_info(sections['summary']['content'])
        
        return sections
    
    def _parse_customer_info(self, text: str) -> Dict[str, Any]:
        """解析客户信息"""
        info = {}
        
        # 提取常见信息
        patterns = {
            'invoice_number': r'invoice\s*(?:no|number|#)?\s*:?\s*([A-Z0-9-]+)',
            'order_number': r'(?:purchase\s*)?order\s*(?:no|number|#)?\s*:?\s*([A-Z0-9-]+)',
            'date': r'date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            'customer_name': r'(?:bill\s*to|customer)\s*:?\s*([^\n]+)',
        }
        
        text_lower = text.lower()
        for key, pattern in patterns.items():
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                info[key] = match.group(1).strip()
        
        return info
    
    def _parse_summary_info(self, text: str) -> Dict[str, Any]:
        """解析总结信息"""
        info = {}
        
        # 提取金额信息
        patterns = {
            'subtotal': r'subtotal\s*:?\s*([0-9,]+\.?\d*)',
            'tax': r'tax\s*:?\s*([0-9,]+\.?\d*)',
            'total': r'(?:grand\s*)?total\s*:?\s*([0-9,]+\.?\d*)',
            'discount': r'discount\s*:?\s*([0-9,]+\.?\d*)',
        }
        
        text_lower = text.lower()
        for key, pattern in patterns.items():
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    info[key] = float(amount_str)
                except ValueError:
                    info[key] = amount_str
        
        return info
    
    def create_multi_sheet_excel(self, sections: Dict[str, Any], output_path: str) -> bool:
        """创建包含三个工作表的Excel文件"""
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                
                # 1. Customer_Info 工作表
                if sections['customer_info']['found']:
                    customer_df = pd.DataFrame([sections['customer_info']['data']])
                    if not customer_df.empty:
                        customer_df.to_excel(writer, sheet_name='Customer_Info', index=False)
                
                # 2. Order_Items 工作表
                if sections['order_tables']['found'] and sections['order_tables']['data']:
                    # 合并所有表格
                    all_tables = []
                    for table_info in sections['order_tables']['data']:
                        df = table_info['data']
                        if not df.empty:
                            all_tables.append(df)
                    
                    if all_tables:
                        combined_df = pd.concat(all_tables, ignore_index=True)
                        combined_df.to_excel(writer, sheet_name='Order_Items', index=False)
                
                # 3. Summary 工作表
                if sections['summary']['found']:
                    summary_df = pd.DataFrame([sections['summary']['data']])
                    if not summary_df.empty:
                        summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # 如果没有找到任何结构化数据，至少创建一个工作表
                if not any(sections[key]['found'] for key in sections):
                    empty_df = pd.DataFrame({'Message': ['No structured data found in PDF']})
                    empty_df.to_excel(writer, sheet_name='Data', index=False)
            
            logger.info(f"Successfully created multi-sheet Excel: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create multi-sheet Excel: {e}")
            return False

# 全局实例
_enhanced_parser = None

def get_enhanced_parser() -> EnhancedPDFParser:
    """获取增强PDF解析器实例"""
    global _enhanced_parser
    if _enhanced_parser is None:
        _enhanced_parser = EnhancedPDFParser()
    return _enhanced_parser