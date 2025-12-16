# 签到教室端管理系统

这是一个基于Python的签到教室端管理系统，包含tkinter图形界面和轻量级API服务器。

## 功能特点

1. **图形化管理界面**
   - 使用tkinter创建友好的管理界面
   - 启动/停止API服务器
   - 查看签到统计
   - 导出签到历史记录

2. **轻量级API服务器**
   - 基于Flask实现
   - 支持局域网内学生机签到
   - 提供三个API接口：
     - `GET /isalive` - 检查服务器状态
     - `GET /myid` - 根据IP获取学生ID
     - `POST /checkin` - 处理签到请求

3. **配置管理**
   - 使用YAML配置文件
   - 支持IP到学生ID的映射
   - 可配置签到密码和课堂ID

4. **签到记录**
   - SQLite数据库存储
   - 支持按日期、数量筛选
   - CSV格式导出

5. **后台运行**
   - 服务器在后台线程运行
   - 关闭UI后服务器继续工作

## 安装

1. 克隆仓库
```bash
git clone https://github.com/ZSXB2468/check-class-begin-teacher.git
cd check-class-begin-teacher
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 创建配置文件
```bash
cp config.yaml.example config.yaml
```

4. 编辑配置文件，设置学生IP映射、签到密码等

## 使用方法

### 启动管理界面

```bash
python main.py
```

### 配置文件说明

编辑 `config.yaml` 文件：

```yaml
# 当前课堂ID
class_id: '2024-class-001'

# 签到密码
password: 'checkin123'

# API服务器配置
api_server:
  host: '0.0.0.0'
  port: 5000

# 学生机IP到学生ID的映射
student_ip_mapping:
  '192.168.1.101': 'student001'
  '192.168.1.102': 'student002'
```

### API接口说明

1. **检查服务器状态**
```bash
GET http://服务器IP:5000/isalive
返回: true
```

2. **获取学生ID**
```bash
GET http://服务器IP:5000/myid
返回: {"id": "student001"}
```

3. **签到**
```bash
POST http://服务器IP:5000/checkin
请求体: {"id": "student001", "passwd": "checkin123"}
返回: true 或 false
```

### 客户端示例

Python客户端示例：

```python
import requests

# 检查服务器
response = requests.get('http://192.168.1.100:5000/isalive')
print(response.json())  # True

# 获取我的ID
response = requests.get('http://192.168.1.100:5000/myid')
print(response.json())  # {"id": "student001"}

# 签到
response = requests.post(
    'http://192.168.1.100:5000/checkin',
    json={"id": "student001", "passwd": "checkin123"}
)
print(response.json())  # True
```

## 文件结构

```
check-class-begin-teacher/
├── main.py                 # 主程序入口（UI界面）
├── api_server.py          # API服务器模块
├── config_manager.py      # 配置管理模块
├── checkin_logger.py      # 签到记录模块
├── requirements.txt       # Python依赖
├── config.yaml.example    # 配置文件示例
├── config.yaml           # 实际配置文件（需创建）
└── checkin_records.db    # 签到记录数据库（自动创建）
```

## 注意事项

1. 首次使用需要创建并编辑 `config.yaml` 配置文件
2. 确保服务器端口（默认5000）未被占用
3. 学生机需要与服务器在同一局域网
4. 导出的CSV文件使用UTF-8 BOM编码，可在Excel中正确显示中文
5. 关闭UI后，API服务器会继续在后台运行（需要重启程序才能完全停止）

## 许可证

MIT License
