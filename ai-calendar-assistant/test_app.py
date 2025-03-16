import unittest
import os
import json
from unittest.mock import patch, MagicMock
from app import app, load_model, generate_response, process_calendar_intent

class TestAICalendarAssistant(unittest.TestCase):
    """测试AI日历助手应用"""
    
    def setUp(self):
        """测试前设置"""
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # 模拟环境变量
        self.env_patcher = patch.dict('os.environ', {
            'MODEL_PATH': '/tmp/models',
            'CLIENT_SECRET_FILE': '/tmp/credentials/client_secret.json'
        })
        self.env_patcher.start()
    
    def tearDown(self):
        """测试后清理"""
        self.env_patcher.stop()
    
    @patch('app.AutoModelForCausalLM')
    @patch('app.AutoTokenizer')
    @patch('os.path.exists')
    def test_load_model(self, mock_exists, mock_tokenizer, mock_model):
        """测试模型加载功能"""
        # 模拟模型已存在本地
        mock_exists.return_value = True
        mock_model.from_pretrained.return_value = MagicMock()
        mock_tokenizer.from_pretrained.return_value = MagicMock()
        
        result = load_model()
        
        self.assertTrue(result)
        mock_model.from_pretrained.assert_called_once()
        mock_tokenizer.from_pretrained.assert_called_once()
    
    @patch('app.model')
    @patch('app.tokenizer')
    def test_generate_response(self, mock_tokenizer, mock_model):
        """测试响应生成功能"""
        # 模拟模型输入和输出
        mock_tokenizer.return_value = {'input_ids': MagicMock()}
        mock_tokenizer.decode.return_value = "用户输入: 测试\n助手回复: 这是一个测试回复"
        mock_model.generate.return_value = [MagicMock()]
        
        response = generate_response("用户输入: 测试\n助手回复:")
        
        self.assertEqual(response, "这是一个测试回复")
        mock_model.generate.assert_called_once()
    
    @patch('app.get_credentials')
    @patch('app.generate_response')
    def test_process_calendar_intent_unauthorized(self, mock_generate, mock_get_credentials):
        """测试未授权状态下的日历意图处理"""
        mock_get_credentials.return_value = None
        
        response = process_calendar_intent("帮我创建一个会议")
        
        self.assertIn("您需要先授权访问Google日历", response)
    
    @patch('app.get_credentials')
    @patch('app.generate_response')
    @patch('app.list_upcoming_events')
    def test_process_calendar_intent_query_events(self, mock_list_events, mock_generate, mock_get_credentials):
        """测试查询事件意图处理"""
        # 模拟已授权
        mock_get_credentials.return_value = MagicMock()
        # 模拟意图分析结果
        mock_generate.return_value = "查询事件\n时间范围: 今天"
        # 模拟事件列表
        mock_list_events.return_value = [
            {'summary': '测试会议', 'start': {'dateTime': '2025-03-14T14:00:00+08:00'}}
        ]
        
        response = process_calendar_intent("查看我今天的日程")
        
        self.assertIn("测试会议", response)
        mock_list_events.assert_called_once()
    
    def test_index_route(self):
        """测试主页路由"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_chat_route(self):
        """测试聊天接口"""
        with patch('app.generate_response') as mock_generate:
            mock_generate.return_value = "这是一个测试回复"
            
            response = self.client.post('/chat', 
                                      json={'message': '你好'},
                                      content_type='application/json')
            
            data = json.loads(response.data)
            self.assertEqual(response.status_code, 200)
            self.assertIn('response', data)
    
    def test_health_route(self):
        """测试健康检查接口"""
        with patch('app.model', MagicMock()), patch('app.tokenizer', MagicMock()):
            response = self.client.get('/health')
            data = json.loads(response.data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['status'], 'ok')

if __name__ == '__main__':
    unittest.main()
