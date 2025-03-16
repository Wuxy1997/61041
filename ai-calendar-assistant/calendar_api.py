from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from flask import redirect, request, url_for, session
import os
import json
import datetime
import logging

# 配置日志
logger = logging.getLogger(__name__)

# Google Calendar API 配置
SCOPES = ['https://www.googleapis.com/auth/calendar']
CLIENT_SECRET_FILE = os.environ.get('CLIENT_SECRET_FILE', '/app/credentials/client_secret.json')
TOKEN_FILE = os.environ.get('TOKEN_FILE', '/app/credentials/token.json')

def get_credentials():
    """获取Google API凭据"""
    if 'credentials' in session:
        return Credentials.from_authorized_user_info(json.loads(session['credentials']), SCOPES)
    
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as token:
            return Credentials.from_authorized_user_info(json.load(token), SCOPES)
    
    return None

def save_credentials(credentials):
    """保存凭据到会话和文件"""
    session['credentials'] = credentials.to_json()
    
    # 确保目录存在
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    
    # 保存到文件
    with open(TOKEN_FILE, 'w') as token:
        token.write(credentials.to_json())

def create_flow():
    """创建OAuth2.0授权流程"""
    try:
        return Flow.from_client_secrets_file(
            CLIENT_SECRET_FILE,
            scopes=SCOPES,
            redirect_uri=url_for('oauth2callback', _external=True)
        )
    except Exception as e:
        logger.error(f"创建授权流程失败: {str(e)}")
        return None

def get_calendar_service():
    """获取Google Calendar服务"""
    credentials = get_credentials()
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            save_credentials(credentials)
        else:
            return None
    
    return build('calendar', 'v3', credentials=credentials)

def list_upcoming_events(max_results=10):
    """列出即将到来的事件"""
    service = get_calendar_service()
    if not service:
        return None
    
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' 表示 UTC 时间
    
    try:
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        return events_result.get('items', [])
    except Exception as e:
        logger.error(f"获取事件列表失败: {str(e)}")
        return None

def create_event(summary, start_time, end_time, description=None, location=None, is_important=False):
    """创建日历事件"""
    service = get_calendar_service()
    if not service:
        return False
    
    # 处理重要事件标记
    colorId = '11' if is_important else None  # 11 是红色，表示重要事件
    
    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': 'Asia/Shanghai',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Asia/Shanghai',
        },
        'colorId': colorId,
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 30},
            ],
        },
    }
    
    try:
        event = service.events().insert(calendarId='primary', body=event).execute()
        return event
    except Exception as e:
        logger.error(f"创建事件失败: {str(e)}")
        return None

def mark_event_as_important(event_id):
    """将事件标记为重要"""
    service = get_calendar_service()
    if not service:
        return False
    
    try:
        # 获取现有事件
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        
        # 更新颜色为红色（表示重要）
        event['colorId'] = '11'
        
        # 更新事件
        updated_event = service.events().update(
            calendarId='primary',
            eventId=event_id,
            body=event
        ).execute()
        
        return updated_event
    except Exception as e:
        logger.error(f"标记重要事件失败: {str(e)}")
        return None

def parse_event_time(time_str):
    """解析事件时间字符串为ISO格式"""
    try:
        # 这里可以根据实际需求扩展更多的时间格式解析
        dt = datetime.datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        return dt.isoformat()
    except Exception as e:
        logger.error(f"解析时间失败: {str(e)}")
        return None
