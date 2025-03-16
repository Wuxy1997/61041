import os
import json
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import datetime
import logging
from calendar_api import (
    get_credentials, save_credentials, create_flow, 
    get_calendar_service, list_upcoming_events, 
    create_event, mark_event_as_important
)
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-for-session')

# 全局变量
model = None
tokenizer = None

# Google Calendar API 配置
SCOPES = ['https://www.googleapis.com/auth/calendar']
CLIENT_SECRET_FILE = os.environ.get('CLIENT_SECRET_FILE', '/app/credentials/client_secret.json')

def load_model():
    """加载LLM模型"""
    global model, tokenizer
    
    model_name = os.environ.get('MODEL_NAME', 'Qwen/Qwen2.5-0.5B-Instruct')
    model_path = os.environ.get('MODEL_PATH', '/app/models')
    
    logger.info(f"正在加载模型: {model_name}")
    
    try:
        # 尝试从本地加载模型
        if os.path.exists(os.path.join(model_path, 'config.json')):
            model = AutoModelForCausalLM.from_pretrained(model_path, device_map='auto')
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            logger.info("已从本地路径加载模型")
        else:
            # 从Hugging Face下载模型
            model = AutoModelForCausalLM.from_pretrained(model_name, device_map='auto')
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            # 保存模型到本地
            model.save_pretrained(model_path)
            tokenizer.save_pretrained(model_path)
            logger.info(f"已从Hugging Face下载模型并保存到: {model_path}")
            
        return True
    except Exception as e:
        logger.error(f"模型加载失败: {str(e)}")
        return False

def generate_response(prompt, max_length=512):
    """使用LLM生成响应"""
    try:
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=max_length,
                num_return_sequences=1,
                temperature=0.7,
                top_p=0.9,
                do_sample=True
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # 移除输入提示，只保留生成的回复
        if response.startswith(prompt):
            response = response[len(prompt):].strip()
            
        return response
    except Exception as e:
        logger.error(f"生成响应时出错: {str(e)}")
        return "抱歉，我无法处理您的请求。"

def process_calendar_intent(user_input):
    """处理与日历相关的意图"""
    # 检查是否已授权
    if not get_credentials():
        return "您需要先授权访问Google日历才能使用此功能。请点击右侧的'连接Google日历'按钮进行授权。"
    
    # 使用LLM分析用户意图
    prompt = f"""分析以下用户输入，确定用户想要执行的日历操作类型（查询事件、创建事件、标记重要事件）。
如果是创建事件，提取事件标题、开始时间、结束时间、地点（如有）和描述（如有）。
如果是查询事件，确定查询的时间范围。
如果是标记重要事件，提取事件标题或ID。
用户输入: {user_input}
分析结果:"""
    
    intent_analysis = generate_response(prompt)
    
    # 根据意图执行相应操作
    if "查询事件" in intent_analysis:
        events = list_upcoming_events(10)
        if not events:
            return "未找到即将到来的事件。"
        
        events_text = "以下是您即将到来的事件：\n"
        for i, event in enumerate(events):
            start = event['start'].get('dateTime', event['start'].get('date'))
            events_text += f"{i+1}. {event['summary']} ({start})\n"
        
        return events_text
    
    elif "创建事件" in intent_analysis:
        # 这里需要更复杂的解析逻辑，简化处理
        # 实际应用中应该使用更强大的NLP来提取事件详情
        try:
            # 提取事件信息
            lines = intent_analysis.split('\n')
            event_info = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    event_info[key.strip()] = value.strip()
            
            if '标题' in event_info and '开始时间' in event_info and '结束时间' in event_info:
                event = create_event(
                    summary=event_info.get('标题'),
                    start_time=event_info.get('开始时间'),
                    end_time=event_info.get('结束时间'),
                    description=event_info.get('描述', ''),
                    location=event_info.get('地点', ''),
                    is_important='重要' in user_input
                )
                
                if event:
                    return f"已成功创建事件：{event_info.get('标题')}"
            
            return "创建事件失败，请提供完整的事件信息（标题、开始时间和结束时间）。"
        except Exception as e:
            logger.error(f"创建事件时出错: {str(e)}")
            return "创建事件时出错，请重试。"
    
    elif "标记重要" in intent_analysis:
        # 简化处理，实际应用中需要更复杂的逻辑
        events = list_upcoming_events(10)
        if not events:
            return "未找到可标记的事件。"
        
        # 尝试匹配事件标题
        for event in events:
            if event['summary'].lower() in user_input.lower():
                marked_event = mark_event_as_important(event['id'])
                if marked_event:
                    return f"已将事件 '{event['summary']}' 标记为重要。"
        
        return "未找到匹配的事件，请提供准确的事件标题。"
    
    return "我无法理解您的日历操作请求，请尝试更清晰地描述您想要执行的操作。"

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    data = request.json
    user_input = data.get('message', '')
    
    if not user_input:
        return jsonify({'response': '请输入您的问题或指令'})
    
    # 构建提示
    prompt = f"""你是一个AI日历助手，可以帮助用户管理Google日历中的事件。
用户输入: {user_input}
助手回复:"""
    
    # 生成回复
    response = generate_response(prompt)
    
    # 如果涉及日历操作，进行特殊处理
    if any(keyword in user_input.lower() for keyword in ['日历', '事件', '安排', '提醒', '会议']):
        calendar_response = process_calendar_intent(user_input)
        response = calendar_response
    
    return jsonify({'response': response})

@app.route('/authorize')
def authorize():
    """重定向到Google授权页面"""
    flow = create_flow()
    if not flow:
        return "创建授权流程失败，请确保client_secret.json文件存在。", 500
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    session['state'] = state
    
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    """处理OAuth回调"""
    state = session.get('state')
    
    flow = create_flow()
    flow.fetch_token(authorization_response=request.url)
    
    credentials = flow.credentials
    save_credentials(credentials)
    
    return redirect(url_for('index'))

@app.route('/auth_status')
def auth_status():
    """检查授权状态"""
    credentials = get_credentials()
    return jsonify({'authorized': credentials is not None})

@app.route('/health')
def health():
    """健康检查端点"""
    if model is None or tokenizer is None:
        return jsonify({'status': 'error', 'message': '模型未加载'}), 503
    return jsonify({'status': 'ok', 'message': '服务正常运行中'})

if __name__ == '__main__':
    # 加载模型
    if load_model():
        # 启动应用
        port = int(os.environ.get('PORT', 8080))
        app.run(host='0.0.0.0', port=port)
    else:
        logger.error("模型加载失败，应用无法启动")
