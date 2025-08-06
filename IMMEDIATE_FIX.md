# 🚨 立即修复 - Dockerfile语法错误

## 问题分析
错误信息显示Dockerfile中有语法错误和camelot-py包问题：
1. Dockerfile语法错误：RUN命令格式不正确
2. camelot-py包本身有问题：`NameError: name 'file' is not defined`

## 🔧 立即修复 (在虚拟机上执行)

### 方案1: 使用紧急构建脚本 (推荐)
```bash
./emergency_build.sh
```

### 方案2: 手动修复
```bash
# 1. 停止并清理
docker stop $(docker ps -q) 2>/dev/null || true
docker rm $(docker ps -aq) 2>/dev/null || true
docker system prune -f

# 2. 创建干净的Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    default-jre \
    ghostscript \
    poppler-utils \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

ENV JAVA_HOME=/usr/lib/jvm/default-java

RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 install --no-cache-dir numpy==1.24.3
RUN pip3 install --no-cache-dir pandas==2.0.3
RUN pip3 install --no-cache-dir Flask==2.3.3 flask-cors==4.0.0 Flask-SQLAlchemy==3.0.5 Werkzeug==2.3.7
RUN pip3 install --no-cache-dir openpyxl==3.1.2 pdfplumber==0.9.0 PyPDF2==3.0.1
RUN pip3 install --no-cache-dir python-dateutil==2.8.2 six==1.16.0 requests==2.31.0

COPY . .
RUN mkdir -p uploads outputs data logs config
RUN chmod -R 755 /app

EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/pdf/diagnose || exit 1

CMD ["python3", "-m", "src.main"]
EOF

# 3. 构建镜像
docker build --no-cache -t pdf2excel:latest .

# 4. 启动测试
docker run -d -p 5000:5000 --name pdf2excel-test pdf2excel:latest

# 5. 验证
sleep 15
curl http://localhost:5000/api/pdf/diagnose
```

### 方案3: 最简化版本
```bash
# 如果还有问题，使用最简化的requirements.txt
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
requests==2.31.0
EOF

# 然后重新构建
docker build --no-cache -t pdf2excel:latest .
```

## ✅ 验证修复
```bash
# 检查容器状态
docker ps

# 检查服务
curl http://localhost:5000/api/pdf/diagnose

# 查看日志
docker logs pdf2excel-test
```

## 🔍 问题根因
1. **Dockerfile语法**: 可能有隐藏字符或格式问题
2. **camelot-py包**: 这个包本身有Python 3.11兼容性问题
3. **构建缓存**: 可能使用了旧的构建缓存

## 💡 解决策略
- ✅ 移除problematic的camelot-py依赖
- ✅ 使用经过验证的核心依赖
- ✅ 清理构建缓存
- ✅ 分步安装避免冲突

---

**立即执行**: `./emergency_build.sh` 使用干净配置一键构建！