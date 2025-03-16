# AI日历助手

一个基于Docker部署的智能助手，集成Qwen2.5-0.5B-Instruct模型和Google Calendar API，帮助用户通过自然语言交互管理日历事件。

## 项目特点

- 🤖 集成Qwen2.5-0.5B-Instruct模型进行自然语言处理
- 📅 连接Google Calendar API管理日历事件
- 🔍 查询即将到来的日历事件
- ➕ 通过自然语言创建新事件
- ⭐ 标记重要日历事件
- 🔒 安全的OAuth2.0认证流程
- 🐳 完整的Docker部署方案

## 快速开始

### 前提条件

- Docker 和 Docker Compose
- Google Cloud Platform 账号
- 网络连接

### 部署步骤

1. 克隆代码仓库
   ```bash
   git clone <repository-url>
   cd ai-calendar-assistant
   ```

2. 配置Google API凭据
   - 在[Google Cloud Console](https://console.cloud.google.com/)创建项目
   - 启用Google Calendar API
   - 配置OAuth同意屏幕
   - 创建OAuth客户端ID（选择"桌面应用"类型）
   - 下载凭据JSON文件，重命名为`client_secret.json`
   - 将凭据文件放入`credentials`目录
   ```bash
   mkdir -p credentials
   cp /path/to/client_secret.json credentials/
   ```

3. 启动应用
   ```bash
   docker-compose up -d
   ```

4. 访问应用
   - 打开浏览器，访问 http://localhost:8080
   - 点击"连接Google日历"按钮完成授权

## 使用示例

### 查询日历事件
```
查看我今天的日程
显示我本周的会议
下周我有什么安排？
```

### 创建新事件
```
创建一个明天下午3点到5点的产品会议
帮我安排周五上午10点与张三的电话会议
下周一早上9点添加一个重要的客户会议
```

### 标记重要事件
```
将明天的产品会议标记为重要
把周五的电话会议设为重要事件
```

## 项目结构

```
ai-calendar-assistant/
├── app.py                 # 主应用文件
├── calendar_api.py        # Google Calendar API集成
├── Dockerfile             # Docker配置文件
├── docker-compose.yml     # Docker Compose配置
├── requirements.txt       # Python依赖
├── templates/             # 前端模板
│   └── index.html         # 主页模板
├── credentials/           # 存放Google API凭据
├── models/                # 存放LLM模型
├── test_app.py            # 单元测试
├── run_tests.sh           # 测试脚本
├── user_manual.md         # 用户手册
└── deployment_guide.md    # 部署指南
```

## 文档

- [用户手册](user_manual.md) - 详细的使用指南
- [部署指南](deployment_guide.md) - 完整的部署文档

## 技术栈

- **后端**: Python, Flask
- **AI模型**: Qwen2.5-0.5B-Instruct
- **API集成**: Google Calendar API
- **容器化**: Docker, Docker Compose
- **认证**: OAuth 2.0

## 贡献

欢迎提交问题和改进建议！

## 许可证

MIT
