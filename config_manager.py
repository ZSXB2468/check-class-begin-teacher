"""
配置管理模块
负责加载和管理YAML配置文件
"""
import yaml
import os


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path='config.yaml'):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            return self.get_default_config()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config if config else self.get_default_config()
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return self.get_default_config()
    
    def save_config(self, config=None):
        """保存配置到文件"""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def get_default_config(self):
        """获取默认配置"""
        return {
            'class_id': '2024-class-001',
            'password': 'checkin123',
            'api_server': {
                'host': '0.0.0.0',
                'port': 5000
            },
            'student_ip_mapping': {
                '192.168.1.101': 'student001',
                '192.168.1.102': 'student002',
                '192.168.1.103': 'student003'
            }
        }
    
    def get_student_id_by_ip(self, ip):
        """根据IP地址获取学生ID"""
        return self.config.get('student_ip_mapping', {}).get(ip)
    
    def get_password(self):
        """获取签到密码"""
        return self.config.get('password', '')
    
    def get_class_id(self):
        """获取当前课堂ID"""
        return self.config.get('class_id', '')
    
    def get_api_server_config(self):
        """获取API服务器配置"""
        api_config = self.config.get('api_server', {})
        return {
            'host': api_config.get('host', '0.0.0.0'),
            'port': api_config.get('port', 5000)
        }
