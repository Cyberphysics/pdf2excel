# 🚨 NumPy/Pandas兼容性错误修复

## 问题
容器启动时报错：`ValueError: numpy.dtype size changed, may indicate binary incompatibility`

这是pandas和numpy版本不匹配导致的二进制兼容性问题。

## 🔧 立即修复 (在虚拟机上执行)

### 方案1: 兼容性修复 (推荐)
```bash
./vm_numpy_fix.sh
```

### 方案2: 最小化版本 (快速解决)
```bash
./vm_minimal_fix.sh
```

### 方案3: 手动修复
```bash
# 1. 停止当前容器
docker stop df909bb4cc8e
docker rm df909bb4cc8e

# 2. 创建兼容的requirements.txt
cat > requirements.txt << 'EOF'
Flask==2.3.3
flask-cors==4.0.0
Flask-SQLAlchemy==3.0.5
Werkzeug==2.3.7
numpy==1.24.3
pandas==2.0.3
openpyxl==3.1.2
pdfplumber==0.9.0
PyPDF2==3.0.1
python-dateutil==2.8.2
six==1.16.0
EOF

# 3. 创建分步安装的Dockerfile
cat > Dockerfile.fix << 'EOF'
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y build-essential default-jre ghostscript poppler-utils curl && rm -rf /var/lib/apt/lists/*

# 分步安装确保兼容性
RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 install --no-cache-dir numpy==1.24.3
RUN pip3 install --no-cache-dir pandas==2.0.3
RUN pip3 install --no-cache-dir Flask==2.3.3 flask-cors==4.0.0 Flask-SQLAlchemy==3.0.5 Werkzeug==2.3.7
RUN pip3 install --no-cache-dir openpyxl==3.1.2 pdfplumber==0.9.0 PyPDF2==3.0.1
RUN pip3 install --no-cache-dir python-dateutil==2.8.2 six==1.16.0

COPY . .
RUN mkdir -p uploads outputs data logs config
EXPOSE 5000
CMD ["python3", "-m", "src.main"]
EOF

# 4. 构建
docker build -f Dockerfile.fix --no-cache -t pdf2excel:latest .

# 5. 测试
docker run -d -p 5001:5000 --name pdf2excel-test pdf2excel:latest
sleep 15
curl http://localhost:5001/api/pdf/diagnose
```

### 方案4: 无pandas版本 (最快)
```bash
# 1. 停止容器
docker stop df909bb4cc8e && docker rm df909bb4cc8e

# 2. 创建无pandas的requirements.txt
cat > requirements.txt << 'EOF'
Flask==2.3.3
flask-cors==4.0.0
Flask-SQLAlchemy==3.0.5
Werkzeug==2.3.7
openpyxl==3.1.2
pdfplumber==0.9.0
PyPDF2==3.0.1
python-dateutil==2.8.2
six==1.16.0
EOF

# 3. 修改pdf_converter.py，移除pandas导入
sed -i 's/import pandas as pd/#import pandas as pd/' src/routes/pdf_converter.py
sed -i 's/import numpy as np/#import numpy as np/' src/routes/pdf_converter.py

# 4. 构建
docker build --no-cache -t pdf2excel:latest .

# 5. 测试
docker run -d -p 5001:5000 --name pdf2excel-test pdf2excel:latest
```

## ✅ 验证修复
```bash
# 检查服务状态
curl http://localhost:5001/api/pdf/diagnose

# 测试pandas导入 (如果使用方案1)
docker exec pdf2excel-test python3 -c "import pandas; import numpy; print('导入成功')"

# 查看日志
docker logs pdf2excel-test
```

## 🔍 问题分析
- **根因**: pandas 2.0.3 与 numpy 版本不匹配
- **影响**: 无法导入pandas，服务启动失败
- **解决**: 使用兼容的版本组合或移除pandas依赖

## 📋 版本兼容性
| NumPy | Pandas | 兼容性 |
|-------|--------|--------|
| 1.24.3 | 2.0.3 | ✅ 兼容 |
| 1.25.x | 2.0.3 | ❌ 不兼容 |
| 1.23.x | 2.0.3 | ✅ 兼容 |

---

**推荐执行顺序**:
1. 先尝试 `./vm_minimal_fix.sh` (最快)
2. 如需完整功能，再用 `./vm_numpy_fix.sh`