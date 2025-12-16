"""
签到记录模块
负责记录和管理签到数据
"""
import sqlite3
import csv
from datetime import datetime, timedelta
import os
import threading


class CheckinLogger:
    """签到记录器"""
    
    def __init__(self, db_path='checkin_records.db'):
        self.db_path = db_path
        self.lock = threading.Lock()  # 添加线程锁保证数据库操作的线程安全
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS checkin_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    class_id TEXT NOT NULL,
                    checkin_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
    
    def log_checkin(self, student_id, class_id, ip_address):
        """记录签到"""
        try:
            with self.lock:  # 使用锁保证线程安全
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO checkin_records (student_id, class_id, ip_address)
                    VALUES (?, ?, ?)
                ''', (student_id, class_id, ip_address))
                
                conn.commit()
                conn.close()
            return True
        except Exception as e:
            print(f"记录签到失败: {e}")
            return False
    
    def get_records(self, days=None, count=None, class_id=None):
        """获取签到记录
        
        Args:
            days: 获取最近N天的记录
            count: 限制返回的记录数量
            class_id: 筛选指定课堂ID的记录
        """
        with self.lock:  # 使用锁保证线程安全
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = 'SELECT student_id, class_id, checkin_time, ip_address FROM checkin_records WHERE 1=1'
            params = []
            
            if days is not None:
                start_date = datetime.now() - timedelta(days=days)
                query += ' AND checkin_time >= ?'
                params.append(start_date.strftime('%Y-%m-%d %H:%M:%S'))
            
            if class_id is not None:
                query += ' AND class_id = ?'
                params.append(class_id)
            
            query += ' ORDER BY checkin_time DESC'
            
            if count is not None:
                query += ' LIMIT ?'
                params.append(count)
            
            cursor.execute(query, params)
            records = cursor.fetchall()
            conn.close()
            
            return records
    
    def export_to_csv(self, filename, days=None, count=None, class_id=None):
        """导出签到记录到CSV文件
        
        Args:
            filename: 输出文件名
            days: 获取最近N天的记录
            count: 限制导出的记录数量
            class_id: 筛选指定课堂ID的记录
        """
        try:
            records = self.get_records(days=days, count=count, class_id=class_id)
            
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['学生ID', '课堂ID', '签到时间', 'IP地址'])
                writer.writerows(records)
            
            return True, f"成功导出 {len(records)} 条记录"
        except Exception as e:
            return False, f"导出失败: {e}"
    
    def get_statistics(self, class_id=None):
        """获取签到统计信息"""
        with self.lock:  # 使用锁保证线程安全
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = 'SELECT COUNT(*) as total, COUNT(DISTINCT student_id) as unique_students FROM checkin_records'
            params = []
            
            if class_id is not None:
                query += ' WHERE class_id = ?'
                params.append(class_id)
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            conn.close()
            
            return {
                'total_checkins': result[0] if result else 0,
                'unique_students': result[1] if result else 0
            }
