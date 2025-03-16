FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 创建目录结构
RUN mkdir -p /app/models /app/credentials /app/static /app/templates

# 复制应用代码
COPY . .

# 设置环境变量
ENV MODEL_PATH=/app/models
ENV CLIENT_SECRET_FILE=/app/credentials/client_secret.json
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["python", "app.py"]
