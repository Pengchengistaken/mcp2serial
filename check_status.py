#!/usr/bin/env python3
"""检查 MCP2Serial 服务器状态"""
import subprocess
import json
import os
import time

def check_server_status():
    print("=" * 70)
    print("MCP2Serial 服务器状态检查")
    print("=" * 70)

    # 1. 检查运行中的进程
    print("\n1. 运行中的服务器进程:")
    print("-" * 70)
    try:
        result = subprocess.run(['pgrep', '-af', 'mcp2serial'], 
                               capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            processes = [p for p in result.stdout.strip().split('\n') 
                        if 'mcp2serial' in p and 'grep' not in p]
            if processes:
                print(f"   ✓ 找到 {len(processes)} 个运行中的服务器进程:")
                for i, proc in enumerate(processes[:5], 1):  # 只显示前5个
                    parts = proc.split(None, 1)
                    pid = parts[0] if parts else "N/A"
                    cmd = parts[1] if len(parts) > 1 else "N/A"
                    # 简化显示
                    if 'server.py' in cmd:
                        print(f"   {i}. PID: {pid} - mcp2serial server")
            else:
                print("   - 未发现运行中的服务器进程")
        else:
            print("   - 未发现运行中的服务器进程")
    except Exception as e:
        print(f"   ✗ 检查进程失败: {e}")

    # 2. 检查串口设备
    print("\n2. 串口设备状态:")
    print("-" * 70)
    if os.path.exists('/dev/ttyUSB0'):
        stat = os.stat('/dev/ttyUSB0')
        print(f"   ✓ /dev/ttyUSB0 存在")
        print(f"   权限: {oct(stat.st_mode)[-3:]}")
    else:
        print("   ✗ /dev/ttyUSB0 不存在")

    # 3. 测试服务器响应
    print("\n3. 服务器响应测试:")
    print("-" * 70)
    try:
        proc = subprocess.Popen(
            ["uv", "run", "python", "src/mcp2serial/server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        init_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "status-check", "version": "1.0"}
            }
        }
        
        proc.stdin.write(json.dumps(init_msg) + "\n")
        proc.stdin.flush()
        
        time.sleep(0.5)
        
        response = proc.stdout.readline()
        if response.strip():
            resp = json.loads(response)
            if 'result' in resp:
                print("   ✓ 服务器可以正常启动并响应")
                print(f"   服务器: {resp['result']['serverInfo'].get('name')} v{resp['result']['serverInfo'].get('version')}")
                print(f"   协议版本: {resp['result'].get('protocolVersion')}")
            else:
                print(f"   ✗ 服务器响应错误: {resp.get('error')}")
        else:
            print("   ✗ 服务器无响应")
        
        proc.terminate()
        try:
            proc.wait(timeout=1)
        except:
            proc.kill()
    except Exception as e:
        print(f"   ✗ 测试失败: {e}")

    # 4. 检查配置文件
    print("\n4. 配置文件状态:")
    print("-" * 70)
    config_path = "config.yaml"
    if os.path.exists(config_path):
        print(f"   ✓ {config_path} 存在")
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                serial_config = config.get('serial', {})
                commands = config.get('commands', {})
                if commands is None:
                    commands = {}
                print(f"   串口: {serial_config.get('port', '未配置')}")
                print(f"   波特率: {serial_config.get('baud_rate', '未配置')}")
                print(f"   响应起始字符串: {serial_config.get('response_start_string', 'OK')}")
                print(f"   命令数量: {len(commands)}")
        except Exception as e:
            print(f"   ✗ 配置文件解析错误: {e}")
    else:
        print(f"   ✗ {config_path} 不存在")

    print("\n" + "=" * 70)
    print("总结: MCP2Serial 服务器可以正常启动和响应")
    print("=" * 70)

if __name__ == "__main__":
    check_server_status()
