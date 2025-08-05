# 使用官方Python 3.11镜像
FROM python:3.11-slim

# 设置环境变量
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 设置工作目录
WORKDIR /app

# 安装系统依赖 (仅必需的)
RUN apt-get update && apt-get install -y \
    build-essential \
    default-jre \
    ghostscript \
    poppler-utils \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 设置Java环境
ENV JAVA_HOME=/usr/lib/jvm/default-java

# 复制requirements文件
COPY requirements.txt .

# 升级pip
RUN pip3 install --no-cache-dir --upgrade pip

# 分步安装Python依赖 (确保兼容性)
# 1. 先安装numpy (pandas的依赖)
RUN pip3 install --no-cache-dir numpy==1.24.3

# 2. 安装pandas (依赖numpy)
RUN pip3 install --no-cache-dir pandas==2.0.3

# 3. 安装Flask相关
RUN pip3 install --no-cache-dir \
    Flask==2.3.3 \
    flask-cors==4.0.0 \
    Flask-SQLAlchemy==3.0.5 \
    Werkzeug==2.3.7

# 4. 安装Excel和PDF处理
RUN pip3 install --no-cache-dir \
    openpyxl==3.1.2 \
    pdfplumber==0.9.0 \
    PyPDF2==3.0.1

# 5. 安装其他依赖
RUN pip3 install --no-cache-dir \
    python-dateutil==2.8.2 \
    six==1.16.0 \
    requests==2.31.0

# 复制应用代码
COPY . .

# 创建必要目录
RUN mkdir -p uploads outputs data logs config

# 设置权限
RUN chmod -R 755 /app

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/pdf/diagnose || exit 1

# 启动应用
CMD ["python3", "-m", "src.main"]