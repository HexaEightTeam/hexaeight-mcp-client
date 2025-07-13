#!/usr/bin/env python3
"""
Test that the package can be imported correctly
"""

import sys
sys.path.insert(0, '.')

try:
    print("🧪 Testing package imports...")
    
    # Test individual components
    from hexaeight_mcp_client.client import HexaEightMCPClient, ToolResult
    print("✅ Client imported successfully")
    
    from hexaeight_mcp_client.agent_manager import HexaEightAgentManager
    print("✅ AgentManager imported successfully")
    
    from hexaeight_mcp_client.adapters import AutogenAdapter, FrameworkDetector
    print("✅ Adapters imported successfully")
    
    from hexaeight_mcp_client.exceptions import HexaEightMCPError
    print("✅ Exceptions imported successfully")
    
    # Test full package import
    from hexaeight_mcp_client import HexaEightMCPClient, HexaEightAgentManager
    print("✅ Full package import successful")
    
    # Test basic functionality
    client = HexaEightMCPClient()
    tools = client.get_available_tools()
    print(f"✅ Client created, tools available: {list(tools.keys())}")
    
    manager = HexaEightAgentManager(debug=False)
    print("✅ AgentManager created successfully")
    
    print("\n🎉 All imports working correctly!")
    print("📦 Package is ready for Step 3 expansion")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
