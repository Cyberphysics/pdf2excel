# PDF to Excel Converter Service

一个强大的PDF转Excel转换服务，专为汽车配件公司设计，支持智能表格识别、多行描述合并和订单规格比对功能。

## 🌟 主要特性

### 核心功能
- **智能PDF解析**: 自动识别PDF中的客户信息、订单表格和总结三个部分
- **多行合并**: 智能合并被分割的DESCRIPTION字段为单个单元格
- **标准化表头**: 统一使用8个标准字段格式
- **多工作表输出**: 自动生成包含三个工作表的Excel文件
- **订单规格比对**: 支持订单与产品规格表的智能比对

### 技术特性
- **多PDF引擎**: 支持Camelot、Tabula、pdfplumber等多种PDF处理引擎
- **智能回退**: 当一种方法失败时自动尝试其他方法
- **Docker支持**: 完整的容器化部署方案
- **RESTful API**: 完整的REST API接口
- **实时预览**: 支持文件预览和进度查询

## 📋 标准表头格式

系统使用以下8个标准字段：

| 字段 | 说明 |
|------|------|
| ITEM | 项目编号 |
| EXTERNAL ITEM NUMBER | 外部项目编号 |
| DESCRIPTION | 产品描述 |
| DELIVERY DATE | 交付日期 |
| UNIT | 单位 |
| QUANTITY | 数量 |
| PRICE | 单价 |
| AMOUNT | 总价 |

## 🔧 PDF处理引擎

系统集成了多种PDF处理库，按优先级自动选择最佳引擎：

### 文本提取引擎
1. **pdfplumber** (推荐) - 高精度文本提取
2. **pdfminer.six** - 备选文本提取引擎
3. **PyPDF2** - 兼容性文本提取

### 表格提取引擎
1. **Camelot** - 专业表格提取（支持lattice和stream模式）
2. **Tabula** - 备选表格提取引擎

### 增强PDF解析器
- **三部分内容识别**：自动分离客户信息、订单表格、总结信息
- **多工作表Excel生成**：为每个部分创建独立工作表
- **智能关键词识别**：基于中英文关键词自动识别内容区域
- **结构化数据提取**：自动解析客户信息和财务汇总数据

## 🚀 快速开始

### 使用Docker部署（推荐）

1. **克隆项目**
```bash
git clone git@github.com:Cyberphysics/pdf2excel.git
cd pdf2excel
```

2. **构建并启动服务**
```bash
# 使用docker-compose一键部署
docker-compose up -d

# 或者手动构建
docker build -t pdf2excel .
docker run -d -p 5000:5000 --name pdf2excel-service pdf2excel
```

3. **验证部署**
```bash
# 检查服务状态
curl http://localhost:5000/api/pdf/diagnose

# 查看容器日志
docker-compose logs -f
```

### 本地开发部署

1. **环境要求**
- Python 3.8+
- Java Runtime Environment (JRE) - Tabula依赖
- Ghostscript - PDF处理支持
- Poppler Utils - PDF工具集

2. **安装系统依赖**

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip default-jre ghostscript poppler-utils
```

**macOS:**
```bash
brew install python3 openjdk ghostscript poppler
```

3. **安装Python依赖**
```bash
pip install -r requirements.txt
```

4. **验证PDF处理能力**
```bash
# 启动服务后检查PDF处理库状态
curl http://localhost:5000/api/pdf/diagnose
```

5. **启动服务**
```bash
python -m src.main
```

### 快速测试脚本

项目提供了一个快速启动测试脚本，可以自动检查依赖并启动服务：

```bash
# 快速启动和测试
python3 quick_start.py
```

该脚本会：
- 自动检查关键Python依赖
- 启动PDF转Excel服务
- 测试基本API端点
- 提供服务诊断信息
- 保持服务运行直到手动停止

## 📁 项目结构

```
pdf2excel/
├── src/                    # 源代码
│   ├── routes/            # API路由
│   ├── utils/             # 工具模块
│   ├── models/            # 数据模型
│   └── static/            # 静态文件
├── uploads/               # 上传文件存储
├── outputs/               # 输出文件存储
├── data/                  # 数据库文件
├── logs/                  # 日志文件
├── config/                # 配置文件
├── Dockerfile             # Docker配置
├── docker-compose.yml     # Docker Compose配置
├── requirements.txt       # Python依赖
└── README.md             # 项目文档
```

## 🔧 API接口

### 文件上传和转换

```bash
# 上传PDF文件
curl -X POST -F "file=@order.pdf" http://localhost:5000/api/pdf/upload

# 转换PDF为Excel
curl -X POST http://localhost:5000/api/pdf/convert/{file_id}

# 下载转换后的Excel文件
curl -O http://localhost:5000/api/pdf/download/{file_id}
```

### 文件管理

```bash
# 获取已转换文件列表
curl http://localhost:5000/api/pdf/list_converted

# 预览转换后的文件
curl http://localhost:5000/api/pdf/preview_converted/{file_id}

# 获取文件状态
curl http://localhost:5000/api/pdf/status/{file_id}

# 删除文件
curl -X DELETE http://localhost:5000/api/pdf/delete_converted/{file_id}
```

### 诊断和测试

```bash
# 检查PDF处理能力
curl http://localhost:5000/api/pdf/diagnose

# 测试特定PDF的解析能力
curl http://localhost:5000/api/pdf/test_pdf/{file_id}
```

### 订单规格比对

```bash
# 上传规格表
curl -X POST -F "file=@spec.xlsx" http://localhost:5000/api/upload_spec

# 比对订单与规格表
curl -X POST http://localhost:5000/api/compare_orders \
  -H "Content-Type: application/json" \
  -d '{"order_file_id": "order_id", "spec_file_id": "spec_id"}'

# 下载比对结果
curl -O http://localhost:5000/api/download_comparison/{result_id}
```

## 🔍 使用示例

### 1. 基本PDF转换流程

```python
import requests

# 1. 上传PDF文件
with open('order.pdf', 'rb') as f:
    response = requests.post('http://localhost:5000/api/pdf/upload', 
                           files={'file': f})
    file_id = response.json()['file_id']

# 2. 转换PDF为Excel
response = requests.post(f'http://localhost:5000/api/pdf/convert/{file_id}')
print(response.json())

# 3. 下载Excel文件
response = requests.get(f'http://localhost:5000/api/pdf/download/{file_id}')
with open('converted.xlsx', 'wb') as f:
    f.write(response.content)
```

### 2. 检查PDF解析能力

```python
import requests

# 检查系统PDF处理能力
response = requests.get('http://localhost:5000/api/pdf/diagnose')
capabilities = response.json()

print("可用的PDF库:")
for lib, available in capabilities['pdf_libraries'].items():
    status = "✅" if available else "❌"
    print(f"  {status} {lib}")
```

## 🐳 Docker部署详解

### 环境变量配置

```yaml
# docker-compose.yml
environment:
  - FLASK_ENV=production
  - JAVA_HOME=/usr/lib/jvm/default-java
  - PYTHONPATH=/app
```

### 数据持久化

```yaml
# 挂载数据目录
volumes:
  - ./uploads:/app/uploads      # 上传文件
  - ./outputs:/app/outputs      # 输出文件
  - ./data:/app/data           # 数据库文件
  - ./logs:/app/logs           # 日志文件
  - ./config:/app/config       # 配置文件
```

### 健康检查

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/api/pdf/diagnose"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

## 🔧 故障排除

### 常见问题

1. **PDF解析失败**
```bash
# 检查PDF处理库状态
curl http://localhost:5000/api/pdf/diagnose

# 测试特定PDF文件
curl http://localhost:5000/api/pdf/test_pdf/{file_id}
```

2. **Docker容器启动失败**
```bash
# 查看容器日志
docker-compose logs pdf2excel

# 检查容器状态
docker-compose ps
```

3. **Java环境问题**
```bash
# 进入容器检查Java
docker exec -it pdf2excel-service bash
java -version
echo $JAVA_HOME
```

### 性能优化

1. **内存设置**
```yaml
# docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
    reservations:
      memory: 1G
```

2. **并发处理**
```python
# 在src/main.py中配置
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
```

## 📊 监控和日志

### 日志配置

日志文件位置：
- 应用日志: `logs/app.log`
- 错误日志: `logs/error.log`
- 访问日志: `logs/access.log`

### 监控指标

```bash
# 检查服务健康状态
curl http://localhost:5000/api/pdf/diagnose

# 查看文件处理统计
curl http://localhost:5000/api/pdf/list_converted
```

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 支持

如果您遇到问题或有疑问，请：

1. 查看 [故障排除](#-故障排除) 部分
2. 检查 [Issues](https://github.com/Cyberphysics/pdf2excel/issues)
3. 创建新的 Issue 描述您的问题

## 🔄 更新日志

### v2.0.0 (2025-07-30)
- ✨ 新增增强PDF解析器，支持三部分识别
- ✨ 新增多工作表Excel输出
- ✨ 新增Docker完整支持
- ✨ 新增诊断和测试API
- ✨ 优化依赖管理，按功能分组
- ✨ 增强PDF处理库支持（pdfplumber、pdfminer、PyPDF2）
- ✨ 智能PDF处理引擎选择和回退机制
- 🐛 修复Docker环境PDF解析问题
- 🔧 优化目录结构，符合业界标准
- 🔧 统一JSON序列化安全处理

### v1.0.0
- 🎉 初始版本发布
- ✨ 基础PDF转Excel功能
- ✨ 订单规格比对功能