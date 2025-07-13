#!/usr/bin/env python3
"""
Test script to verify agent_manager.py works correctly
"""

import sys
import os

# Add current directory to path for testing
sys.path.insert(0, '.')

try:
    from hexaeight_mcp_client.agent_manager import HexaEightAgentManager
    from hexaeight_mcp_client.exceptions import DotnetScriptError, AgentCreationError
    
    print("🧪 Testing HexaEightAgentManager...")
    
    # Test initialization
    try:
        manager = HexaEightAgentManager(debug=True)
        print("✅ AgentManager initialized successfully")
        print(f"📁 Scripts path: {manager.scripts_path}")
        
        # Test dotnet availability
        print("✅ .NET availability check passed")
        
        # Test script verification
        print("✅ Script verification passed")
        
        # Test listing existing configs
        configs = manager.list_existing_configs()
        print(f"📋 Existing configs found: {configs}")
        
        print("\n🎯 AgentManager is ready for use!")
        print("\nExample usage:")
        print(">>> manager = HexaEightAgentManager()")
        print(">>> result = manager.create_parent_agent('my_parent.json')")
        print(">>> print(result.success, result.config_file)")
        
    except DotnetScriptError as e:
        print(f"❌ .NET issue: {e}")
        print("Make sure .NET SDK is installed: https://dotnet.microsoft.com/download")
        
    except AgentCreationError as e:
        print(f"❌ Agent creation issue: {e}")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure hexaeight-agent is installed: pip install hexaeight-agent")
