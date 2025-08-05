# 🚨 紧急修复命令 - Flask-SQLAlchemy缺失

## 问题
容器启动时报错：`ModuleNotFoundError: No module named 'flask_sqlalchemy'`

## 🔧 立即修复 (在虚拟机上执行)

### 方案1: 使用修复脚本 (推荐)
```bash
./vm_emergency_fix.sh
```

### 方案2: 手动修复
```bash
# 1. 停止当前容器
docker stop $(docker ps -q)
docker rm $(docker ps -aq)

# 2. 修复requirements.txt
cat > requirements.txt << 'EOF'
Flask==2.3.3
flask-cors==4.0.0
Flask-SQLAlchemy==3.0.5
Werkzeug==2.3.7
pandas==2.0.3
numpy==1.24.3
openpyxl==3.1.2
pdfplumber==0.9.0
PyPDF2==3.0.1
python-dateutil==2.8.2
six==1.16.0
EOF

# 3. 重新构建
docker build --no-cache -t pdf2excel:latest .

# 4. 启动测试
docker run -d -p 5001:5000 --name pdf2excel-test pdf2excel:latest

# 5. 验证
sleep 10
curl http://localhost:5001/api/pdf/diagnose
```

### 方案3: 快速Dockerfile
```bash
# 创建简化Dockerfile
cat > Dockerfile.simple << 'EOF'
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y build-essential default-jre ghostscript poppler-utils curl && rm -rf /var/lib/apt/lists/*

# 直接安装必需包
RUN pip3 install --no-cache-dir Flask==2.3.3 flask-cors==4.0.0 Flask-SQLAlchemy==3.0.5 Werkzeug==2.3.7
RUN pip3 install --no-cache-dir pandas==2.0.3 numpy==1.24.3 openpyxl==3.1.2
RUN pip3 install --no-cache-dir pdfplumber==0.9.0 PyPDF2==3.0.1
RUN pip3 install --no-cache-dir python-dateutil==2.8.2 six==1.16.0

COPY . .
RUN mkdir -p uploads outputs data logs config
EXPOSE 5000
CMD ["python3", "-m", "src.main"]
EOF

# 构建
docker build -f Dockerfile.simple -t pdf2excel:latest .
```

## ✅ 验证修复
```bash
# 检查服务状态
curl http://localhost:5001/api/pdf/diagnose

# 查看容器日志
docker logs pdf2excel-test

# 进入容器检查
docker exec -it pdf2excel-test python3 -c "import flask_sqlalchemy; print('Flask-SQLAlchemy OK')"
```

## 🚀 修复后的下一步
```bash
# 1. 标记镜像
docker tag pdf2excel:latest your-username/pdf2excel:latest

# 2. 推送到DockerHub
docker push your-username/pdf2excel:latest

# 3. 生产部署
docker run -d -p 80:5000 --name pdf2excel your-username/pdf2excel:latest
```

---

**立即执行**: `./vm_emergency_fix.sh` 一键修复所有问题！