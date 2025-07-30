"""
订单与产品规格比对相关的API路由
"""

from flask import Blueprint, request, jsonify, send_file, current_app
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.enhanced_spec_manager import EnhancedProductSpecManager
from src.utils.order_comparator import OrderSpecComparator
from src.utils.json_utils import safe_jsonify, clean_nan_values, prepare_sheet_data
from ..utils.path_manager import get_path_manager

# 创建蓝图
spec_bp = Blueprint('spec', __name__)

# 初始化管理器
spec_manager = EnhancedProductSpecManager()
comparator = OrderSpecComparator()

@spec_bp.route('/api/upload_spec', methods=['POST'])
def upload_spec():
    """上传产品规格表"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'error': '未选择文件',
                'error_code': 'NO_FILE_SELECTED',
                'message': '请选择一个Excel文件上传'
            }), 400
            
        file = request.files['file']
        
        # 检查文件名是否为空
        if file.filename == '':
            return jsonify({
                'error': '文件名为空',
                'error_code': 'EMPTY_FILENAME',
                'message': '请选择一个有效的文件'
            }), 400
        
        # 获取列名映射配置信息（用于错误提示）
        mapping_info = spec_manager.get_column_mapping_info()
        
        # 上传并处理文件
        result = spec_manager.upload_spec(file)
        
        if 'error' in result:
            # 返回详细的错误信息和建议
            response = {
                'error': result['error'],
                'error_code': result.get('error_code', 'VALIDATION_ERROR'),
                'message': result.get('message', '规格表验证失败，请查看详细错误信息')
            }
            
            # 添加警告、数据错误和建议（如果有）
            if 'warnings' in result:
                response['warnings'] = result['warnings']
            
            if 'data_errors' in result:
                response['data_errors'] = result['data_errors']
                
            if 'suggestions' in result:
                response['suggestions'] = result['suggestions']
                
            if 'mapping_result' in result:
                response['mapping_result'] = result['mapping_result']
                
            # 添加列名映射信息，帮助用户理解所需格式
            response['column_mapping_info'] = mapping_info
            
            # 添加可接受的列名示例
            response['acceptable_columns'] = spec_manager.generate_column_mapping_examples()
            
            return jsonify(response), 400
        else:
            # 添加警告（如果有）
            if 'warnings' in result:
                result['has_warnings'] = True
                result['warning_count'] = len(result['warnings'])
                
            # 添加成功消息
            result['message'] = '规格表上传成功'
            
            # 添加映射信息（如果应用了映射）
            if 'mapped_columns' in result and result['mapped_columns']:
                result['mapping_applied'] = True
                result['mapping_count'] = len(result['mapped_columns'])
                
            return jsonify(result), 200
            
    except Exception as e:
        current_app.logger.error(f"上传规格表失败: {str(e)}")
        return jsonify({
            'error': '上传失败',
            'error_code': 'UPLOAD_FAILED',
            'message': f'处理文件时发生错误: {str(e)}',
            'details': str(e)
        }), 500

@spec_bp.route('/api/list_specs', methods=['GET'])
def list_specs():
    """获取产品规格表列表"""
    try:
        specs = spec_manager.list_specs()
        return jsonify({'specs': specs}), 200
        
    except Exception as e:
        current_app.logger.error(f"获取规格表列表失败: {str(e)}")
        return jsonify({'error': '获取列表失败'}), 500

@spec_bp.route('/api/delete_spec/<spec_id>', methods=['DELETE'])
def delete_spec(spec_id):
    """删除产品规格表"""
    try:
        result = spec_manager.delete_spec(spec_id)
        
        if 'error' in result:
            return jsonify(result), 404
        else:
            return jsonify(result), 200
            
    except Exception as e:
        current_app.logger.error(f"删除规格表失败: {str(e)}")
        return jsonify({'error': '删除失败'}), 500

@spec_bp.route('/api/compare_orders', methods=['POST'])
def compare_orders():
    """比对订单与产品规格表"""
    try:
        data = request.get_json()
        
        if not data or 'order_file_id' not in data or 'spec_id' not in data:
            return safe_jsonify({'error': '缺少必需的参数'}), 400
            
        order_file_id = data['order_file_id']
        spec_id = data['spec_id']
        check_total_calc = data.get('check_total_calc', True)
        
        # 获取订单文件路径 - 使用路径管理器
        path_manager = get_path_manager()
        order_file_path = path_manager.get_output_path(f"{order_file_id}.xlsx")
        
        # 检查文件是否存在
        if not os.path.exists(order_file_path):
            current_app.logger.error(f"订单文件不存在: {order_file_path}")
            return safe_jsonify({'error': '订单文件不存在'}), 404
            
        # 获取规格表文件路径
        spec_file_path = spec_manager.get_spec_path(spec_id)
        if not spec_file_path:
            return safe_jsonify({'error': '规格表文件不存在'}), 404
            
        # 执行比对
        result = comparator.compare_orders(
            order_file_path, 
            spec_file_path, 
            check_total_calc
        )
        
        if 'error' in result:
            return safe_jsonify(result), 500
        else:
            # 清理结果中的NaN值
            clean_result = clean_nan_values(result)
            
            # 生成摘要报告
            summary = comparator.get_comparison_summary(clean_result['stats'])
            clean_result['summary'] = summary
            
            return safe_jsonify(clean_result), 200
            
    except Exception as e:
        current_app.logger.error(f"订单比对失败: {str(e)}")
        return safe_jsonify({'error': f'比对失败: {str(e)}'}), 500

@spec_bp.route('/api/download_comparison/<result_file_id>', methods=['GET'])
def download_comparison_result(result_file_id):
    """下载比对结果文件"""
    try:
        # 使用与order_comparator一致的路径构建方式
        # 使用路径管理器获取文件路径
        path_manager = get_path_manager()
        file_path = path_manager.get_output_path(f"order_comparison_{result_file_id}.xlsx")
        
        if not os.path.exists(file_path):
            current_app.logger.error(f"比对结果文件不存在: {file_path}")
            return safe_jsonify({'error': '文件不存在'}), 404
            
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"订单比对结果_{result_file_id}.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        current_app.logger.error(f"下载比对结果失败: {str(e)}")
        return safe_jsonify({'error': '下载失败'}), 500

@spec_bp.route('/api/preview_comparison/<result_file_id>', methods=['GET'])
def preview_comparison_result(result_file_id):
    """预览比对结果"""
    try:
        # 使用与order_comparator一致的路径构建方式
        # 使用路径管理器获取文件路径
        path_manager = get_path_manager()
        file_path = path_manager.get_output_path(f"order_comparison_{result_file_id}.xlsx")
        
        if not os.path.exists(file_path):
            current_app.logger.error(f"比对结果文件不存在: {file_path}")
            return safe_jsonify({'error': '文件不存在'}), 404
            
        import pandas as pd
        
        # 读取Excel文件
        df = pd.read_excel(file_path)
        
        # 使用统一的数据准备函数，限制预览行数
        sheet_data = prepare_sheet_data(df.head(100))
        preview_data = sheet_data['data']
        columns = sheet_data['columns']
        
        # 统计信息
        total_rows = len(df)
        error_rows = len(df[df['核对状态'] == '有问题']) if '核对状态' in df.columns else 0
        
        return safe_jsonify({
            'columns': columns,
            'data': preview_data,
            'total_rows': total_rows,
            'error_rows': error_rows,
            'preview_rows': len(preview_data)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"预览比对结果失败: {str(e)}")
        return safe_jsonify({'error': '预览失败'}), 500

@spec_bp.route('/api/spec_info/<spec_id>', methods=['GET'])
def get_spec_info(spec_id):
    """获取规格表详细信息"""
    try:
        spec_path = spec_manager.get_spec_path(spec_id)
        if not spec_path:
            return jsonify({'error': '规格表不存在'}), 404
            
        # 验证规格表格式并获取信息
        validation_result = spec_manager.validate_spec_format(spec_path)
        
        if not validation_result['valid']:
            response = {
                'spec_id': spec_id,
                'valid': False,
                'error': validation_result['error']
            }
            
            # 添加警告、数据错误和建议（如果有）
            if 'warnings' in validation_result:
                response['warnings'] = validation_result['warnings']
            
            if 'data_errors' in validation_result:
                response['data_errors'] = validation_result['data_errors']
                
            if 'suggestions' in validation_result:
                response['suggestions'] = validation_result['suggestions']
                
            if 'mapping_result' in validation_result:
                response['mapping_result'] = validation_result['mapping_result']
                
            return jsonify(response), 400
            
        response = {
            'spec_id': spec_id,
            'valid': True,
            'record_count': validation_result['record_count'],
            'columns': validation_result['columns']
        }
        
        # 添加映射列信息（如果有）
        if 'mapped_columns' in validation_result:
            response['mapped_columns'] = validation_result['mapped_columns']
            
        # 添加警告（如果有）
        if 'warnings' in validation_result:
            response['warnings'] = validation_result['warnings']
            response['has_warnings'] = True
            
        if 'data_errors' in validation_result:
            response['data_errors'] = validation_result['data_errors']
            
        return jsonify(response), 200
        
    except Exception as e:
        current_app.logger.error(f"获取规格表信息失败: {str(e)}")
        return jsonify({'error': '获取信息失败'}), 500

@spec_bp.route('/api/download_spec/<spec_id>', methods=['GET'])
def download_spec(spec_id):
    """下载规格表文件"""
    try:
        spec_path = spec_manager.get_spec_path(spec_id)
        if not spec_path:
            return jsonify({'error': '规格表不存在'}), 404
        
        # 获取原始文件名
        import json
        metadata_path = os.path.join(spec_manager.specs_dir, f"{spec_id}.json")
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        original_filename = metadata.get('original_filename', f"规格表_{spec_id}.xlsx")
        
        return send_file(
            spec_path,
            as_attachment=True,
            download_name=original_filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        current_app.logger.error(f"下载规格表失败: {str(e)}")
        return jsonify({'error': '下载失败'}), 500

@spec_bp.route('/api/preview_spec/<spec_id>', methods=['GET'])
def preview_spec(spec_id):
    """预览规格表内容"""
    try:
        spec_path = spec_manager.get_spec_path(spec_id)
        if not spec_path:
            return jsonify({'error': '规格表不存在'}), 404
        
        import pandas as pd
        
        # 读取Excel文件
        df = pd.read_excel(spec_path)
        
        # 使用统一的数据准备函数，限制预览行数
        sheet_data = prepare_sheet_data(df.head(100))
        preview_data = sheet_data['data']
        columns = sheet_data['columns']
        
        return safe_jsonify({
            'spec_id': spec_id,
            'columns': columns,
            'data': preview_data,
            'total_rows': len(df),
            'preview_rows': len(preview_data)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"预览规格表失败: {str(e)}")
        return safe_jsonify({'error': '预览失败'}), 500

@spec_bp.route('/api/download_spec_template', methods=['GET'])
def download_spec_template():
    """下载规格表模板文件"""
    try:
        import pandas as pd
        import tempfile
        
        # 获取行数参数
        row_count = request.args.get('rows', default=5, type=int)
        
        # 生成示例数据
        df = spec_manager.generate_sample_excel(row_count)
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            df.to_excel(tmp_file.name, index=False)
            
            return send_file(
                tmp_file.name,
                as_attachment=True,
                download_name='产品规格表模板.xlsx',
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
    except Exception as e:
        current_app.logger.error(f"生成规格表模板失败: {str(e)}")
        return jsonify({'error': '模板生成失败'}), 500

@spec_bp.route('/api/column_mapping_info', methods=['GET'])
def get_column_mapping_info():
    """获取列名映射配置信息"""
    try:
        mapping_info = spec_manager.get_column_mapping_info()
        return jsonify(mapping_info), 200
    except Exception as e:
        current_app.logger.error(f"获取列名映射配置失败: {str(e)}")
        return jsonify({
            'error': '获取配置失败',
            'error_code': 'CONFIG_FETCH_ERROR',
            'message': '无法获取列名映射配置信息',
            'details': str(e)
        }), 500

@spec_bp.route('/api/config/column_mappings', methods=['GET'])
def get_column_mappings_config():
    """获取列名映射配置"""
    try:
        from src.utils.config_loader import ConfigLoader
        
        # 获取原始配置
        config = ConfigLoader.get_column_mappings()
        
        # 如果配置为空，返回默认配置
        if not config:
            config = ConfigLoader.get_default_column_mappings()
        
        return jsonify({
            'success': True,
            'config': config,
            'message': '获取列名映射配置成功'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取列名映射配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取配置失败',
            'error_code': 'CONFIG_FETCH_ERROR',
            'message': '无法获取列名映射配置',
            'details': str(e)
        }), 500

@spec_bp.route('/api/config/column_mappings', methods=['PUT'])
def update_column_mappings_config():
    """更新列名映射配置"""
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': '请求必须是JSON格式',
                'error_code': 'INVALID_REQUEST_FORMAT',
                'message': '请确保请求体是有效的JSON格式'
            }), 400
        
        from src.utils.config_loader import ConfigLoader
        
        # 获取请求数据
        config_data = request.get_json()
        
        # 验证配置数据
        if not isinstance(config_data, dict):
            return jsonify({
                'success': False,
                'error': '无效的配置数据格式',
                'error_code': 'INVALID_CONFIG_FORMAT',
                'message': '配置数据必须是一个JSON对象'
            }), 400
        
        # 验证必要的键
        required_keys = ['column_mappings', 'required_columns', 'optional_columns']
        missing_keys = [key for key in required_keys if key not in config_data]
        
        if missing_keys:
            return jsonify({
                'success': False,
                'error': f'缺少必要的配置键: {", ".join(missing_keys)}',
                'error_code': 'MISSING_CONFIG_KEYS',
                'message': '配置数据必须包含column_mappings、required_columns和optional_columns'
            }), 400
        
        # 验证column_mappings格式
        if not isinstance(config_data['column_mappings'], dict):
            return jsonify({
                'success': False,
                'error': 'column_mappings必须是一个对象',
                'error_code': 'INVALID_COLUMN_MAPPINGS',
                'message': 'column_mappings应该是一个对象，键为标准列名，值为别名数组'
            }), 400
        
        # 验证required_columns和optional_columns格式
        if not isinstance(config_data['required_columns'], list) or not isinstance(config_data['optional_columns'], list):
            return jsonify({
                'success': False,
                'error': 'required_columns和optional_columns必须是数组',
                'error_code': 'INVALID_COLUMNS_FORMAT',
                'message': 'required_columns和optional_columns应该是字符串数组'
            }), 400
        
        # 验证required_columns中的列是否都在column_mappings中定义
        undefined_required = [col for col in config_data['required_columns'] if col not in config_data['column_mappings']]
        if undefined_required:
            return jsonify({
                'success': False,
                'error': f'以下必需列在column_mappings中未定义: {", ".join(undefined_required)}',
                'error_code': 'UNDEFINED_REQUIRED_COLUMNS',
                'message': '所有必需列必须在column_mappings中定义'
            }), 400
        
        # 验证optional_columns中的列是否都在column_mappings中定义
        undefined_optional = [col for col in config_data['optional_columns'] if col not in config_data['column_mappings']]
        if undefined_optional:
            return jsonify({
                'success': False,
                'error': f'以下可选列在column_mappings中未定义: {", ".join(undefined_optional)}',
                'error_code': 'UNDEFINED_OPTIONAL_COLUMNS',
                'message': '所有可选列必须在column_mappings中定义'
            }), 400
        
        # 保存配置
        if ConfigLoader.save_column_mappings(config_data):
            # 重新加载配置到spec_manager
            spec_manager.load_column_mappings()
            
            return jsonify({
                'success': True,
                'message': '列名映射配置已更新',
                'config': config_data
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '保存配置失败',
                'error_code': 'CONFIG_SAVE_ERROR',
                'message': '无法保存列名映射配置'
            }), 500
        
    except Exception as e:
        current_app.logger.error(f"更新列名映射配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '更新配置失败',
            'error_code': 'CONFIG_UPDATE_ERROR',
            'message': '更新列名映射配置时发生错误',
            'details': str(e)
        }), 500

@spec_bp.route('/api/config/column_mappings/reset', methods=['POST'])
def reset_column_mappings_config():
    """重置列名映射配置为默认值"""
    try:
        from src.utils.config_loader import ConfigLoader
        
        # 获取默认配置
        default_config = ConfigLoader.get_default_column_mappings()
        
        # 保存默认配置
        if ConfigLoader.save_column_mappings(default_config):
            # 重新加载配置到spec_manager
            spec_manager.load_column_mappings()
            
            return jsonify({
                'success': True,
                'message': '列名映射配置已重置为默认值',
                'config': default_config
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '重置配置失败',
                'error_code': 'CONFIG_RESET_ERROR',
                'message': '无法重置列名映射配置'
            }), 500
        
    except Exception as e:
        current_app.logger.error(f"重置列名映射配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '重置配置失败',
            'error_code': 'CONFIG_RESET_ERROR',
            'message': '重置列名映射配置时发生错误',
            'details': str(e)
        }), 500

@spec_bp.route('/api/config/column_mappings/column', methods=['POST'])
def add_column_mapping():
    """添加新的列映射"""
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': '请求必须是JSON格式',
                'error_code': 'INVALID_REQUEST_FORMAT',
                'message': '请确保请求体是有效的JSON格式'
            }), 400
        
        from src.utils.config_loader import ConfigLoader
        
        # 获取请求数据
        data = request.get_json()
        
        # 验证必要的参数
        required_params = ['standard_column', 'aliases', 'is_required']
        missing_params = [param for param in required_params if param not in data]
        
        if missing_params:
            return jsonify({
                'success': False,
                'error': f'缺少必要的参数: {", ".join(missing_params)}',
                'error_code': 'MISSING_PARAMETERS',
                'message': '请提供standard_column、aliases和is_required参数'
            }), 400
        
        standard_column = data['standard_column']
        aliases = data['aliases']
        is_required = data['is_required']
        
        # 验证参数类型
        if not isinstance(standard_column, str) or not standard_column:
            return jsonify({
                'success': False,
                'error': 'standard_column必须是非空字符串',
                'error_code': 'INVALID_STANDARD_COLUMN',
                'message': '请提供有效的标准列名'
            }), 400
        
        if not isinstance(aliases, list):
            return jsonify({
                'success': False,
                'error': 'aliases必须是字符串数组',
                'error_code': 'INVALID_ALIASES',
                'message': 'aliases应该是一个字符串数组'
            }), 400
        
        if not isinstance(is_required, bool):
            return jsonify({
                'success': False,
                'error': 'is_required必须是布尔值',
                'error_code': 'INVALID_IS_REQUIRED',
                'message': 'is_required应该是一个布尔值'
            }), 400
        
        # 获取当前配置
        config = ConfigLoader.get_column_mappings()
        if not config:
            config = ConfigLoader.get_default_column_mappings()
        
        # 更新配置
        if standard_column not in config['column_mappings']:
            config['column_mappings'][standard_column] = []
        
        # 添加新的别名（去重）
        for alias in aliases:
            if isinstance(alias, str) and alias and alias not in config['column_mappings'][standard_column]:
                config['column_mappings'][standard_column].append(alias)
        
        # 更新必需/可选列
        if is_required:
            if standard_column not in config['required_columns']:
                config['required_columns'].append(standard_column)
            # 确保不在可选列中
            if standard_column in config['optional_columns']:
                config['optional_columns'].remove(standard_column)
        else:
            if standard_column not in config['optional_columns']:
                config['optional_columns'].append(standard_column)
            # 确保不在必需列中
            if standard_column in config['required_columns']:
                config['required_columns'].remove(standard_column)
        
        # 保存配置
        if ConfigLoader.save_column_mappings(config):
            # 重新加载配置到spec_manager
            spec_manager.load_column_mappings()
            
            return jsonify({
                'success': True,
                'message': f'已添加列映射: {standard_column}',
                'standard_column': standard_column,
                'aliases': config['column_mappings'][standard_column],
                'is_required': standard_column in config['required_columns'],
                'config': config
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '保存配置失败',
                'error_code': 'CONFIG_SAVE_ERROR',
                'message': '无法保存列名映射配置'
            }), 500
        
    except Exception as e:
        current_app.logger.error(f"添加列映射失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '添加列映射失败',
            'error_code': 'ADD_MAPPING_ERROR',
            'message': '添加列映射时发生错误',
            'details': str(e)
        }), 500

@spec_bp.route('/api/config/column_mappings/column/<standard_column>', methods=['DELETE'])
def delete_column_mapping(standard_column):
    """删除列映射"""
    try:
        from src.utils.config_loader import ConfigLoader
        
        # 获取当前配置
        config = ConfigLoader.get_column_mappings()
        if not config:
            config = ConfigLoader.get_default_column_mappings()
        
        # 检查列是否存在
        if standard_column not in config['column_mappings']:
            return jsonify({
                'success': False,
                'error': f'列映射不存在: {standard_column}',
                'error_code': 'COLUMN_NOT_FOUND',
                'message': f'找不到名为{standard_column}的列映射'
            }), 404
        
        # 删除列映射
        del config['column_mappings'][standard_column]
        
        # 从必需列和可选列中移除
        if standard_column in config['required_columns']:
            config['required_columns'].remove(standard_column)
        
        if standard_column in config['optional_columns']:
            config['optional_columns'].remove(standard_column)
        
        # 保存配置
        if ConfigLoader.save_column_mappings(config):
            # 重新加载配置到spec_manager
            spec_manager.load_column_mappings()
            
            return jsonify({
                'success': True,
                'message': f'已删除列映射: {standard_column}',
                'config': config
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '保存配置失败',
                'error_code': 'CONFIG_SAVE_ERROR',
                'message': '无法保存列名映射配置'
            }), 500
        
    except Exception as e:
        current_app.logger.error(f"删除列映射失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '删除列映射失败',
            'error_code': 'DELETE_MAPPING_ERROR',
            'message': '删除列映射时发生错误',
            'details': str(e)
        }), 500

@spec_bp.route('/api/config/column_mappings/column/<standard_column>/alias', methods=['POST'])
def add_column_alias(standard_column):
    """添加列别名"""
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': '请求必须是JSON格式',
                'error_code': 'INVALID_REQUEST_FORMAT',
                'message': '请确保请求体是有效的JSON格式'
            }), 400
        
        from src.utils.config_loader import ConfigLoader
        
        # 获取请求数据
        data = request.get_json()
        
        # 验证必要的参数
        if 'alias' not in data:
            return jsonify({
                'success': False,
                'error': '缺少必要的参数: alias',
                'error_code': 'MISSING_PARAMETERS',
                'message': '请提供alias参数'
            }), 400
        
        alias = data['alias']
        
        # 验证参数类型
        if not isinstance(alias, str) or not alias:
            return jsonify({
                'success': False,
                'error': 'alias必须是非空字符串',
                'error_code': 'INVALID_ALIAS',
                'message': '请提供有效的列别名'
            }), 400
        
        # 获取当前配置
        config = ConfigLoader.get_column_mappings()
        if not config:
            config = ConfigLoader.get_default_column_mappings()
        
        # 检查列是否存在
        if standard_column not in config['column_mappings']:
            return jsonify({
                'success': False,
                'error': f'列映射不存在: {standard_column}',
                'error_code': 'COLUMN_NOT_FOUND',
                'message': f'找不到名为{standard_column}的列映射'
            }), 404
        
        # 添加别名（如果不存在）
        if alias not in config['column_mappings'][standard_column]:
            config['column_mappings'][standard_column].append(alias)
            
            # 保存配置
            if ConfigLoader.save_column_mappings(config):
                # 重新加载配置到spec_manager
                spec_manager.load_column_mappings()
                
                return jsonify({
                    'success': True,
                    'message': f'已添加别名: {alias}',
                    'standard_column': standard_column,
                    'aliases': config['column_mappings'][standard_column]
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': '保存配置失败',
                    'error_code': 'CONFIG_SAVE_ERROR',
                    'message': '无法保存列名映射配置'
                }), 500
        else:
            return jsonify({
                'success': True,
                'message': f'别名已存在: {alias}',
                'standard_column': standard_column,
                'aliases': config['column_mappings'][standard_column]
            }), 200
        
    except Exception as e:
        current_app.logger.error(f"添加列别名失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '添加列别名失败',
            'error_code': 'ADD_ALIAS_ERROR',
            'message': '添加列别名时发生错误',
            'details': str(e)
        }), 500

@spec_bp.route('/api/column_mapping_examples', methods=['GET'])
def get_column_mapping_examples():
    """获取列名映射示例"""
    try:
        examples = spec_manager.generate_column_mapping_examples()
        
        # 添加示例数据
        sample_df = spec_manager.generate_sample_excel(3)
        sample_data = {}
        
        for col in sample_df.columns:
            sample_data[col] = sample_df[col].tolist()
        
        return jsonify({
            'examples': examples,
            'sample_data': sample_data
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取列名映射示例失败: {str(e)}")
        return jsonify({'error': '获取示例失败'}), 500

@spec_bp.route('/api/upload_for_mapping', methods=['POST'])
def upload_for_mapping():
    """上传文件用于列映射预览和确认"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'error': '未选择文件',
                'error_code': 'NO_FILE_SELECTED',
                'message': '请选择一个Excel文件上传'
            }), 400
            
        file = request.files['file']
        
        # 检查文件名是否为空
        if file.filename == '':
            return jsonify({
                'error': '文件名为空',
                'error_code': 'EMPTY_FILENAME',
                'message': '请选择一个有效的文件'
            }), 400
        
        # 检查文件格式
        if not spec_manager.allowed_file(file.filename):
            return jsonify({
                'error': '文件格式不支持，请上传Excel文件(.xlsx或.xls)',
                'error_code': 'INVALID_FILE_FORMAT',
                'message': '只支持.xlsx或.xls格式的Excel文件'
            }), 400
        
        # 生成唯一的文件ID
        import uuid
        import tempfile
        file_id = str(uuid.uuid4())
        original_filename = file.filename
        
        # 保存到临时目录
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, f"{file_id}.xlsx")
        file.save(file_path)
        
        # 验证Excel文件是否可以正常读取
        try:
            import pandas as pd
            df = pd.read_excel(file_path)
            
            if df.empty:
                os.remove(file_path)
                return jsonify({
                    'error': 'Excel文件为空或格式不正确',
                    'error_code': 'EMPTY_EXCEL_FILE',
                    'message': '上传的Excel文件不包含任何数据，请检查文件内容'
                }), 400
            
            # 尝试自动映射列名
            mapping_result = spec_manager.map_columns(df)
            
            # 返回文件ID和初步映射结果
            response = {
                'file_id': file_id,
                'original_filename': original_filename,
                'column_count': len(df.columns),
                'row_count': len(df),
                'columns': list(df.columns),
                'auto_mapping_success': mapping_result.success,
                'mapped_columns': mapping_result.mapped_columns,
                'missing_required': mapping_result.missing_required,
                'unmapped_columns': mapping_result.unmapped_columns
            }
            
            # 添加建议信息
            if mapping_result.suggestions:
                structured_suggestions = {}
                for col, suggestion in mapping_result.suggestions.items():
                    structured_suggestions[col] = {
                        'mapped_to': suggestion['mapped_to'],
                        'confidence': suggestion['confidence'],
                        'suggestions': suggestion['suggestions']
                    }
                
                response['suggestions'] = structured_suggestions
            
            # 添加列名映射配置信息
            response['column_mapping_info'] = spec_manager.get_column_mapping_info()
            
            return jsonify(response), 200
            
        except Exception as e:
            # 如果读取失败，删除临时文件
            if os.path.exists(file_path):
                os.remove(file_path)
                
            return jsonify({
                'error': f'Excel文件处理失败: {str(e)}',
                'error_code': 'EXCEL_PROCESSING_ERROR',
                'message': '无法处理Excel文件，请检查文件格式是否正确',
                'details': str(e)
            }), 400
            
    except Exception as e:
        current_app.logger.error(f"上传文件用于映射失败: {str(e)}")
        return jsonify({
            'error': f'上传失败: {str(e)}',
            'error_code': 'UPLOAD_FAILED',
            'message': '文件上传过程中发生错误',
            'details': str(e)
        }), 500

@spec_bp.route('/api/validate_mapping', methods=['POST'])
def validate_mapping():
    """验证列映射"""
    try:
        if not request.is_json:
            return jsonify({
                'error': '请求必须是JSON格式',
                'error_code': 'INVALID_REQUEST_FORMAT',
                'message': '请确保请求体是有效的JSON格式'
            }), 400
            
        data = request.get_json()
        
        if 'file_id' not in data:
            return jsonify({
                'error': '缺少file_id参数',
                'error_code': 'MISSING_FILE_ID',
                'message': '请提供file_id参数以识别要验证的文件'
            }), 400
            
        file_id = data['file_id']
        
        # 获取临时上传的文件路径
        import tempfile
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, f"{file_id}.xlsx")
        
        if not os.path.exists(file_path):
            return jsonify({
                'error': '找不到上传的文件',
                'error_code': 'FILE_NOT_FOUND',
                'message': f'找不到ID为{file_id}的文件，可能已过期或未上传'
            }), 404
            
        # 读取Excel文件
        import pandas as pd
        df = pd.read_excel(file_path)
        
        # 如果提供了自定义映射，使用它
        custom_mapping = data.get('column_mapping', {})
        
        if custom_mapping:
            # 创建一个新的DataFrame，使用自定义映射
            mapped_df = pd.DataFrame()
            
            for standard_col, original_col in custom_mapping.items():
                if original_col in df.columns:
                    mapped_df[standard_col] = df[original_col]
                else:
                    mapped_df[standard_col] = None
                    
            # 验证映射后的DataFrame
            validation_result = spec_manager.validate_mapped_dataframe(mapped_df)
            
            # 如果验证失败，返回错误信息
            if not validation_result['valid']:
                # 生成修改建议
                correction_suggestions = spec_manager.suggest_corrections(df, validation_result)
                
                return jsonify({
                    'valid': False,
                    'error': validation_result['error'],
                    'error_code': 'CUSTOM_MAPPING_VALIDATION_FAILED',
                    'message': '自定义映射验证失败，请查看详细错误信息',
                    'warnings': validation_result.get('warnings', []),
                    'data_errors': validation_result.get('data_errors', {}),
                    'suggestions': correction_suggestions
                }), 400
                
            # 如果验证成功，返回结果
            result = {
                'valid': True,
                'message': '自定义映射验证成功',
                'record_count': validation_result['record_count'],
                'columns': validation_result['columns'],
                'custom_mapping': custom_mapping
            }
            
            # 添加警告（如果有）
            if 'warnings' in validation_result:
                result['warnings'] = validation_result['warnings']
                result['has_warnings'] = True
                result['data_errors'] = validation_result.get('data_errors', {})
                
            return jsonify(result), 200
        else:
            # 使用自动映射
            mapping_result = spec_manager.map_columns(df)
            
            # 如果映射失败，返回错误信息
            if not mapping_result.success:
                error_msg = f'Excel文件缺少必需的列: {", ".join(mapping_result.missing_required)}'
                
                # 添加建议信息
                suggestions = {}
                if mapping_result.suggestions:
                    column_suggestions = []
                    for col, suggestion in mapping_result.suggestions.items():
                        if suggestion['mapped_to'] is None and col in mapping_result.unmapped_columns:
                            sugg_list = [f"'{s}'" for s in suggestion['suggestions']]
                            sugg_str = f"'{col}' 可能是 {', '.join(sugg_list)}"
                            column_suggestions.append(sugg_str)
                    
                    if column_suggestions:
                        suggestions['column_mapping'] = {
                            'message': '建议修改列名',
                            'suggestions': column_suggestions
                        }
                
                return jsonify({
                    'valid': False, 
                    'error': error_msg,
                    'error_code': 'AUTO_MAPPING_FAILED',
                    'message': '自动列映射失败，缺少必需的列',
                    'mapping_result': mapping_result.__dict__,
                    'suggestions': suggestions,
                    'required_columns': spec_manager.required_columns,
                    'missing_columns': mapping_result.missing_required
                }), 400
                
            # 创建映射后的DataFrame
            mapped_df = spec_manager.create_mapped_dataframe(df, mapping_result)
            
            # 验证映射后的DataFrame
            validation_result = spec_manager.validate_mapped_dataframe(mapped_df)
            
            # 如果验证失败，返回错误信息
            if not validation_result['valid']:
                # 生成修改建议
                correction_suggestions = spec_manager.suggest_corrections(df, validation_result)
                
                return jsonify({
                    'valid': False,
                    'error': validation_result['error'],
                    'error_code': 'AUTO_MAPPING_VALIDATION_FAILED',
                    'message': '自动映射验证失败，请查看详细错误信息',
                    'warnings': validation_result.get('warnings', []),
                    'data_errors': validation_result.get('data_errors', {}),
                    'suggestions': correction_suggestions
                }), 400
                
            # 如果验证成功，返回结果
            result = {
                'valid': True,
                'message': '自动映射验证成功',
                'record_count': validation_result['record_count'],
                'columns': validation_result['columns'],
                'mapped_columns': mapping_result.mapped_columns
            }
            
            # 添加警告（如果有）
            if 'warnings' in validation_result:
                result['warnings'] = validation_result['warnings']
                result['has_warnings'] = True
                result['data_errors'] = validation_result.get('data_errors', {})
                
            return jsonify(result), 200
            
    except Exception as e:
        current_app.logger.error(f"验证列映射失败: {str(e)}")
        return jsonify({
            'error': f'验证失败: {str(e)}',
            'error_code': 'MAPPING_VALIDATION_ERROR',
            'message': '验证列映射时发生错误',
            'details': str(e)
        }), 500

@spec_bp.route('/api/preview_mapping', methods=['POST'])
def preview_mapping():
    """预览列映射结果"""
    try:
        if not request.is_json:
            return jsonify({
                'error': '请求必须是JSON格式',
                'error_code': 'INVALID_REQUEST_FORMAT',
                'message': '请确保请求体是有效的JSON格式'
            }), 400
            
        data = request.get_json()
        
        if 'file_id' not in data:
            return jsonify({
                'error': '缺少file_id参数',
                'error_code': 'MISSING_FILE_ID',
                'message': '请提供file_id参数以识别要预览的文件'
            }), 400
            
        file_id = data['file_id']
        
        # 获取临时上传的文件路径
        import tempfile
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, f"{file_id}.xlsx")
        
        if not os.path.exists(file_path):
            return jsonify({
                'error': '找不到上传的文件',
                'error_code': 'FILE_NOT_FOUND',
                'message': f'找不到ID为{file_id}的文件，可能已过期或未上传'
            }), 404
            
        # 读取Excel文件
        import pandas as pd
        df = pd.read_excel(file_path)
        
        # 获取列映射方式
        mapping_type = data.get('mapping_type', 'auto')  # 'auto' 或 'custom'
        custom_mapping = data.get('column_mapping', {})
        
        # 根据映射类型获取映射结果
        if mapping_type == 'custom' and custom_mapping:
            # 使用自定义映射
            preview_data = []
            
            # 获取原始数据的前5行（或更少）
            sample_rows = min(5, len(df))
            original_sample = df.head(sample_rows).to_dict('records')
            
            # 创建映射预览
            for i, row in enumerate(original_sample):
                mapped_row = {}
                for standard_col, original_col in custom_mapping.items():
                    if original_col in df.columns:
                        mapped_row[standard_col] = row.get(original_col)
                    else:
                        mapped_row[standard_col] = None
                
                preview_data.append({
                    'row_index': i + 1,
                    'original': row,
                    'mapped': mapped_row
                })
                
            # 构建响应
            response = {
                'mapping_type': 'custom',
                'custom_mapping': custom_mapping,
                'preview_data': preview_data,
                'original_columns': list(df.columns),
                'mapped_columns': list(custom_mapping.keys()),
                'sample_count': sample_rows,
                'total_rows': len(df)
            }
            
            return jsonify(response), 200
            
        else:
            # 使用自动映射
            mapping_result = spec_manager.map_columns(df)
            
            # 如果映射失败，仍然返回部分映射结果供预览
            preview_data = []
            
            # 获取原始数据的前5行（或更少）
            sample_rows = min(5, len(df))
            original_sample = df.head(sample_rows).to_dict('records')
            
            # 创建映射预览
            for i, row in enumerate(original_sample):
                mapped_row = {}
                for original_col, standard_col in mapping_result.mapped_columns.items():
                    mapped_row[standard_col] = row.get(original_col)
                
                # 对于缺失的必需列，添加空值
                for col in mapping_result.missing_required:
                    mapped_row[col] = None
                
                preview_data.append({
                    'row_index': i + 1,
                    'original': row,
                    'mapped': mapped_row
                })
            
            # 构建响应
            response = {
                'mapping_type': 'auto',
                'mapping_success': mapping_result.success,
                'mapped_columns': mapping_result.mapped_columns,
                'missing_required': mapping_result.missing_required,
                'unmapped_columns': mapping_result.unmapped_columns,
                'preview_data': preview_data,
                'original_columns': list(df.columns),
                'sample_count': sample_rows,
                'total_rows': len(df)
            }
            
            # 添加建议信息
            if mapping_result.suggestions:
                structured_suggestions = {}
                for col, suggestion in mapping_result.suggestions.items():
                    structured_suggestions[col] = {
                        'mapped_to': suggestion['mapped_to'],
                        'confidence': suggestion['confidence'],
                        'suggestions': suggestion['suggestions']
                    }
                
                response['suggestions'] = structured_suggestions
            
            return jsonify(response), 200
            
    except Exception as e:
        current_app.logger.error(f"预览列映射失败: {str(e)}")
        return jsonify({
            'error': f'预览失败: {str(e)}',
            'error_code': 'MAPPING_PREVIEW_ERROR',
            'message': '预览列映射时发生错误',
            'details': str(e)
        }), 500

@spec_bp.route('/api/confirm_mapping', methods=['POST'])
def confirm_mapping():
    """确认列映射并上传规格表"""
    try:
        if not request.is_json:
            return jsonify({
                'error': '请求必须是JSON格式',
                'error_code': 'INVALID_REQUEST_FORMAT',
                'message': '请确保请求体是有效的JSON格式'
            }), 400
            
        data = request.get_json()
        
        if 'file_id' not in data:
            return jsonify({
                'error': '缺少file_id参数',
                'error_code': 'MISSING_FILE_ID',
                'message': '请提供file_id参数以识别要确认的文件'
            }), 400
            
        file_id = data['file_id']
        
        # 获取临时上传的文件路径
        import tempfile
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, f"{file_id}.xlsx")
        
        if not os.path.exists(file_path):
            return jsonify({
                'error': '找不到上传的文件',
                'error_code': 'FILE_NOT_FOUND',
                'message': f'找不到ID为{file_id}的文件，可能已过期或未上传'
            }), 404
            
        # 读取Excel文件
        import pandas as pd
        df = pd.read_excel(file_path)
        
        # 获取映射类型和映射信息
        mapping_type = data.get('mapping_type', 'auto')  # 'auto' 或 'custom'
        custom_mapping = data.get('column_mapping', {})
        
        # 根据映射类型处理数据
        if mapping_type == 'custom' and custom_mapping:
            # 使用自定义映射创建新的DataFrame
            mapped_df = pd.DataFrame()
            
            for standard_col, original_col in custom_mapping.items():
                if original_col in df.columns:
                    mapped_df[standard_col] = df[original_col]
                else:
                    mapped_df[standard_col] = None
            
            # 验证映射后的DataFrame
            validation_result = spec_manager.validate_mapped_dataframe(mapped_df)
            
            # 如果验证失败，返回错误信息
            if not validation_result['valid']:
                return jsonify({
                    'valid': False,
                    'error': validation_result['error'],
                    'error_code': 'CUSTOM_MAPPING_VALIDATION_FAILED',
                    'message': '自定义映射验证失败，无法保存规格表',
                    'warnings': validation_result.get('warnings', []),
                    'data_errors': validation_result.get('data_errors', {})
                }), 400
            
            # 生成唯一的规格表ID
            spec_id = str(uuid.uuid4())
            
            # 获取原始文件名
            original_filename = data.get('original_filename', f"规格表_{spec_id}.xlsx")
            
            # 保存映射后的DataFrame
            spec_file_path = os.path.join(spec_manager.specs_dir, f"{spec_id}.xlsx")
            mapped_df.to_excel(spec_file_path, index=False)
            
            # 创建元数据文件
            metadata = {
                'spec_id': spec_id,
                'original_filename': original_filename,
                'stored_filename': f"{spec_id}.xlsx",
                'upload_time': datetime.datetime.now().isoformat(),
                'file_size': os.path.getsize(spec_file_path),
                'record_count': len(mapped_df),
                'column_mapping': custom_mapping,
                'mapping_type': 'custom'
            }
            
            metadata_path = os.path.join(spec_manager.specs_dir, f"{spec_id}.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            # 删除临时文件
            try:
                os.remove(file_path)
            except:
                pass
            
            # 返回成功响应
            return jsonify({
                'success': True,
                'message': '规格表上传成功',
                'spec_id': spec_id,
                'filename': original_filename,
                'record_count': len(mapped_df),
                'upload_time': metadata['upload_time'],
                'mapping_type': 'custom',
                'mapping_count': len(custom_mapping)
            }), 200
            
        else:
            # 使用自动映射
            mapping_result = spec_manager.map_columns(df)
            
            # 如果映射失败，返回错误信息
            if not mapping_result.success:
                return jsonify({
                    'success': False,
                    'error': f'自动映射失败，缺少必需的列: {", ".join(mapping_result.missing_required)}',
                    'error_code': 'AUTO_MAPPING_FAILED',
                    'message': '无法完成自动列映射，请使用自定义映射',
                    'mapping_result': mapping_result.__dict__
                }), 400
            
            # 创建映射后的DataFrame
            mapped_df = spec_manager.create_mapped_dataframe(df, mapping_result)
            
            # 验证映射后的DataFrame
            validation_result = spec_manager.validate_mapped_dataframe(mapped_df)
            
            # 如果验证失败，返回错误信息
            if not validation_result['valid']:
                return jsonify({
                    'success': False,
                    'error': validation_result['error'],
                    'error_code': 'AUTO_MAPPING_VALIDATION_FAILED',
                    'message': '自动映射验证失败，无法保存规格表',
                    'warnings': validation_result.get('warnings', []),
                    'data_errors': validation_result.get('data_errors', {})
                }), 400
            
            # 生成唯一的规格表ID
            spec_id = str(uuid.uuid4())
            
            # 获取原始文件名
            original_filename = data.get('original_filename', f"规格表_{spec_id}.xlsx")
            
            # 保存映射后的DataFrame
            spec_file_path = os.path.join(spec_manager.specs_dir, f"{spec_id}.xlsx")
            mapped_df.to_excel(spec_file_path, index=False)
            
            # 创建元数据文件
            metadata = {
                'spec_id': spec_id,
                'original_filename': original_filename,
                'stored_filename': f"{spec_id}.xlsx",
                'upload_time': datetime.datetime.now().isoformat(),
                'file_size': os.path.getsize(spec_file_path),
                'record_count': len(mapped_df),
                'column_mapping': mapping_result.mapped_columns,
                'mapping_type': 'auto'
            }
            
            metadata_path = os.path.join(spec_manager.specs_dir, f"{spec_id}.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            # 删除临时文件
            try:
                os.remove(file_path)
            except:
                pass
            
            # 返回成功响应
            return jsonify({
                'success': True,
                'message': '规格表上传成功',
                'spec_id': spec_id,
                'filename': original_filename,
                'record_count': len(mapped_df),
                'upload_time': metadata['upload_time'],
                'mapping_type': 'auto',
                'mapping_count': len(mapping_result.mapped_columns)
            }), 200
            
    except Exception as e:
        current_app.logger.error(f"确认列映射失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'确认失败: {str(e)}',
            'error_code': 'MAPPING_CONFIRMATION_ERROR',
            'message': '确认列映射时发生错误',
            'details': str(e)
        }), 500