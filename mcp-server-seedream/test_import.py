# 测试导入是否正常工作
try:
    from mcp_server_seedream.server import mcp
    print("✅ 成功导入服务器模块")
    print("✅ 服务器准备就绪，可以运行")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()