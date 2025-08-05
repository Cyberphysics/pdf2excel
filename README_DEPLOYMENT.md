# PDF转Excel服务 - 完整部署方案

## 🎯 **项目概述**

这是一个完整的PDF转Excel服务，支持从MacBook开发到生产环境的全流程部署。

### 核心功能
- ✅ PDF文件上传和处理
- ✅ 智能表格识别和提取
- ✅ Excel文件生成和下载
- ✅ 订单规格表比对功能
- ✅ RESTful API接口
- ✅ 响应式Web界面

### 技术栈
- **后端**: Python Flask
- **PDF处理**: pdfplumber, camelot, tabula
- **数据处理**: pandas, numpy
- **容器化**: Docker
- **部署**: DockerHub + 云服务

## 🔄 **部署流程架构**

```
MacBook (开发) → Git仓库 → 虚拟机 (构建) → DockerHub → 生产环境
     ↓              ↓           ↓            ↓          ↓
  本地开发        代码管理     镜像构建      镜像存储    服务部署
```

## 🚀 **快速开始**

### 1️⃣ **环境检查**
```bash
# 检查配置是否完整
./check_config.sh
```

### 2️⃣ **一键部署**
```bash
# 从MacBook部署到生产环境
./deploy_from_macbook.sh
```

### 3️⃣ **验证部署**
```bash
# 检查服务状态
curl http://your-domain.com/api/pdf/diagnose
```

## 📋 **详细配置步骤**

### MacBook端配置

1. **安装系统依赖**
```bash
brew install poppler ghostscript git python3
```

2. **配置环境变量**
```bash
# 添加到 ~/.zshrc
export VM_HOST="your-vm-ip"
export VM_USER="ubuntu"
export DOCKERHUB_USERNAME="your-dockerhub-username"
```

3. **配置Git仓库**
```bash
git remote add origin https://github.com/YOUR_USERNAME/pdf-to-excel-service.git
git push -u origin main
```

### 虚拟机端配置

1. **安装Docker**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

2. **登录DockerHub**
```bash
docker login
```

3. **配置环境变量**
```bash
export REPO_URL="https://github.com/YOUR_USERNAME/pdf-to-excel-service.git"
export DOCKERHUB_USERNAME="your-dockerhub-username"
```

## 🛠️ **可用脚本工具**

| 脚本 | 用途 | 执行环境 |
|------|------|----------|
| `check_config.sh` | 配置检查 | MacBook |
| `quick_start.py` | 本地测试 | MacBook |
| `deploy_from_macbook.sh` | 一键部署 | MacBook |
| `vm_complete_workflow.sh` | 构建推送 | 虚拟机 |
| `setup_and_test.sh` | 环境设置 | 任意 |
| `build_docker.sh` | Docker构建 | 虚拟机 |

## 📊 **API接口文档**

### 核心端点

#### 服务诊断
```bash
GET /api/pdf/diagnose
# 返回服务状态和PDF处理能力信息
```

#### 文件上传
```bash
POST /api/pdf/upload
Content-Type: multipart/form-data
# 上传PDF文件，返回file_id
```

#### PDF转换
```bash
POST /api/pdf/convert/{file_id}
# 将PDF转换为Excel，返回转换结果
```

#### 文件下载
```bash
GET /api/pdf/download/{file_id}
# 下载转换后的Excel文件
```

#### 规格表比对
```bash
POST /api/compare_orders
Content-Type: multipart/form-data
# 上传订单文件和规格表进行比对
```

### 使用示例

```bash
# 1. 上传PDF文件
curl -X POST -F "file=@sample.pdf" http://localhost:5000/api/pdf/upload

# 2. 转换为Excel
curl -X POST http://localhost:5000/api/pdf/convert/FILE_ID

# 3. 下载结果
curl -O http://localhost:5000/api/pdf/download/FILE_ID
```

## 🌐 **生产部署选项**

### 选项1: 直接Docker运行
```bash
docker run -d -p 80:5000 --name pdf2excel your-username/pdf2excel:latest
```

### 选项2: Docker Compose
```bash
# 使用 docker-compose.prod.yml
docker-compose -f docker-compose.prod.yml up -d
```

### 选项3: 云服务平台
- **Railway**: 连接GitHub仓库自动部署
- **Render**: 支持Docker镜像部署
- **DigitalOcean App Platform**: 容器化应用部署
- **AWS ECS**: 企业级容器服务

## 🔍 **监控和维护**

### 健康检查
```bash
# 服务状态
curl http://your-domain.com/api/pdf/diagnose

# 容器状态
docker ps
docker logs pdf2excel
```

### 更新部署
```bash
# 1. MacBook: 更新代码
git add . && git commit -m "update" && git push

# 2. 虚拟机: 重新构建
./vm_complete_workflow.sh

# 3. 生产环境: 更新服务
docker pull your-username/pdf2excel:latest
docker-compose -f docker-compose.prod.yml up -d
```

### 数据备份
```bash
# 备份数据卷
docker run --rm -v pdf2excel_data:/data -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz -C /data .
```

## 🛡️ **安全配置**

### 环境变量
```bash
# 生产环境建议配置
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=your-secret-key
MAX_CONTENT_LENGTH=100MB
```

### 网络安全
- 使用HTTPS (配置SSL证书)
- 限制文件上传大小
- 配置防火墙规则
- 定期更新依赖包

## 📈 **性能优化**

### 资源限制
```yaml
# docker-compose.prod.yml
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '1.0'
```

### 缓存策略
- 静态文件缓存
- API响应缓存
- 数据库查询优化

## 🔧 **故障排除**

### 常见问题

1. **依赖安装失败**
```bash
# 清理pip缓存
pip3 cache purge
pip3 install --no-cache-dir -r requirements.txt
```

2. **Docker构建失败**
```bash
# 清理Docker缓存
docker system prune -a
docker build --no-cache -t test .
```

3. **服务无法访问**
```bash
# 检查端口占用
lsof -i :5000
# 检查防火墙
sudo ufw status
```

4. **PDF处理失败**
```bash
# 检查系统依赖
pdfinfo -v
gs --version
java -version
```

## 📚 **相关文档**

- `SETUP_GUIDE.md` - 详细设置指南
- `DEPLOYMENT_WORKFLOW.md` - 部署流程说明
- `CURRENT_STATUS.md` - 项目状态总结
- `API_DOCUMENTATION.md` - API接口文档

## 🎉 **项目特色**

- ✅ **完整的开发到部署流程**
- ✅ **自动化构建和推送**
- ✅ **多种PDF处理引擎**
- ✅ **智能表格识别**
- ✅ **容器化部署**
- ✅ **生产级配置**
- ✅ **详细的文档和脚本**

---

## 🚀 **立即开始**

1. **检查配置**: `./check_config.sh`
2. **本地测试**: `python3 quick_start.py`
3. **一键部署**: `./deploy_from_macbook.sh`
4. **验证服务**: 访问你的域名

**祝你部署成功！** 🎊