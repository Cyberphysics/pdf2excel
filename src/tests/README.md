# 测试文档

本目录包含了PDF转Excel服务中规格表验证功能的完整测试套件。

## 测试结构

### 单元测试
- `test_validation_logic.py` - 验证逻辑的单元测试
- `test_column_mapping.py` - 列名映射功能的单元测试
- `test_config_management.py` - 配置管理功能的单元测试
- `test_api_endpoints.py` - API端点的单元测试
- `test_merge_logic.py` - 行合并逻辑的独立测试（包含独立实现）
- `test_row_merging.py` - 行合并功能的集成测试

### 集成测试
- `test_integration_workflow.py` - 完整工作流程的集成测试
- `test_integration_api.py` - API端点的集成测试

### 测试运行器
- `run_tests.py` - 单元测试运行器
- `run_integration_tests.py` - 集成测试运行器

## 运行测试

### 运行所有单元测试
```bash
cd pdf-to-excel-service/src/tests
python run_tests.py
```

### 运行特定的单元测试模块
```bash
python run_tests.py test_validation_logic
python run_tests.py test_column_mapping
python run_tests.py test_config_management
python run_tests.py test_merge_logic
```

### 运行所有集成测试
```bash
python run_integration_tests.py
```

### 运行特定类型的集成测试
```bash
python run_integration_tests.py workflow
python run_integration_tests.py api
python run_integration_tests.py report
```

### 运行单个测试文件
```bash
python -m unittest test_validation_logic.py
python -m unittest test_integration_workflow.py
```

## 测试覆盖范围

### 验证逻辑测试 (test_validation_logic.py)
- ✅ 有效DataFrame的验证
- ✅ 缺少必需列的处理
- ✅ 空item_id的检测
- ✅ 非数字价格的检测
- ✅ 可选列的处理
- ✅ 多个错误的处理
- ✅ 警告信息的生成
- ✅ 负价格的处理
- ✅ 修改建议的生成
- ✅ 增强验证逻辑
- ✅ 建议生成功能

### 列名映射测试 (test_column_mapping.py)
- ✅ 精确匹配
- ✅ 别名匹配
- ✅ 缺少必需列的处理
- ✅ 未映射列的处理
- ✅ 映射后DataFrame的创建
- ✅ 模糊匹配
- ✅ 大小写不敏感匹配
- ✅ 中英文混合映射
- ✅ 部分映射和建议
- ✅ 额外列的处理
- ✅ 配置加载功能

### 配置管理测试 (test_config_management.py)
- ✅ 配置文件的加载
- ✅ 配置文件的保存
- ✅ 列名映射配置的验证
- ✅ 无效配置的处理
- ✅ 默认配置的获取
- ✅ Unicode字符的支持

### API端点测试 (test_api_endpoints.py)
- ✅ 列名映射信息端点
- ✅ 列名映射示例端点
- ✅ 配置获取端点
- ✅ 配置更新端点
- ✅ 映射预览端点

### 工作流程集成测试 (test_integration_workflow.py)
- ✅ 完美规格表的上传工作流程
- ✅ 中文列名规格表的上传工作流程
- ✅ 英文列名规格表的上传工作流程
- ✅ 不完整规格表的处理工作流程
- ✅ 数据错误规格表的处理工作流程
- ✅ 规格表列表和删除工作流程
- ✅ 规格表验证工作流程
- ✅ 配置更改应用工作流程

### API集成测试 (test_integration_api.py)
- ✅ 上传文件用于映射的API
- ✅ 映射预览工作流程
- ✅ 映射确认工作流程
- ✅ 配置管理工作流程

### 行合并逻辑测试 (test_merge_logic.py)
- ✅ 独立的行合并函数实现
- ✅ DESCRIPTION字段合并测试
- ✅ 表头检测和处理
- ✅ 分割行识别和合并
- ✅ 边界情况处理

### 行合并功能测试 (test_row_merging.py)
- ✅ 集成测试行合并功能
- ✅ 与PDF转换器的集成
- ✅ 实际数据处理验证
- ✅ 边界情况测试

## 测试数据

测试使用以下类型的测试数据：

### 有效数据
- 包含所有必需列的完整规格表
- 使用标准列名的规格表
- 使用中文别名的规格表
- 使用英文别名的规格表

### 无效数据
- 缺少必需列的规格表
- 包含空值的规格表
- 包含无效数据类型的规格表
- 包含重复值的规格表

### 边界情况
- 空DataFrame
- 大数据集
- Unicode字符
- 特殊字符

## 测试环境

测试使用临时目录和模拟对象来隔离测试环境：

- 每个测试类都创建独立的临时目录
- 使用模拟的Flask应用和请求对象
- 配置文件路径被重定向到临时目录
- 测试完成后自动清理临时文件

## 测试最佳实践

1. **隔离性**: 每个测试都是独立的，不依赖其他测试的结果
2. **可重复性**: 测试可以在任何环境中重复运行
3. **清晰性**: 测试名称和结构清晰地表达了测试意图
4. **覆盖性**: 测试覆盖了正常情况、边界情况和错误情况
5. **维护性**: 测试代码易于理解和维护

## 故障排除

### 常见问题

1. **导入错误**: 确保Python路径正确设置
2. **临时文件问题**: 确保有足够的磁盘空间和权限
3. **模拟对象问题**: 检查模拟对象的配置是否正确

### 调试技巧

1. 使用`-v`参数运行测试以获得详细输出
2. 在测试中添加打印语句来调试
3. 使用Python调试器来逐步执行测试

## 持续集成

这些测试可以集成到CI/CD流水线中：

```bash
# 在CI环境中运行所有测试
python src/tests/run_tests.py
python src/tests/run_integration_tests.py
```

## 贡献指南

添加新测试时请遵循以下指南：

1. 为新功能添加相应的单元测试
2. 为新的API端点添加集成测试
3. 确保测试覆盖正常和异常情况
4. 使用描述性的测试名称
5. 添加必要的文档和注释
6. 确保测试在隔离环境中运行
7. 在提交前运行所有测试确保通过