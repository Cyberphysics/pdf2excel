# 🚨 虚拟机依赖冲突快速修复

## 问题描述
Docker构建时出现pdfminer.six版本冲突：
```
ERROR: Cannot install pdfminer.six==20250506 because:
pdfplumber 0.9.0 depends on pdfminer.six==20221105
```

## 🔧 立即修复方案

### 方案1: 使用修复脚本 (推荐)
```bash
# 在虚拟机上执行
cd pdf-to-excel-service
chmod +x vm_fix_dependencies.sh
./vm_fix_dependencies.sh
```

### 方案2: 手动修复
```bash
# 1. 清理Docker缓存
docker builder prune -f
docker system prune -f

# 2. 创建修复后的requirements.txt
cat > requirements.txt << 'EOF'
# Flask核心框架
Flask==2.3.3
flask-cors==4.0.0
Flask-SQLAlchemy==3.0.5
Werkzeug==2.3.7

# 数据处理
pandas==2.0.3
numpy==1.24.3
openpyxl==3.1.2

# PDF文本提取库 (兼容版本)
pdfplumber==0.9.0
# 重要：不指定pdfminer.six版本，让pdfplumber自动管理
PyPDF2==3.0.1

# PDF表格提取库
camelot-py[cv]==0.10.1
tabula-py==2.7.0

# 图像处理依赖
opencv-python-headless==4.8.0.76

# 其他依赖
requests==2.31.0
python-dateutil==2.8.2
pytz==2023.3
six==1.16.0
EOF

# 3. 重新构建
docker build --no-cache -t pdf2excel:latest .
```

### 方案3: 分步安装Dockerfile
```bash
# 创建优化的Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential default-jre libxml2-dev libxslt1-dev \
    libffi-dev libssl-dev zlib1g-dev libjpeg-dev libpng-dev \
    libfreetype6-dev liblcms2-dev libopenjp2-7-dev libtiff5-dev \
    tk-dev tcl-dev ghostscript poppler-utils libgl1-mesa-glx \
    libglib2.0-0 fonts-dejavu-core fonts-liberation curl \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/default-java

COPY requirements.txt .

# 分步安装避免冲突
RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 install --no-cache-dir Flask==2.3.3 flask-cors==4.0.0 Flask-SQLAlchemy==3.0.5 Werkzeug==2.3.7
RUN pip3 install --no-cache-dir pandas==2.0.3 numpy==1.24.3 openpyxl==3.1.2
RUN pip3 install --no-cache-dir pdfplumber==0.9.0
RUN pip3 install --no-cache-dir PyPDF2==3.0.1
RUN pip3 install --no-cache-dir opencv-python-headless==4.8.0.76
RUN pip3 install --no-cache-dir camelot-py[cv]==0.10.1
RUN pip3 install --no-cache-dir tabula-py==2.7.0
RUN pip3 install --no-cache-dir requests==2.31.0 python-dateutil==2.8.2 pytz==2023.3 six==1.16.0

COPY . .
RUN mkdir -p uploads outputs data logs config
RUN chmod -R 755 /app

EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/pdf/diagnose || exit 1

CMD ["python3", "-m", "src.main"]
EOF

# 构建镜像
docker build --no-cache -t pdf2excel:latest .
```

## 🧪 测试验证
```bash
# 测试镜像
docker run -d --name pdf2excel-test -p 5001:5000 pdf2excel:latest
sleep 15
curl http://localhost:5001/api/pdf/diagnose

# 清理测试
docker stop pdf2excel-test
docker rm pdf2excel-test
```

## 🚀 推送到DockerHub
```bash
# 标记镜像
docker tag pdf2excel:latest your-username/pdf2excel:latest

# 推送镜像
docker push your-username/pdf2excel:latest
```

## 🔍 问题根因
1. **版本冲突**: pdfplumber 0.9.0 严格依赖 pdfminer.six==20221105
2. **缓存问题**: Docker构建缓存可能包含旧的依赖信息
3. **安装顺序**: 同时安装冲突包会导致解析失败

## ✅ 修复要点
1. **移除显式版本**: 不要手动指定pdfminer.six版本
2. **分步安装**: 先安装pdfplumber，让它管理pdfminer.six
3. **清理缓存**: 使用--no-cache-dir避免缓存问题
4. **兼容版本**: 使用经过测试的稳定版本组合

---

**立即执行**: `./vm_fix_dependencies.sh` 一键修复所有问题！