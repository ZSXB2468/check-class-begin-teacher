#!/usr/bin/env python3
"""
模块验证脚本
验证所有模块能正确导入和基本功能正常
"""
import sys


def test_config_manager():
    """测试配置管理模块"""
    print("测试 config_manager...")
    from config_manager import ConfigManager
    
    cm = ConfigManager('test_config.yaml')
    
    # 测试默认配置
    assert cm.get_class_id() == '2024-class-001'
    assert cm.get_password() == 'checkin123'
    assert cm.get_student_id_by_ip('192.168.1.101') == 'student001'
    
    # 测试获取API配置
    api_config = cm.get_api_server_config()
    assert api_config['host'] == '0.0.0.0'
    assert api_config['port'] == 5000
    
    print("  ✓ ConfigManager 测试通过")
    return True


def test_checkin_logger():
    """测试签到记录模块"""
    print("测试 checkin_logger...")
    from checkin_logger import CheckinLogger
    import os
    
    # 使用临时数据库
    db_path = 'test_checkin.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    logger = CheckinLogger(db_path)
    
    # 测试记录签到
    assert logger.log_checkin('student001', 'class001', '192.168.1.101')
    assert logger.log_checkin('student002', 'class001', '192.168.1.102')
    
    # 测试获取记录
    records = logger.get_records(count=5)
    assert len(records) == 2
    
    # 测试统计
    stats = logger.get_statistics()
    assert stats['total_checkins'] == 2
    assert stats['unique_students'] == 2
    
    # 测试导出
    success, msg = logger.export_to_csv('test_export.csv', count=10)
    assert success
    assert os.path.exists('test_export.csv')
    
    # 清理
    os.remove(db_path)
    os.remove('test_export.csv')
    
    print("  ✓ CheckinLogger 测试通过")
    return True


def test_api_server():
    """测试API服务器模块"""
    print("测试 api_server...")
    from api_server import APIServer
    from config_manager import ConfigManager
    from checkin_logger import CheckinLogger
    
    cm = ConfigManager()
    logger = CheckinLogger('test_api.db')
    api = APIServer(cm, logger)
    
    # 验证Flask应用存在
    assert api.app is not None
    assert hasattr(api, 'start')
    assert hasattr(api, 'stop')
    assert hasattr(api, 'get_status')
    
    # 清理
    import os
    if os.path.exists('test_api.db'):
        os.remove('test_api.db')
    
    print("  ✓ APIServer 测试通过")
    return True


def main():
    """主测试函数"""
    print("\n" + "=" * 50)
    print("签到系统模块验证")
    print("=" * 50 + "\n")
    
    tests = [
        test_config_manager,
        test_checkin_logger,
        test_api_server
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ✗ {test.__name__} 失败: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 50 + "\n")
    
    # 清理测试文件
    import os
    for f in ['test_config.yaml', 'test_checkin.db', 'test_api.db', 'test_export.csv']:
        if os.path.exists(f):
            os.remove(f)
    
    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
