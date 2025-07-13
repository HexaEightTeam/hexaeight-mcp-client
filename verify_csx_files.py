#!/usr/bin/env python3
"""
Verify that hexaeight-agent .csx files are accessible
"""
import os
import sys

try:
    import hexaeight_agent
    
    # Get package directory
    package_dir = os.path.dirname(hexaeight_agent.__file__)
    create_dir = os.path.join(package_dir, "create")
    
    # Check for .csx files
    parent_script = os.path.join(create_dir, "create-identity-for-parent-agent.csx")
    child_script = os.path.join(create_dir, "create-identity-for-child-agent.csx")
    
    print("🔍 Checking hexaeight-agent .csx files...")
    print(f"📁 Package directory: {package_dir}")
    print(f"📁 Create directory: {create_dir}")
    
    if os.path.exists(parent_script):
        print(f"✅ Parent script found: {parent_script}")
    else:
        print(f"❌ Parent script NOT found: {parent_script}")
        
    if os.path.exists(child_script):
        print(f"✅ Child script found: {child_script}")
    else:
        print(f"❌ Child script NOT found: {child_script}")
    
    # Test the helper function
    from hexaeight_agent import get_create_scripts_path
    scripts_path = get_create_scripts_path()
    print(f"📂 Scripts path via helper: {scripts_path}")
    
    print("\n🎯 Integration approach:")
    print("- agent_manager.py will use get_create_scripts_path()")
    print("- No need to bundle .csx files in mcp-client package")
    print("- Always uses latest scripts from hexaeight-agent")
    
except ImportError as e:
    print(f"❌ Error importing hexaeight-agent: {e}")
    print("Make sure hexaeight-agent is installed: pip install hexaeight-agent")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
