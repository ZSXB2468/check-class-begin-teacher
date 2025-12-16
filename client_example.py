#!/usr/bin/env python3
"""
签到客户端示例
演示如何从学生机调用签到API
"""
import requests
import sys


class CheckinClient:
    """签到客户端"""
    
    def __init__(self, server_url="http://192.168.1.100:5000"):
        """
        初始化客户端
        
        Args:
            server_url: 服务器地址，格式为 http://IP:端口
        """
        self.server_url = server_url.rstrip('/')
    
    def is_alive(self):
        """检查服务器是否在线"""
        try:
            response = requests.get(f"{self.server_url}/isalive", timeout=5)
            return response.json()
        except Exception as e:
            print(f"错误: 无法连接到服务器 - {e}")
            return False
    
    def get_my_id(self):
        """获取本机对应的学生ID"""
        try:
            response = requests.get(f"{self.server_url}/myid", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('id')
            elif response.status_code == 404:
                print("错误: 本机IP未在服务器配置中")
                return None
            else:
                print(f"错误: 服务器返回状态码 {response.status_code}")
                return None
        except Exception as e:
            print(f"错误: 无法获取学生ID - {e}")
            return None
    
    def checkin(self, student_id, password):
        """
        签到
        
        Args:
            student_id: 学生ID
            password: 签到密码
            
        Returns:
            True: 签到成功
            False: 签到失败
        """
        try:
            data = {
                "id": student_id,
                "passwd": password
            }
            response = requests.post(
                f"{self.server_url}/checkin",
                json=data,
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"错误: 服务器返回状态码 {response.status_code}")
                return False
                
        except Exception as e:
            print(f"错误: 签到失败 - {e}")
            return False


def main():
    """主函数 - 演示客户端使用"""
    
    # 使用示例
    print("=" * 60)
    print("签到客户端示例")
    print("=" * 60)
    print()
    
    # 1. 创建客户端（修改为实际的服务器地址）
    server_url = "http://127.0.0.1:5000"  # 修改为实际服务器IP
    client = CheckinClient(server_url)
    
    # 2. 检查服务器是否在线
    print("1. 检查服务器状态...")
    if client.is_alive():
        print("   ✓ 服务器在线")
    else:
        print("   ✗ 服务器离线")
        return
    
    print()
    
    # 3. 获取本机学生ID
    print("2. 获取本机学生ID...")
    student_id = client.get_my_id()
    if student_id:
        print(f"   ✓ 学生ID: {student_id}")
    else:
        print("   ✗ 无法获取学生ID")
        print("   提示: 请确保本机IP已在服务器配置中")
        # 也可以手动输入学生ID
        student_id = input("   请手动输入学生ID: ").strip()
        if not student_id:
            return
    
    print()
    
    # 4. 签到
    print("3. 进行签到...")
    password = input("   请输入签到密码: ").strip()
    
    if client.checkin(student_id, password):
        print("   ✓ 签到成功！")
    else:
        print("   ✗ 签到失败")
        print("   提示: 请检查密码是否正确")
    
    print()
    print("=" * 60)


if __name__ == '__main__':
    # 如果提供了命令行参数，使用自动签到模式
    if len(sys.argv) >= 3:
        server_url = sys.argv[1]
        password = sys.argv[2]
        student_id = sys.argv[3] if len(sys.argv) >= 4 else None
        
        client = CheckinClient(server_url)
        
        # 如果没有提供学生ID，自动获取
        if not student_id:
            student_id = client.get_my_id()
            if not student_id:
                print("无法获取学生ID")
                sys.exit(1)
        
        # 执行签到
        if client.checkin(student_id, password):
            print(f"学生 {student_id} 签到成功")
            sys.exit(0)
        else:
            print(f"学生 {student_id} 签到失败")
            sys.exit(1)
    else:
        # 交互模式
        main()
