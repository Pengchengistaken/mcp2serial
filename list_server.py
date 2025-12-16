#!/usr/bin/env python3
"""列出 MCP2Serial 服务器信息"""
import asyncio
import sys
from src.mcp2serial.server import Config, handle_list_tools

async def main():
    # 处理配置文件名参数
    config_name = None
    if len(sys.argv) > 1:
        if sys.argv[1] == '--config' and len(sys.argv) > 2:
            config_name = sys.argv[2]
        elif sys.argv[1].startswith('--'):
            pass  # 忽略其他参数
        else:
            config_name = sys.argv[1]
    
    # 处理配置文件名
    if config_name and config_name != "default":
        if not config_name.endswith("_config.yaml"):
            config_name = f"{config_name}_config.yaml"
    else:
        config_name = "config.yaml"
    
    # 加载配置
    config = Config.load(config_name)
    
    print("=" * 60)
    print("MCP2Serial 服务器信息")
    print("=" * 60)
    print(f"配置文件: {config_name}")
    print(f"服务器名称: mcp2serial")
    print(f"版本: 0.1.0")
    print(f"\n串口配置:")
    print(f"  端口: {config.port or '自动检测'}")
    print(f"  波特率: {config.baud_rate}")
    print(f"  超时: {config.timeout} 秒")
    print(f"  读取超时: {config.read_timeout} 秒")
    print(f"  响应起始字符串: {config.response_start_string}")
    
    print(f"\n可用工具: {len(config.commands)} 个")
    print("-" * 60)
    
    if config.commands:
        # 临时替换全局 config 以便 handle_list_tools 使用
        import src.mcp2serial.server as server_module
        original_config = server_module.config
        server_module.config = config
        
        try:
            tools = await handle_list_tools()
            for i, tool in enumerate(tools, 1):
                print(f"\n{i}. {tool.name}")
                print(f"   描述: {tool.description}")
                if tool.inputSchema and 'properties' in tool.inputSchema:
                    props = tool.inputSchema['properties']
                    if props:
                        print(f"   参数:")
                        for param, schema in props.items():
                            param_type = schema.get('type', 'unknown')
                            print(f"     - {param} ({param_type})")
                if hasattr(tool, 'prompts') and tool.prompts:
                    print(f"   提示词示例:")
                    for prompt in tool.prompts[:3]:  # 只显示前3个
                        print(f"     - {prompt}")
        finally:
            server_module.config = original_config
    else:
        print("当前没有配置任何工具")
        print("\n提示: 请在配置文件中添加 commands 配置")
        print("参考示例 (Pico_config.yaml):")
        print("  commands:")
        print("    set_pwm:")
        print("      command: \"PWM {frequency}\"")
        print("      need_parse: false")
        print("      prompts:")
        print("        - \"把PWM调到最大\"")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
