"""
API服务器模块
提供签到相关的API接口
"""
from flask import Flask, request, jsonify
from config_manager import ConfigManager
from checkin_logger import CheckinLogger
import threading
import secrets


class APIServer:
    """API服务器"""
    
    def __init__(self, config_manager, checkin_logger):
        self.app = Flask(__name__)
        self.config_manager = config_manager
        self.checkin_logger = checkin_logger
        self.server_thread = None
        self.is_running = False
        
        self.setup_routes()
    
    def setup_routes(self):
        """设置API路由"""
        
        @self.app.route('/isalive', methods=['GET'])
        def isalive():
            """检查服务器是否存活"""
            return jsonify(True)
        
        @self.app.route('/myid', methods=['GET'])
        def myid():
            """根据请求IP返回对应的学生ID"""
            client_ip = request.remote_addr
            student_id = self.config_manager.get_student_id_by_ip(client_ip)
            
            if student_id:
                return jsonify({'id': student_id})
            else:
                return jsonify({'error': 'IP not found in mapping'}), 404
        
        @self.app.route('/checkin', methods=['POST'])
        def checkin():
            """处理签到请求"""
            try:
                data = request.get_json()
                
                if not data or 'id' not in data or 'passwd' not in data:
                    return jsonify(False), 400
                
                student_id = data.get('id')
                password = data.get('passwd')
                
                # 使用常量时间比较防止时序攻击
                correct_password = self.config_manager.get_password()
                if not secrets.compare_digest(password, correct_password):
                    return jsonify(False)
                
                # 记录签到
                class_id = self.config_manager.get_class_id()
                client_ip = request.remote_addr
                
                success = self.checkin_logger.log_checkin(
                    student_id=student_id,
                    class_id=class_id,
                    ip_address=client_ip
                )
                
                return jsonify(success)
                
            except Exception as e:
                print(f"签到处理错误: {e}")
                return jsonify(False), 500
    
    def start(self):
        """启动API服务器（后台线程）"""
        if self.is_running:
            return False, "服务器已在运行"
        
        try:
            server_config = self.config_manager.get_api_server_config()
            host = server_config['host']
            port = server_config['port']
            
            self.server_thread = threading.Thread(
                target=self._run_server,
                args=(host, port),
                daemon=True
            )
            self.server_thread.start()
            self.is_running = True
            
            return True, f"服务器已启动: {host}:{port}"
        except Exception as e:
            return False, f"启动失败: {e}"
    
    def _run_server(self, host, port):
        """在后台线程中运行服务器"""
        self.app.run(host=host, port=port, debug=False, use_reloader=False)
    
    def stop(self):
        """停止API服务器
        
        注意：由于Flask的限制，服务器无法完全停止。
        需要重启程序才能完全停止服务器。
        这个方法主要用于更新UI状态。
        """
        if not self.is_running:
            return False, "服务器未运行"
        
        self.is_running = False
        return True, "服务器停止信号已发送（需要重启程序完全停止）"
    
    def get_status(self):
        """获取服务器状态"""
        return self.is_running
