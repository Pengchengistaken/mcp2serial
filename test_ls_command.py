#!/usr/bin/env python3
"""测试 ls -l 命令的返回"""
import logging
from src.mcp2serial.server import SerialConnection, Config, Command

# 设置日志级别为 DEBUG 以查看详细信息
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_ls_command():
    """测试 ls -l 命令"""
    print("=" * 70)
    print("测试 ls -l 命令")
    print("=" * 70)
    
    # 加载配置
    print("\n1. 加载配置...")
    config = Config.load("config.yaml")
    print(f"   串口: {config.port or '自动检测'}")
    print(f"   波特率: {config.baud_rate}")
    print(f"   读取超时: {config.read_timeout} 秒")
    print(f"   响应起始字符串: {repr(config.response_start_string)}")
    
    # 检查命令配置
    if 'send_ls_l' not in config.commands:
        print("\n❌ 错误: 配置文件中没有找到 'send_ls_l' 命令")
        return
    
    command = config.commands['send_ls_l']
    print(f"\n2. 命令配置:")
    print(f"   命令模板: {repr(command.command)}")
    print(f"   需要解析: {command.need_parse}")
    
    # 创建串口连接
    print("\n3. 连接串口...")
    serial_connection = SerialConnection()
    try:
        if serial_connection.connect():
            print(f"   ✓ 连接成功")
            if serial_connection.serial_port:
                print(f"   端口: {serial_connection.serial_port.port}")
        else:
            print("   ❌ 连接失败")
            return
    except Exception as e:
        print(f"   ❌ 连接错误: {e}")
        return
    
    # 发送命令
    print("\n4. 发送命令...")
    print(f"   发送: {command.command}")
    try:
        response = serial_connection.send_command(command, {})
        
        print(f"\n5. 响应结果:")
        print("-" * 70)
        if not response:
            print("   (空响应)")
        else:
            for i, item in enumerate(response, 1):
                print(f"\n   响应 {i}:")
                print(f"   类型: {type(item).__name__}")
                if hasattr(item, 'text'):
                    text = item.text
                    if text:
                        print(f"   内容:")
                        # 分行显示，每行前面加缩进
                        for line in text.split('\n'):
                            print(f"      {line}")
                    else:
                        print(f"   内容: (空)")
                else:
                    print(f"   内容: {item}")
        
        print("\n" + "=" * 70)
        print("测试完成")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ 执行错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        serial_connection.close()
        print("\n已关闭串口连接")

if __name__ == "__main__":
    test_ls_command()
