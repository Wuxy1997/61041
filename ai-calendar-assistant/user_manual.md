# AI日历助手使用说明文档

## 项目概述

AI日历助手是一个基于Docker部署的智能应用，集成了Qwen2.5-0.5B-Instruct模型和Google Calendar API，能够帮助用户通过自然语言交互管理和标记日历中的重要事件。

### 主要功能

- 自然语言理解：理解用户的日历相关指令
- 日历事件查询：查看即将到来的事件
- 事件创建：通过自然语言创建新的日历事件
- 重要事件标记：将特定事件标记为重要
- 用户友好界面：提供简洁直观的Web交互界面

## 安装指南

### 前提条件

- Docker 和 Docker Compose
- Google Cloud Platform 账号
- 网络连接

### 获取Google API凭据

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用 Google Calendar API
4. 配置 OAuth 同意屏幕
5. 创建 OAuth 客户端 ID（选择"桌面应用"类型）
6. 下载凭据 JSON 文件，重命名为 `client_secret.json`

### 部署步骤

1. 克隆代码仓库：
   ```bash
   git clone <repository-url>
   cd ai-calendar-assistant
   ```

2. 将 `client_secret.json` 文件放入 `credentials` 目录：
   ```bash
   mkdir -p credentials
   cp /path/to/client_secret.json credentials/
   ```

3. 使用 Docker Compose 构建并启动应用：
   ```bash
   docker-compose up -d
   ```

4. 访问应用：
   打开浏览器，访问 http://localhost:8080

## 使用指南

### 首次使用

1. 打开应用后，点击右侧的"连接Google日历"按钮
2. 按照提示完成 Google 账户授权
3. 授权成功后，页面会自动返回到应用主界面

### 日常使用

#### 查询日历事件

示例指令：
- "查看我今天的日程"
- "显示我本周的会议"
- "下周我有什么安排？"

#### 创建新事件

示例指令：
- "创建一个明天下午3点到5点的产品会议"
- "帮我安排周五上午10点与张三的电话会议"
- "下周一早上9点添加一个重要的客户会议"

#### 标记重要事件

示例指令：
- "将明天的产品会议标记为重要"
- "把周五的电话会议设为重要事件"

## 故障排除

### 常见问题

1. **应用无法启动**
   - 检查 Docker 和 Docker Compose 是否正确安装
   - 确认端口 8080 未被其他应用占用

2. **无法连接 Google 日历**
   - 确认 `client_secret.json` 文件位置正确
   - 检查 Google Cloud Console 中的 API 是否已启用
   - 确认 OAuth 同意屏幕配置正确

3. **模型加载失败**
   - 检查网络连接是否正常
   - 确认系统内存足够加载模型

### 日志查看

查看应用日志：
```bash
docker-compose logs -f ai-calendar-assistant
```

## 隐私与安全

- 所有 Google 认证凭据安全存储在 Docker 卷中
- 应用不会将您的日历数据发送给第三方
- 模型推理在本地进行，不依赖外部服务

## 技术支持

如有任何问题或需要技术支持，请联系：support@example.com
