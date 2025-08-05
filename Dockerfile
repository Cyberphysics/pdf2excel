# 使用官方Python 3.11镜像作为基础镜像
FROM python:3.11-slim

# 设置非交互模式
ENV DEBIAN_FRONTEND=noninteractive

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    default-jre \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    libssl-dev \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    tk-dev \
    tcl-dev \
    ghostscript \
    poppler-utils \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 设置Java环境变量
ENV JAVA_HOME=/usr/lib/jvm/default-java

# 复制requirements文件
COPY requirements.txt .

# 升级pip并安装Python依赖
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录
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