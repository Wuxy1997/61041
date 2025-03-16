# AI日历助手部署文档

## 部署架构

AI日历助手采用Docker容器化部署，主要包含以下组件：

1. **Flask Web应用**：提供用户界面和API接口
2. **Qwen2.5-0.5B-Instruct模型**：提供自然语言处理能力
3. **Google Calendar API集成**：实现日历功能

## 系统要求

### 硬件要求
- CPU: 4核或更高
- 内存: 至少8GB RAM
- 存储: 至少10GB可用空间

### 软件要求
- Docker Engine 20.10.0+
- Docker Compose 2.0.0+
- 互联网连接

## 详细部署步骤

### 1. 准备环境

确保系统已安装Docker和Docker Compose:

```bash
# 检查Docker版本
docker --version

# 检查Docker Compose版本
docker-compose --version
```

### 2. 获取项目代码

```bash
# 克隆代码仓库
git clone <repository-url>
cd ai-calendar-assistant
```

### 3. 配置Google API凭据

#### 3.1 创建Google Cloud项目
1. 访问[Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目
3. 记录项目ID

#### 3.2 启用Google Calendar API
1. 在Google Cloud Console中，导航至"API和服务" > "库"
2. 搜索"Google Calendar API"并启用

#### 3.3 配置OAuth同意屏幕
1. 导航至"API和服务" > "OAuth同意屏幕"
2. 选择用户类型（内部/外部）
3. 填写应用名称和必要信息
4. 添加范围：`https://www.googleapis.com/auth/calendar`
5. 添加测试用户

#### 3.4 创建OAuth客户端ID
1. 导航至"API和服务" > "凭据"
2. 点击"创建凭据" > "OAuth客户端ID"
3. 应用类型选择"桌面应用"
4. 下载JSON凭据文件

#### 3.5 配置应用凭据
```bash
# 创建凭据目录
mkdir -p credentials

# 复制凭据文件
cp /path/to/downloaded/client_secret.json credentials/client_secret.json
```

### 4. 构建和启动应用

```bash
# 构建Docker镜像并启动容器
docker-compose up -d --build
```

### 5. 验证部署

访问 http://localhost:8080 确认应用已成功启动。

### 6. 初始授权

1. 打开应用界面
2. 点击"连接Google日历"按钮
3. 完成Google账户授权流程

## 生产环境配置

### 环境变量配置

在生产环境中，建议通过环境变量配置敏感信息。可以创建`.env`文件或在`docker-compose.yml`中直接配置：

```yaml
services:
  ai-calendar-assistant:
    environment:
      - SECRET_KEY=your-secure-secret-key
      - MODEL_NAME=Qwen/Qwen2.5-0.5B-Instruct
      - PORT=8080
```

### HTTPS配置

在生产环境中，强烈建议配置HTTPS。可以使用Nginx作为反向代理：

1. 安装Nginx
2. 配置SSL证书
3. 创建Nginx配置文件：

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 持久化存储

确保Docker卷正确配置，以保存用户凭据和模型数据：

```yaml
volumes:
  credentials:
    driver: local
  models:
    driver: local
```

## 更新与维护

### 更新应用

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose down
docker-compose up -d --build
```

### 备份凭据

定期备份凭据目录：

```bash
# 备份凭据
docker cp $(docker-compose ps -q ai-calendar-assistant):/app/credentials /backup/credentials-$(date +%Y%m%d)
```

### 日志管理

查看应用日志：

```bash
# 查看实时日志
docker-compose logs -f

# 保存日志到文件
docker-compose logs > app-logs-$(date +%Y%m%d).log
```

## 故障排除

### 常见部署问题

1. **Docker构建失败**
   - 检查网络连接
   - 确认Docker服务正在运行
   - 检查磁盘空间是否充足

2. **应用启动失败**
   - 检查日志：`docker-compose logs`
   - 确认端口8080未被占用
   - 验证凭据文件路径正确

3. **OAuth认证失败**
   - 确认重定向URI配置正确
   - 检查Google Cloud项目中的API是否已启用
   - 验证OAuth同意屏幕配置

## 安全最佳实践

1. 定期更新依赖包
2. 使用强密码保护环境变量
3. 限制Docker容器的资源使用
4. 定期备份用户凭据
5. 监控应用日志以检测异常活动
