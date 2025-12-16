"""
签到教室端管理界面
使用tkinter创建UI，管理后台API服务器
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from config_manager import ConfigManager
from checkin_logger import CheckinLogger
from api_server import APIServer
import os


class CheckinManagerUI:
    """签到管理界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("签到教室端管理系统")
        self.root.geometry("800x600")
        
        # 初始化组件
        self.config_manager = ConfigManager()
        self.checkin_logger = CheckinLogger()
        self.api_server = APIServer(self.config_manager, self.checkin_logger)
        
        self.setup_ui()
        self.update_status()
    
    def setup_ui(self):
        """设置用户界面"""
        # 标题
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill=tk.X)
        
        title_label = ttk.Label(
            title_frame,
            text="签到教室端管理系统",
            font=("Arial", 16, "bold")
        )
        title_label.pack()
        
        # 服务器控制区域
        control_frame = ttk.LabelFrame(self.root, text="服务器控制", padding="10")
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 状态显示
        status_frame = ttk.Frame(control_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(status_frame, text="服务器状态:").pack(side=tk.LEFT)
        self.status_label = ttk.Label(
            status_frame,
            text="未运行",
            foreground="red",
            font=("Arial", 10, "bold")
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # 控制按钮
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        self.start_button = ttk.Button(
            button_frame,
            text="启动服务器",
            command=self.start_server
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(
            button_frame,
            text="停止服务器",
            command=self.stop_server,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="刷新状态",
            command=self.update_status
        ).pack(side=tk.LEFT, padx=5)
        
        # 配置信息显示
        config_frame = ttk.LabelFrame(self.root, text="当前配置", padding="10")
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.config_text = tk.Text(config_frame, height=6, width=70)
        self.config_text.pack(fill=tk.BOTH, expand=True)
        self.update_config_display()
        
        # 签到记录统计
        stats_frame = ttk.LabelFrame(self.root, text="签到统计", padding="10")
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.stats_label = ttk.Label(stats_frame, text="加载中...")
        self.stats_label.pack()
        
        ttk.Button(
            stats_frame,
            text="刷新统计",
            command=self.update_statistics
        ).pack(pady=5)
        
        # 导出记录区域
        export_frame = ttk.LabelFrame(self.root, text="导出签到记录", padding="10")
        export_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 过滤选项
        filter_frame = ttk.Frame(export_frame)
        filter_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(filter_frame, text="最近天数:").pack(side=tk.LEFT, padx=5)
        self.days_var = tk.StringVar(value="7")
        ttk.Entry(filter_frame, textvariable=self.days_var, width=10).pack(side=tk.LEFT)
        
        ttk.Label(filter_frame, text="限制条数:").pack(side=tk.LEFT, padx=5)
        self.count_var = tk.StringVar(value="1000")
        ttk.Entry(filter_frame, textvariable=self.count_var, width=10).pack(side=tk.LEFT)
        
        ttk.Button(
            filter_frame,
            text="导出为CSV",
            command=self.export_records
        ).pack(side=tk.LEFT, padx=10)
        
        # 底部信息
        info_frame = ttk.Frame(self.root)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(
            info_frame,
            text="提示: 启动服务器后，可以关闭此窗口，服务器将继续在后台运行",
            foreground="blue"
        ).pack()
        
        # 初始化统计
        self.update_statistics()
    
    def update_config_display(self):
        """更新配置显示"""
        self.config_text.delete(1.0, tk.END)
        
        config = self.config_manager.config
        api_config = config.get('api_server', {})
        
        config_info = f"""课堂ID: {config.get('class_id', 'N/A')}
签到密码: {config.get('password', 'N/A')}
服务器地址: {api_config.get('host', '0.0.0.0')}:{api_config.get('port', 5000)}
学生机IP映射数量: {len(config.get('student_ip_mapping', {}))}
配置文件: config.yaml"""
        
        self.config_text.insert(1.0, config_info)
        self.config_text.config(state=tk.DISABLED)
    
    def start_server(self):
        """启动API服务器"""
        success, message = self.api_server.start()
        
        if success:
            messagebox.showinfo("成功", message)
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.update_status()
        else:
            messagebox.showerror("错误", message)
    
    def stop_server(self):
        """停止API服务器"""
        success, message = self.api_server.stop()
        
        if success:
            messagebox.showinfo("提示", message)
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.update_status()
        else:
            messagebox.showerror("错误", message)
    
    def update_status(self):
        """更新服务器状态显示"""
        is_running = self.api_server.get_status()
        
        if is_running:
            self.status_label.config(text="运行中", foreground="green")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
        else:
            self.status_label.config(text="未运行", foreground="red")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
    
    def update_statistics(self):
        """更新签到统计信息"""
        class_id = self.config_manager.get_class_id()
        stats = self.checkin_logger.get_statistics(class_id=class_id)
        
        stats_text = f"总签到次数: {stats['total_checkins']}  |  不同学生数: {stats['unique_students']}"
        self.stats_label.config(text=stats_text)
    
    def export_records(self):
        """导出签到记录"""
        try:
            # 获取过滤参数
            days = None
            if self.days_var.get().strip():
                days = int(self.days_var.get())
            
            count = None
            if self.count_var.get().strip():
                count = int(self.count_var.get())
            
            # 选择保存位置
            default_filename = f"checkin_records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                initialfile=default_filename,
                filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
            )
            
            if not filename:
                return
            
            # 导出
            class_id = self.config_manager.get_class_id()
            success, message = self.checkin_logger.export_to_csv(
                filename=filename,
                days=days,
                count=count,
                class_id=class_id
            )
            
            if success:
                messagebox.showinfo("成功", message)
            else:
                messagebox.showerror("错误", message)
                
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {e}")


def main():
    """主函数"""
    root = tk.Tk()
    app = CheckinManagerUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()

