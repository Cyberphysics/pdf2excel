from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
import os
import uuid
import pandas as pd
import numpy as np
# Optional PDF table extraction libraries
try:
    import camelot
    CAMELOT_AVAILABLE = True
except ImportError:
    CAMELOT_AVAILABLE = False
    camelot = None

try:
    import tabula
    TABULA_AVAILABLE = True
except ImportError:
    TABULA_AVAILABLE = False
    tabula = None
from datetime import datetime
import traceback
import json
import math
import re
from ..utils.json_utils import safe_jsonify, prepare_preview_data, prepare_sheet_data
from ..utils.path_manager import get_path_manager
from ..utils.enhanced_pdf_parser import get_enhanced_parser

pdf_converter_bp = Blueprint('pdf_converter', __name__)

# 配置
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_upload_output_paths():
    """获取上传和输出目录路径"""
    path_manager = get_path_manager()
    return path_manager.config.uploads_dir, path_manager.config.outputs_dir

def merge_split_rows(df):
    """
    智能合并被分割的行，特别是DESCRIPTION字段
    标准表头：ITEM, EXTERNAL ITEM, DESCRIPTION, DELIVERY, UNIT, QUANTITY, PRICE, AMOUNT
    """
    if df.empty:
        return df
    
    # 创建副本避免修改原数据
    df = df.copy()
    df = df.reset_index(drop=True)
    
    # 1. 标准化列名
    df = standardize_column_names(df)
    
    # 2. 识别并合并分割的行
    df = merge_description_rows(df)
    
    # 3. 清理和验证数据
    df = clean_merged_data(df)
    
    return df

def normalize_field_name(field_name):
    """标准化字段名，处理换行和空格"""
    if pd.isna(field_name):
        return ''
    
    # 转换为字符串并清理
    field_str = str(field_name).strip()
    
    # 移除换行符并用空格替换
    field_str = re.sub(r'\s*\n\s*', ' ', field_str)
    
    # 标准化空格
    field_str = re.sub(r'\s+', ' ', field_str)
    
    # 转换为大写
    field_str = field_str.upper()
    
    return field_str

def handle_multiline_headers(df):
    """处理多行表头的情况"""
    if len(df) < 2:
        return df
    
    # 表头关键词
    header_keywords = ['ITEM', 'EXTERNAL', 'NUMBER', 'DESCRIPTION', 'DELIVERY', 'DATE', 'UNIT', 'QUANTITY', 'QTY', 'PRICE', 'AMOUNT']
    
    # 检查每一行是否看起来像表头行
    header_rows = []
    for row_idx in range(min(3, len(df))):
        row_data = df.iloc[row_idx]
        header_like_cells = 0
        total_non_empty_cells = 0
        
        for cell_value in row_data:
            if pd.notna(cell_value) and str(cell_value).strip():
                total_non_empty_cells += 1
                cell_str = str(cell_value).strip().upper()
                
                # 检查是否包含表头关键词
                if any(keyword in cell_str for keyword in header_keywords):
                    header_like_cells += 1
                # 或者是否看起来像表头（全是字母，不包含数字和特殊字符）
                elif re.match(r'^[A-Za-z\s]+$', cell_str) and len(cell_str) > 2:
                    header_like_cells += 1
        
        # 如果大部分非空单元格都像表头，则认为这是表头行
        if total_non_empty_cells > 0 and header_like_cells / total_non_empty_cells >= 0.6:
            header_rows.append(row_idx)
        else:
            break  # 遇到数据行就停止
    
    if not header_rows:
        return df  # 没有找到多行表头
    
    # 合并表头行
    combined_headers = []
    for col_idx in range(len(df.columns)):
        header_parts = []
        
        # 从识别的表头行中收集表头信息
        for row_idx in header_rows:
            cell_value = df.iloc[row_idx, col_idx]
            if pd.notna(cell_value) and str(cell_value).strip():
                cell_str = str(cell_value).strip()
                header_parts.append(cell_str)
        
        # 合并表头部分
        if header_parts:
            combined_header = normalize_field_name(' '.join(header_parts))
            combined_headers.append(combined_header)
        else:
            # 如果没有找到表头信息，使用原始列名
            combined_headers.append(normalize_field_name(str(df.columns[col_idx])))
    
    # 更新列名
    df.columns = combined_headers
    
    # 移除表头行
    if header_rows:
        df = df.iloc[max(header_rows) + 1:].reset_index(drop=True)
    
    return df

def standardize_column_names(df):
    """标准化列名，确保符合预期格式"""
    # 标准列名映射 - 更新为正确的8个字段
    standard_column_order = ['ITEM', 'EXTERNAL ITEM NUMBER', 'DESCRIPTION', 'DELIVERY DATE', 'UNIT', 'QUANTITY', 'PRICE', 'AMOUNT']
    
    # 检查是否需要处理表头（第一行是否包含列名关键词且当前列名是数字索引）
    current_columns_are_numeric = all(str(col).isdigit() or str(col).startswith('col_') for col in df.columns)
    
    # 首先处理多行表头
    if not current_columns_are_numeric:
        df = handle_multiline_headers(df)
    
    if len(df) > 0:
        first_row_str = ' '.join(str(cell).upper() for cell in df.iloc[0] if pd.notna(cell))
        has_header_in_data = any(keyword in first_row_str for keyword in ['DESCRIPTION', 'ITEM', 'QTY', 'PRICE', 'AMOUNT'])
        
        # 如果当前列名是数字索引且第一行包含表头信息，使用第一行作为列名
        if current_columns_are_numeric and has_header_in_data:
            new_columns = []
            header_row = df.iloc[0]
            for col_val in header_row:
                if pd.notna(col_val) and str(col_val).strip():
                    new_columns.append(str(col_val).strip().upper())
                else:
                    new_columns.append(f'Column_{len(new_columns)}')
            
            # 更新列名
            df.columns = new_columns[:len(df.columns)]
            # 删除表头行
            df = df.drop(0).reset_index(drop=True)
            # 处理可能的多行表头
            df = handle_multiline_headers(df)
    
    # 如果是数字列名（col_0, col_1等），按位置映射到标准列名
    if current_columns_are_numeric:
        new_column_mapping = {}
        for i, col in enumerate(df.columns):
            if i < len(standard_column_order):
                new_column_mapping[col] = standard_column_order[i]
            else:
                new_column_mapping[col] = f'Column_{i}'
        
        df = df.rename(columns=new_column_mapping)
        return df
    
    # 如果已经有合理的列名，尝试标准化
    standard_columns = {
        'ITEM': ['item', 'item_code', 'code', '项目', '编号', 'part', 'part_no'],
        'EXTERNAL ITEM NUMBER': [
            'external_item_number', 'external_item', 'ext_item', 'supplier_code', 'vendor_code',
            'external item number', 'external item', 'ext item number'
        ],
        'DESCRIPTION': ['description', 'desc', 'product', 'name', '描述', '产品名称', 'product_name'],
        'DELIVERY DATE': [
            'delivery_date', 'delivery', 'due_date', 'ship_date',
            'delivery date'
        ],
        'UNIT': ['unit', 'uom', 'measure', '单位', 'units'],
        'QUANTITY': ['quantity', 'qty', 'amount', '数量', 'qnty'],
        'PRICE': ['price', 'unit_price', 'cost', '单价', '价格', 'rate'],
        'AMOUNT': ['amount', 'total', 'total_price', '总价', '金额', 'total_amount']
    }
    
    # 创建列名映射字典
    column_mapping = {}
    for col in df.columns:
        col_normalized = normalize_field_name(col)
        
        # 直接匹配标准字段名
        if col_normalized in standard_columns:
            continue
        
        # 模糊匹配
        for standard_col, aliases in standard_columns.items():
            for alias in aliases:
                if normalize_field_name(alias) == col_normalized:
                    column_mapping[col] = standard_col
                    break
            if col in column_mapping:
                break
    
    # 应用列名映射
    if column_mapping:
        df = df.rename(columns=column_mapping)
    
    return df

def merge_description_rows(df):
    """合并被分割的DESCRIPTION行"""
    if 'DESCRIPTION' not in df.columns or len(df) < 2:
        return df
    
    # 识别主要数据行和描述续行
    main_rows = []
    current_main_row = None
    
    for idx, row in df.iterrows():
        if is_main_data_row(row):
            # 如果有之前的主行，先保存
            if current_main_row is not None:
                main_rows.append(current_main_row)
            # 开始新的主行
            current_main_row = row.copy()
        else:
            # 这是一个描述续行
            if current_main_row is not None:
                # 合并描述信息
                current_main_row = merge_description_content(current_main_row, row)
    
    # 添加最后一个主行
    if current_main_row is not None:
        main_rows.append(current_main_row)
    
    if main_rows:
        merged_df = pd.DataFrame(main_rows).reset_index(drop=True)
        return merged_df
    else:
        return df

def is_main_data_row(row):
    """判断是否为主要数据行（包含完整的订单信息）"""
    # 检查关键字段是否有值
    has_item = not pd.isna(row.get('ITEM', np.nan)) and str(row.get('ITEM', '')).strip() != ''
    has_quantity = not pd.isna(row.get('QUANTITY', np.nan)) and str(row.get('QUANTITY', '')).strip() != ''
    has_price = not pd.isna(row.get('PRICE', np.nan)) and str(row.get('PRICE', '')).strip() != ''
    
    # 主要数据行的判断条件：至少要有ITEM和QUANTITY或PRICE中的一个
    if has_item and (has_quantity or has_price):
        return True
    
    # 检查是否有数字特征（价格、数量等）
    numeric_fields = 0
    for field in ['QUANTITY', 'PRICE', 'AMOUNT']:
        if field in row:
            try:
                val = str(row[field]).replace(',', '').strip()
                if val and val != 'nan':
                    float(val)
                    numeric_fields += 1
            except (ValueError, TypeError):
                pass
    
    return numeric_fields >= 2  # 至少有两个数字字段

def merge_description_content(main_row, continuation_row):
    """合并描述内容"""
    # 合并DESCRIPTION字段
    main_desc = str(main_row.get('DESCRIPTION', '')).strip()
    cont_desc = str(continuation_row.get('DESCRIPTION', '')).strip()
    
    if cont_desc and cont_desc != 'nan':
        if main_desc and main_desc != 'nan':
            # 智能合并：检查是否需要添加分隔符
            if main_desc.endswith(('-', '|', ',')):
                main_row['DESCRIPTION'] = main_desc + ' ' + cont_desc
            else:
                main_row['DESCRIPTION'] = main_desc + ' | ' + cont_desc
        else:
            main_row['DESCRIPTION'] = cont_desc
    
    # 检查其他字段是否有补充信息
    for col in continuation_row.index:
        if col != 'DESCRIPTION':
            cont_val = str(continuation_row[col]).strip()
            main_val = str(main_row.get(col, '')).strip()
            # 如果主行该字段为空，但续行有值，则使用续行的值
            if cont_val and cont_val != 'nan' and (not main_val or main_val == 'nan'):
                main_row[col] = continuation_row[col]
    
    return main_row

def clean_merged_data(df):
    """清理合并后的数据"""
    # 清理DESCRIPTION字段
    if 'DESCRIPTION' in df.columns:
        df['DESCRIPTION'] = df['DESCRIPTION'].apply(clean_description_text)
    
    # 标准化数字字段
    numeric_fields = ['QUANTITY', 'PRICE', 'AMOUNT']
    for field in numeric_fields:
        if field in df.columns:
            df[field] = df[field].apply(clean_numeric_value)
    
    # 移除完全空的行
    df = df.dropna(how='all').reset_index(drop=True)
    
    return df

def clean_description_text(text):
    """清理描述文本"""
    if pd.isna(text):
        return ''
    text = str(text).strip()
    # 移除多余的分隔符
    import re
    text = re.sub(r'\s*\|\s*\|\s*', ' | ', text)  # 合并重复的分隔符
    text = re.sub(r'\s+', ' ', text)  # 合并多个空格
    text = text.strip(' |')  # 移除首尾的分隔符
    return text

def clean_numeric_value(value):
    """清理数字值"""
    if pd.isna(value):
        return np.nan
    try:
        import re
        # 移除逗号和其他非数字字符（保留小数点和负号）
        cleaned = re.sub(r'[^\d.-]', '', str(value))
        if cleaned:
            return float(cleaned)
    except (ValueError, TypeError):
        pass
    return np.nan

def extract_tables_with_camelot(pdf_path):
    """使用Camelot提取PDF表格"""
    if not CAMELOT_AVAILABLE:
        return None, "Camelot库未安装，这是可选依赖"
    
    try:
        # 首先尝试lattice模式
        tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
        if len(tables) == 0:
            # 如果lattice模式没有找到表格，尝试stream模式
            tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')
        
        extracted_data = []
        for i, table in enumerate(tables):
            df = table.df
            # 清理数据：移除空行和空列
            df = df.dropna(how='all').dropna(axis=1, how='all')
            if not df.empty:
                # 应用行合并逻辑
                df = merge_split_rows(df)
                # 处理准确率：Camelot返回的accuracy可能是0-100的数值，需要标准化为0-1
                accuracy = table.accuracy if hasattr(table, 'accuracy') else 80.0
                if accuracy > 1:
                    accuracy = accuracy / 100.0  # 转换为0-1之间的小数
                
                extracted_data.append({
                    'table_index': i + 1,
                    'page': table.page,
                    'data': df,
                    'accuracy': accuracy
                })
        
        return extracted_data, None
    except Exception as e:
        print(f"Camelot提取失败: {str(e)}")
        return None, str(e)

def extract_tables_with_tabula(pdf_path):
    """使用Tabula作为备选方案提取PDF表格"""
    if not TABULA_AVAILABLE:
        return None, "Tabula库未安装，这是可选依赖"
    
    try:
        tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True, pandas_options={'header': None})
        extracted_data = []
        for i, df in enumerate(tables):
            if not df.empty:
                # 清理数据
                df = df.dropna(how='all').dropna(axis=1, how='all')
                if not df.empty:
                    # 应用行合并逻辑
                    df = merge_split_rows(df)
                    extracted_data.append({
                        'table_index': i + 1,
                        'page': i + 1,  # Tabula不提供页码信息，使用索引
                        'data': df,
                        'accuracy': 0.8  # 默认准确率
                    })
        
        return extracted_data, None
    except Exception as e:
        print(f"Tabula提取失败: {str(e)}")
        return None, str(e)

def convert_to_excel(extracted_data, output_path):
    """将提取的数据转换为Excel文件"""
    try:
        # 检查输入数据
        if not extracted_data or not isinstance(extracted_data, list):
            # 创建一个空的Excel文件，包含提示信息
            df_empty = pd.DataFrame({
                '提示': ['未能从PDF中提取到表格数据'],
                '说明': ['请检查PDF文件是否包含表格，或尝试其他PDF文件']
            })
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df_empty.to_excel(writer, sheet_name='提示信息', index=False)
            return True, "未提取到表格数据，已创建空文件"
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for table_info in extracted_data:
                if not isinstance(table_info, dict) or 'data' not in table_info:
                    continue
                    
                df = table_info['data']
                if df is None or df.empty:
                    continue
                    
                sheet_name = f"Table_{table_info.get('table_index', 1)}_Page_{table_info.get('page', 1)}"
                # Excel工作表名称长度限制
                if len(sheet_name) > 31:
                    sheet_name = f"Table_{table_info.get('table_index', 1)}"
                
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        return True, None
    except Exception as e:
        return False, str(e)

# 重复的函数定义已删除，使用下面更完整的版本

@pdf_converter_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return safe_jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'pdf-to-excel',
        'core_dependencies': {
            'pdfplumber': True,  # 核心依赖，应该始终可用
            'pandas': True,
            'openpyxl': True
        },
        'optional_dependencies': {
            'camelot': CAMELOT_AVAILABLE,
            'tabula': TABULA_AVAILABLE
        }
    })

@pdf_converter_bp.route('/upload', methods=['POST'])
def upload_file():
    """处理文件上传"""
    try:
        get_path_manager().ensure_directories()
        
        if 'file' not in request.files:
            return safe_jsonify({'error': '没有文件被上传'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return safe_jsonify({'error': '没有选择文件'}), 400
        
        if file and allowed_file(file.filename):
            # 生成唯一的文件名
            file_id = str(uuid.uuid4())
            filename = secure_filename(file.filename)
            file_extension = filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{file_id}.{file_extension}"
            
            upload_path, _ = get_upload_output_paths()
            file_path = os.path.join(upload_path, unique_filename)
            file.save(file_path)
            
            # 保存元数据，包括原始文件名
            metadata = {
                'original_filename': filename,
                'upload_time': datetime.now().isoformat(),
                'file_size': os.path.getsize(file_path)
            }
            
            metadata_path = os.path.join(upload_path, f"{file_id}.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False)
            
            return safe_jsonify({
                'message': '文件上传成功',
                'file_id': file_id,
                'original_filename': filename
            }), 200
        else:
            return safe_jsonify({'error': '不支持的文件类型，请上传PDF文件'}), 400
            
    except Exception as e:
        return safe_jsonify({'error': f'上传失败: {str(e)}'}), 500

@pdf_converter_bp.route('/convert/<file_id>', methods=['POST'])
def convert_pdf(file_id):
    """转换PDF为Excel"""
    try:
        upload_path, output_path = get_upload_output_paths()
        get_path_manager().ensure_directories()
        pdf_path = os.path.join(upload_path, f"{file_id}.pdf")
        
        if not os.path.exists(pdf_path):
            return safe_jsonify({'error': '文件不存在'}), 404
        
        # 使用增强的PDF解析器
        enhanced_parser = get_enhanced_parser()
        pdf_content = enhanced_parser.extract_pdf_content(pdf_path)
        
        if not pdf_content['success']:
            # 回退到原始方法
            extracted_data, error = extract_tables_with_camelot(pdf_path)
            if extracted_data is None or len(extracted_data) == 0:
                extracted_data, error = extract_tables_with_tabula(pdf_path)
            
            if extracted_data is None or len(extracted_data) == 0:
                return safe_jsonify({
                    'error': f'无法从PDF中提取数据。错误信息: {pdf_content.get("error", error or "未检测到内容")}'
                }), 400
        else:
            # 使用增强解析器的结果
            sections = pdf_content['sections']
            extracted_data = sections['order_tables']['data'] if sections['order_tables']['found'] else []
            
            # 如果没有找到表格，尝试原始方法作为备选
            if not extracted_data:
                extracted_data, error = extract_tables_with_camelot(pdf_path)
                if extracted_data is None or len(extracted_data) == 0:
                    extracted_data, error = extract_tables_with_tabula(pdf_path)
            
            # 存储完整的PDF内容信息以供后续使用
            pdf_sections = sections
        
        # 获取原始文件名
        original_filename = f"{file_id}.pdf"
        original_name_without_ext = file_id
        metadata_path = os.path.join(upload_path, f"{file_id}.json")
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    if 'original_filename' in metadata:
                        original_filename = metadata['original_filename']
                        original_name_without_ext = os.path.splitext(original_filename)[0]
            except Exception as e:
                current_app.logger.warning(f"读取元数据失败: {str(e)}")
        
        # 创建转换后文件的元数据
        converted_filename = f"{original_name_without_ext}.xlsx"
        
        # 生成Excel文件
        excel_filename = f"{file_id}.xlsx"
        excel_path = os.path.join(output_path, excel_filename)
        
        # 如果有完整的PDF结构信息，创建多工作表Excel
        if 'pdf_sections' in locals() and pdf_sections:
            success = enhanced_parser.create_multi_sheet_excel(pdf_sections, excel_path)
            if not success:
                # 回退到原始方法
                success, error = convert_to_excel(extracted_data, excel_path)
                if not success:
                    return safe_jsonify({'error': f'Excel生成失败: {error}'}), 500
        else:
            success, error = convert_to_excel(extracted_data, excel_path)
            if not success:
                return safe_jsonify({'error': f'Excel生成失败: {error}'}), 500
        
        # 创建转换后文件的元数据
        # 安全地计算记录数量
        record_count = 0
        if extracted_data and isinstance(extracted_data, list):
            try:
                record_count = sum(len(table.get('data', [])) if isinstance(table, dict) and 'data' in table else 0 for table in extracted_data)
            except Exception as e:
                current_app.logger.warning(f"计算记录数量失败: {str(e)}")
                record_count = 0
        
        converted_metadata = {
            'original_filename': original_filename,
            'filename': converted_filename,
            'convert_time': datetime.now().isoformat(),
            'file_size': os.path.getsize(excel_path),
            'record_count': record_count
        }
        
        # 保存元数据
        converted_metadata_path = os.path.join(output_path, f"{file_id}.json")
        with open(converted_metadata_path, 'w', encoding='utf-8') as f:
            json.dump(converted_metadata, f, ensure_ascii=False)
        
        # 使用统一的预览数据准备函数
        preview_data = prepare_preview_data(extracted_data, max_rows=10)
        
        # 安全地计算表格数量
        tables_count = len(extracted_data) if extracted_data and isinstance(extracted_data, list) else 0
        
        return safe_jsonify({
            'message': '转换成功',
            'file_id': file_id,
            'excel_filename': excel_filename,
            'filename': converted_filename,
            'tables_count': tables_count,
            'preview_data': preview_data
        }), 200
        
    except Exception as e:
        return safe_jsonify({'error': f'转换失败: {str(e)}'}), 500

@pdf_converter_bp.route('/download/<file_id>')
def download_file(file_id):
    """下载转换后的Excel文件"""
    try:
        _, output_path = get_upload_output_paths()
        get_path_manager().ensure_directories()
        excel_filename = f"{file_id}.xlsx"
        excel_path = os.path.join(output_path, excel_filename)
        
        if not os.path.exists(excel_path):
            return safe_jsonify({'error': '文件不存在'}), 404
        
        # 获取原始文件名
        metadata_path = os.path.join(output_path, f"{file_id}.json")
        download_name = f"converted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    if 'filename' in metadata:
                        download_name = metadata['filename']
            except Exception as e:
                current_app.logger.warning(f"读取元数据失败: {str(e)}")
        
        return send_file(
            excel_path,
            as_attachment=True,
            download_name=download_name,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        return safe_jsonify({'error': f'下载失败: {str(e)}'}), 500

@pdf_converter_bp.route('/preview/<file_id>')
def preview_file(file_id):
    """获取转换后文件的预览数据"""
    try:
        upload_path, _ = get_upload_output_paths()
        get_path_manager().ensure_directories()
        pdf_path = os.path.join(upload_path, f"{file_id}.pdf")
        
        if not os.path.exists(pdf_path):
            return safe_jsonify({'error': '文件不存在'}), 404
        
        # 重新提取数据用于预览
        extracted_data, error = extract_tables_with_camelot(pdf_path)
        if extracted_data is None or len(extracted_data) == 0:
            extracted_data, error = extract_tables_with_tabula(pdf_path)
        
        if extracted_data is None or len(extracted_data) == 0:
            return safe_jsonify({'error': '无法提取预览数据'}), 400
        
        # 使用统一的预览数据准备函数
        preview_data = prepare_preview_data(extracted_data, max_rows=20)
        
        return safe_jsonify({
            'file_id': file_id,
            'tables_count': len(extracted_data),
            'preview_data': preview_data
        }), 200
        
    except Exception as e:
        return safe_jsonify({'error': f'预览失败: {str(e)}'}), 500

@pdf_converter_bp.route('/status/<file_id>')
def get_status(file_id):
    """获取文件处理状态"""
    try:
        upload_path, output_path = get_upload_output_paths()
        get_path_manager().ensure_directories()
        pdf_path = os.path.join(upload_path, f"{file_id}.pdf")
        excel_path = os.path.join(output_path, f"{file_id}.xlsx")
        metadata_path = os.path.join(output_path, f"{file_id}.json")
        
        status = {
            'file_id': file_id,
            'pdf_exists': os.path.exists(pdf_path),
            'excel_exists': os.path.exists(excel_path),
            'metadata_exists': os.path.exists(metadata_path),
            'status': 'unknown'
        }
        
        # 如果元数据存在，读取文件名
        if status['metadata_exists']:
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    status['filename'] = metadata.get('filename', f"converted_{file_id}.xlsx")
                    status['original_filename'] = metadata.get('original_filename', '')
                    status['convert_time'] = metadata.get('convert_time', '')
            except Exception as e:
                current_app.logger.warning(f"读取元数据失败: {str(e)}")
        
        if not status['pdf_exists'] and not status['excel_exists']:
            status['status'] = 'not_found'
        elif status['excel_exists']:
            status['status'] = 'completed'
            # 添加文件大小信息
            if os.path.exists(excel_path):
                status['file_size'] = os.path.getsize(excel_path)
                status['file_time'] = os.path.getmtime(excel_path)
        else:
            status['status'] = 'uploaded'
        
        return safe_jsonify(status), 200
        
    except Exception as e:
        return safe_jsonify({'error': f'状态查询失败: {str(e)}'}), 500

@pdf_converter_bp.route('/list_converted', methods=['GET'])
def list_converted_files():
    """列出已转换的订单文件"""
    try:
        _, output_path = get_upload_output_paths()
        get_path_manager().ensure_directories()
        files = []
        
        # 获取所有JSON元数据文件
        metadata_files = [f for f in os.listdir(output_path) if f.endswith('.json') and not f.startswith('order_comparison_')]
        
        for metadata_file in metadata_files:
            file_id = metadata_file.rsplit('.', 1)[0]
            excel_file = f"{file_id}.xlsx"
            excel_path = os.path.join(output_path, excel_file)
            
            # 检查Excel文件是否存在
            file_exists = os.path.exists(excel_path)
            
            # 读取元数据
            metadata_path = os.path.join(output_path, metadata_file)
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    
                # 获取文件信息
                if file_exists:
                    file_size = os.path.getsize(excel_path)
                    file_time = os.path.getmtime(excel_path)
                else:
                    file_size = metadata.get('file_size', 0)
                    file_time = datetime.fromisoformat(metadata.get('convert_time', datetime.now().isoformat())).timestamp()
                
                # 使用元数据中的信息
                filename = metadata.get('filename', f"converted_{file_id}.xlsx")
                original_filename = metadata.get('original_filename', '')
                convert_time = metadata.get('convert_time', datetime.fromtimestamp(file_time).isoformat())
                record_count = metadata.get('record_count', 0)
                
                # 添加到文件列表
                files.append({
                    'file_id': file_id,
                    'filename': filename,
                    'original_filename': original_filename,
                    'file_size': file_size,
                    'convert_time': convert_time,
                    'record_count': record_count,
                    'exists': file_exists  # 文件是否存在
                })
            except Exception as e:
                current_app.logger.warning(f"读取元数据失败: {metadata_file}, 错误: {str(e)}")
                continue
        
        # 按时间倒序排序
        files.sort(key=lambda x: x['convert_time'], reverse=True)
        return safe_jsonify({'files': files}), 200
    except Exception as e:
        current_app.logger.error(f"获取文件列表失败: {str(e)}")
        return safe_jsonify({'error': f'获取文件列表失败: {str(e)}'}), 500
        
@pdf_converter_bp.route('/preview_converted/<file_id>', methods=['GET'])
def preview_converted(file_id):
    """预览已转换的Excel文件信息"""
    try:
        # 获取文件路径
        _, output_path = get_upload_output_paths()
        get_path_manager().ensure_directories()
        file_path = os.path.join(output_path, f"{file_id}.xlsx")
        if not os.path.exists(file_path):
            return safe_jsonify({'error': '文件不存在'}), 404
        
        # 获取文件元数据
        metadata_path = os.path.join(output_path, f"{file_id}.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        else:
            # 如果没有元数据，创建基本信息
            file_time = os.path.getmtime(file_path)
            metadata = {
                'filename': f"converted_{file_id}.xlsx",
                'convert_time': datetime.fromtimestamp(file_time).isoformat(),
                'file_size': os.path.getsize(file_path)
            }
        
        # 获取Excel工作表列表
        import pandas as pd
        xl = pd.ExcelFile(file_path)
        sheets = xl.sheet_names
        
        return safe_jsonify({
            'file_id': file_id,
            'filename': metadata.get('filename', f"converted_{file_id}.xlsx"),
            'convert_time': metadata.get('convert_time'),
            'file_size': os.path.getsize(file_path),
            'sheets': sheets
        }), 200
    except Exception as e:
        current_app.logger.error(f"预览转换文件失败: {str(e)}")
        return safe_jsonify({'error': '预览失败'}), 500

@pdf_converter_bp.route('/sheet_data/<file_id>', methods=['GET'])
def get_sheet_data(file_id):
    """获取Excel工作表数据（统一接口）"""
    try:
        sheet_name = request.args.get('sheet', 'Sheet1')
        
        # 获取文件路径
        _, output_path = get_upload_output_paths()
        get_path_manager().ensure_directories()
        file_path = os.path.join(output_path, f"{file_id}.xlsx")
        if not os.path.exists(file_path):
            return safe_jsonify({'error': '文件不存在'}), 404
        
        # 读取指定工作表数据
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # 使用统一的数据准备函数
        sheet_data = prepare_sheet_data(df, sheet_name)
        
        return safe_jsonify(sheet_data), 200
        
    except Exception as e:
        current_app.logger.error(f"获取工作表数据失败: {str(e)}")
        return safe_jsonify({'error': f'获取数据失败: {str(e)}'}), 500

@pdf_converter_bp.route('/download_converted/<file_id>', methods=['GET'])
def download_converted(file_id):
    """下载已转换的Excel文件"""
    try:
        # 获取文件路径
        _, output_path = get_upload_output_paths()
        get_path_manager().ensure_directories()
        file_path = os.path.join(output_path, f"{file_id}.xlsx")
        if not os.path.exists(file_path):
            return safe_jsonify({'error': '文件不存在'}), 404
        
        # 获取原始文件名
        metadata_path = os.path.join(output_path, f"{file_id}.json")
        download_name = f"converted_{file_id}.xlsx"
        
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    if 'filename' in metadata:
                        download_name = metadata['filename']
                    elif 'original_filename' in metadata:
                        # 如果没有filename但有original_filename，使用原始文件名的基础名称加上.xlsx
                        original_name = metadata['original_filename']
                        base_name = os.path.splitext(original_name)[0]
                        download_name = f"{base_name}.xlsx"
            except Exception as e:
                current_app.logger.warning(f"读取元数据失败: {str(e)}")
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=download_name,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        current_app.logger.error(f"下载转换文件失败: {str(e)}")
        return safe_jsonify({'error': '下载失败'}), 500

@pdf_converter_bp.route('/check_file_exists/<file_id>', methods=['GET'])
def check_file_exists(file_id):
    """检查文件是否存在"""
    try:
        _, output_path = get_upload_output_paths()
        get_path_manager().ensure_directories()
        file_path = os.path.join(output_path, f"{file_id}.xlsx")
        metadata_path = os.path.join(output_path, f"{file_id}.json")
        
        file_exists = os.path.exists(file_path)
        metadata_exists = os.path.exists(metadata_path)
        
        # 获取文件信息
        file_info = {
            'file_id': file_id,
            'exists': file_exists,
            'metadata_exists': metadata_exists
        }
        
        # 如果元数据存在，读取更多信息
        if metadata_exists:
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                file_info.update({
                    'filename': metadata.get('filename', f"converted_{file_id}.xlsx"),
                    'original_filename': metadata.get('original_filename', ''),
                    'convert_time': metadata.get('convert_time', ''),
                    'record_count': metadata.get('record_count', 0)
                })
            except Exception as e:
                current_app.logger.warning(f"读取元数据失败: {str(e)}")
        
        return safe_jsonify(file_info), 200
    except Exception as e:
        return safe_jsonify({'error': f'检查文件失败: {str(e)}'}), 500

@pdf_converter_bp.route('/delete_converted/<file_id>', methods=['DELETE'])
def delete_converted_file(file_id):
    """删除已转换的订单文件"""
    try:
        _, output_path = get_upload_output_paths()
        get_path_manager().ensure_directories()
        file_path = os.path.join(output_path, f"{file_id}.xlsx")
        metadata_path = os.path.join(output_path, f"{file_id}.json")
        
        # 检查文件是否存在
        file_exists = os.path.exists(file_path)
        metadata_exists = os.path.exists(metadata_path)
        
        if not file_exists and not metadata_exists:
            return safe_jsonify({'error': '文件不存在'}), 404
        
        # 删除Excel文件（如果存在）
        if file_exists:
            os.remove(file_path)
        
        # 删除元数据文件（如果存在）
        if metadata_exists:
            os.remove(metadata_path)
            
        return safe_jsonify({'message': '文件删除成功'}), 200
    except Exception as e:
        return safe_jsonify({'error': f'删除文件失败: {str(e)}'}), 500

@pdf_converter_bp.route('/diagnose', methods=['GET'])
def diagnose_pdf_capabilities():
    """诊断PDF处理能力"""
    try:
        enhanced_parser = get_enhanced_parser()
        capabilities = enhanced_parser.available_libraries
        
        # 检查系统信息
        import platform
        import sys
        
        system_info = {
            'platform': platform.platform(),
            'python_version': sys.version,
            'architecture': platform.architecture(),
        }
        
        # 检查环境变量
        env_info = {
            'JAVA_HOME': os.environ.get('JAVA_HOME', 'Not set'),
            'PATH': os.environ.get('PATH', '').split(':')[:5],  # 只显示前5个路径
        }
        
        return safe_jsonify({
            'pdf_libraries': capabilities,
            'system_info': system_info,
            'environment': env_info,
            'recommendations': get_recommendations(capabilities)
        })
        
    except Exception as e:
        return safe_jsonify({'error': str(e)}), 500

def get_recommendations(capabilities):
    """根据可用库提供建议"""
    recommendations = []
    
    if not capabilities.get('pdfplumber') and not capabilities.get('pdfminer') and not capabilities.get('pypdf2'):
        recommendations.append("安装文本提取库: pip install pdfplumber pdfminer.six PyPDF2")
    
    if not capabilities.get('camelot') and not capabilities.get('tabula'):
        recommendations.append("安装表格提取库: pip install camelot-py[cv] tabula-py")
    
    if not capabilities.get('camelot'):
        recommendations.append("安装系统依赖: apt-get install -y ghostscript poppler-utils")
    
    if not capabilities.get('tabula'):
        recommendations.append("安装Java运行环境: apt-get install -y default-jre")
    
    return recommendations

@pdf_converter_bp.route('/test_pdf/<file_id>', methods=['GET'])
def test_pdf_parsing(file_id):
    """测试PDF解析能力"""
    try:
        upload_path, _ = get_upload_output_paths()
        get_path_manager().ensure_directories()
        pdf_path = os.path.join(upload_path, f"{file_id}.pdf")
        
        if not os.path.exists(pdf_path):
            return safe_jsonify({'error': '文件不存在'}), 404
        
        enhanced_parser = get_enhanced_parser()
        pdf_content = enhanced_parser.extract_pdf_content(pdf_path)
        
        # 构建测试结果
        test_result = {
            'file_id': file_id,
            'parsing_success': pdf_content['success'],
            'available_libraries': pdf_content['library_info'],
            'sections_found': {},
            'structure_analysis': {},
            'recommendations': []
        }
        
        if pdf_content['success']:
            sections = pdf_content['sections']
            test_result['sections_found'] = {
                'customer_info': sections['customer_info']['found'],
                'order_tables': sections['order_tables']['found'],
                'summary': sections['summary']['found']
            }
            
            test_result['structure_analysis'] = pdf_content['structure']
            
            # 提供具体建议
            if not sections['customer_info']['found']:
                test_result['recommendations'].append("客户信息部分未找到，可能需要调整关键词识别")
            
            if not sections['order_tables']['found']:
                test_result['recommendations'].append("订单表格未找到，检查表格提取库是否正常工作")
            
            if not sections['summary']['found']:
                test_result['recommendations'].append("总结部分未找到，可能需要调整总结信息识别")
        else:
            test_result['error'] = pdf_content['error']
            test_result['recommendations'] = get_recommendations(pdf_content['library_info'])
        
        return safe_jsonify(test_result)
        
    except Exception as e:
        return safe_jsonify({'error': str(e)}), 500