#!/bin/bash

# 测试脚本：验证AI日历助手的功能

echo "开始测试AI日历助手..."

# 1. 测试Docker环境
echo "测试Docker环境..."
if ! command -v docker &> /dev/null || ! command -v docker-compose &> /dev/null; then
    echo "错误: Docker或Docker Compose未安装"
    exit 1
fi
echo "Docker环境检查通过"

# 2. 测试Python依赖
echo "测试Python依赖..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "错误: Python依赖安装失败"
    exit 1
fi
echo "Python依赖安装成功"

# 3. 运行单元测试
echo "运行单元测试..."
python3 -m unittest test_app.py
if [ $? -ne 0 ]; then
    echo "错误: 单元测试失败"
    exit 1
fi
echo "单元测试通过"

# 4. 测试应用启动
echo "测试应用启动..."
# 在后台启动应用
python3 app.py &
APP_PID=$!

# 等待应用启动
sleep 5

# 检查应用是否正常运行
curl -s http://localhost:8080/health | grep "ok" > /dev/null
if [ $? -ne 0 ]; then
    echo "错误: 应用启动失败"
    kill $APP_PID
    exit 1
fi
echo "应用启动成功"

# 5. 测试基本API
echo "测试基本API..."
# 测试聊天API
RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -d '{"message":"你好"}' http://localhost:8080/chat)
if [[ ! $RESPONSE == *"response"* ]]; then
    echo "错误: 聊天API测试失败"
    kill $APP_PID
    exit 1
fi
echo "基本API测试通过"

# 6. 清理
echo "清理测试环境..."
kill $APP_PID

echo "所有测试完成，AI日历助手功能正常！"
