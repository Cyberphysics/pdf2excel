# 本地运行指南

## 🚨 **相对导入错误修复** (已解决)

### 问题
```
ImportError: attempted relative import with no known parent package
```

### ✅ **解决方案** (已在代码中实现自动fallback)

#### 方案1: 使用正确的运行方式 (推荐)
```bash
# 在项目根目录运行
cd pdf-to-excel-service
python3 -m src.main
```

#### 方案2: 使用本地运行脚本
```bash
# 使用专门的本地运行脚本
python3 run_local.py
```

#### 方案3: 设置环境变量
```bash
# 设置PYTHONPATH
export PYTHONPATH=/path/to/pdf-to-excel-service
python3 src/main.py
```

#### 方案4: 直接修改sys.path (已实现)
```python
# ✅ 已在src/main.py中实现自动fallback机制
# 现在可以直接运行: python3 src/main.py
```

## 🎯 **推荐的开发流程**

### MacBook本地开发
```bash
# 1. 安装依赖
pip3 install -r requirements.txt

# 2. 启动服务 (多种方式都支持)
python3 -m src.main        # 推荐方式
# 或
python3 src/main.py        # 现在也支持 (已添加fallback)
# 或
python3 run_local.py       # 使用本地运行脚本

# 3. 访问服务
open http://localhost:5000
```

### Docker开发 (推荐用于生产环境测试)
```bash
# 1. 构建镜像
docker build -t pdf2excel .

# 2. 运行容器
docker run -d -p 5000:5000 --name pdf2excel-dev pdf2excel

# 3. 查看日志
docker logs -f pdf2excel-dev
```

## 🔍 **问题原因**

Python的相对导入 (`from .utils import ...`) 只能在包内使用，当直接运行文件时，Python不知道包的结构。

### 正确的项目结构理解
```
pdf-to-excel-service/          # 项目根目录
├── src/                       # Python包
│   ├── __init__.py           # 包标识文件
│   ├── main.py               # 主模块
│   ├── routes/               # 路由包
│   └── utils/                # 工具包
├── requirements.txt
└── Dockerfile
```

### 运行方式对比
```bash
# ✅ 推荐方式 (模块方式运行)
python3 -m src.main

# ✅ 现在也支持 (直接运行，已添加fallback机制)
python3 src/main.py

# ✅ 使用本地运行脚本
python3 run_local.py
```

## 💡 **开发建议**

1. **本地开发**: 使用 `python3 -m src.main`
2. **生产环境**: 使用Docker容器
3. **调试**: 使用 `run_local.py` 脚本
4. **IDE配置**: 设置项目根目录为工作目录

---

**快速启动**: `python3 run_local.py` 或 `python3 -m src.main`