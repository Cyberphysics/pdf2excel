FROM ubuntu:20.04

# 设置非交互模式
ENV DEBIAN_FRONTEND=noninteractive

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    default-jre \
    ghostscript \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    fonts-dejavu-core \
    fonts-liberation \
    libgomp1 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# 设置Java环境变量
ENV JAVA_HOME=/usr/lib/jvm/default-java

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip3 install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p uploads outputs data logs config

# 设置权限
RUN chmod -R 755 /app

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/pdf/diagnose || exit 1

# 启动应用
CMD ["python3", "-m", "src.main"]