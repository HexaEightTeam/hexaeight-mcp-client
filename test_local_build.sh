#!/bin/bash

echo "🔨 Local Package Testing Workflow"
echo "=" * 40

# Step 1: Install build tools
echo "📦 Installing build tools..."
pip install build twine

# Step 2: Build package
echo "🔨 Building package..."
python -m build

echo ""
echo "📋 Build results:"
ls -la dist/

# Step 3: Check package
echo "🔍 Checking package..."
python -m twine check dist/*

# Step 4: Create test environment
echo "🧪 Creating test environment..."
python -m venv venv_test
source venv_test/bin/activate

# Step 5: Install hexaeight-agent first
echo "📦 Installing hexaeight-agent..."
pip install hexaeight-agent

# Step 6: Install local package
echo "📦 Installing local package..."
pip install dist/hexaeight_mcp_client-0.1.0-py3-none-any.whl

# Step 7: Test import
echo "🧪 Testing import..."
python -c "
from hexaeight_mcp_client import HexaEightMCPClient, HexaEightAgentManager
print('✅ Import successful')

client = HexaEightMCPClient()
tools = client.get_available_tools()
print(f'✅ Tools available: {list(tools.keys())}')

manager = HexaEightAgentManager(debug=False)
print('✅ Agent manager created')
print('🎉 Local package test successful!')
"

# Step 8: Cleanup
echo "🧹 Cleaning up test environment..."
deactivate
rm -rf venv_test/

echo ""
echo "✅ Local testing completed!"
echo "🚀 Ready for PyPI publishing"
