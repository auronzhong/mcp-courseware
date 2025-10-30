#!/usr/bin/env python3
# 直接启动MCP服务器的脚本

import sys
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()
print("🔧 环境变量已从 .env 文件加载")

from mcp_server_seedream.server import mcp

def main():
    print("🚀 正在启动 Seedream MCP Server...")
    print("📋 服务器配置:")
    print(f"  - 名称: {mcp.name}")
    print(f"  - 传输协议: STDIO (本地模式)")
    print(f"  - 指令: {mcp.instructions[:100]}...")
    print("\n🔧 工具已注册")
    print("✅ 服务器已准备就绪")
    print("ℹ️  按 Ctrl+C 停止服务器")
    print("\n" + "="*60)
    
    try:
        # 运行服务器
        mcp.run()
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"\n❌ 服务器启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()