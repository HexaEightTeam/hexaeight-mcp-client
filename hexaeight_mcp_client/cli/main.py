"""
Main CLI dispatcher for HexaEight MCP Client
Updated to use unified hexaeight-start command structure
"""

import sys
from typing import List, Optional

from .license_activation import LicenseActivationCLI
from .prerequisites import PrerequisitesCLI  
from .directory_setup import DirectorySetupCLI
from .agent_generation import AgentGenerationCLI
from .sample_deployment import SampleDeploymentCLI
from .portable_setup import PortableSetupCLI

def main():
    """Main CLI entry point - Legacy support"""
    print("⚠️  This legacy entry point is no longer available.")
    print("💡 Please use the unified command structure:")
    print("   hexaeight-start <command>")
    print("")
    print("🔧 Available commands:")
    print("   hexaeight-start check-prerequisites")
    print("   hexaeight-start license-activation")
    print("   hexaeight-start create-directory-linked-to-hexaeight-license")
    print("   hexaeight-start generate-parent-or-child-agent-licenses")
    print("   hexaeight-start deploy-multi-ai-agent-samples")
    print("   hexaeight-start setup-portable-child-agent-environment")
    
    sys.exit(1)

def hexaeight_start():
    """Unified entry point for all HexaEight MCP Client commands"""
    
    if len(sys.argv) < 2 or sys.argv[1] in ['--help', '-h', 'help']:
        print_help()
        sys.exit(1)
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    try:
        if command == "check-prerequisites":
            cli = PrerequisitesCLI()
            cli.run(args)
        elif command == "license-activation":
            cli = LicenseActivationCLI()
            cli.run(args)
        elif command == "create-directory-linked-to-hexaeight-license":
            if not args:
                print("❌ Error: Directory name required")
                print("Usage: hexaeight-start create-directory-linked-to-hexaeight-license <directory_name>")
                sys.exit(1)
            cli = DirectorySetupCLI()
            cli.run(args[0])
        elif command == "generate-parent-or-child-agent-licenses":
            cli = AgentGenerationCLI()
            cli.run(args)
        elif command == "deploy-multi-ai-agent-samples":
            cli = SampleDeploymentCLI()
            cli.run(args)
        elif command == "setup-portable-child-agent-environment":
            cli = PortableSetupCLI()
            cli.run(args)
        else:
            print(f"❌ Unknown command: {command}")
            print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def print_help():
    """Print comprehensive help for the unified command structure"""
    print("""
🚀 HexaEight MCP Client - Unified Command Interface

USAGE:
    hexaeight-start <command> [arguments]

COMMANDS:
    check-prerequisites                              Check system requirements (.NET, dotnet-script)
    license-activation                               Setup machine token utility for license activation
    create-directory-linked-to-hexaeight-license    Create project directory with license hardlinks
    generate-parent-or-child-agent-licenses         Generate agent configuration files
    deploy-multi-ai-agent-samples                   Deploy sample multi-agent weather system
    setup-portable-child-agent-environment          Setup portable child agent on secondary machine

WORKFLOW:
    🔧 Complete Setup Workflow:
    
    1. Check Prerequisites:
       hexaeight-start check-prerequisites
    
    2. Activate License (one time):
       hexaeight-start license-activation
    
    3. Create Organized Workspace:
       hexaeight-start create-directory-linked-to-hexaeight-license my-ai-project
       cd my-ai-project
    
    4. Generate Agent Configurations:
       hexaeight-start generate-parent-or-child-agent-licenses
    
    5. Deploy Sample System:
       hexaeight-start deploy-multi-ai-agent-samples
    
    6. Setup Child Agents on Other Machines:
       hexaeight-start setup-portable-child-agent-environment child_config.json

EXAMPLES:
    # Check if system is ready
    hexaeight-start check-prerequisites
    
    # Activate license (creates hexaeight.mac)
    hexaeight-start license-activation
    
    # Create project workspace with license links
    hexaeight-start create-directory-linked-to-hexaeight-license weather-agents
    
    # Generate parent and child agent configs
    hexaeight-start generate-parent-or-child-agent-licenses
    
    # Deploy sample weather system (AutoGen, CrewAI, LangChain)
    hexaeight-start deploy-multi-ai-agent-samples
    
    # Setup child agent environment on cloud/edge device
    hexaeight-start setup-portable-child-agent-environment child_weather_01.json

KEY CONCEPTS:
    🏢 Parent Agent:   Runs on licensed machine, creates child agents
    👥 Child Agents:   Run anywhere, work forever, unlimited creation
    🔗 License Links:  Hardlinks allow organized project structure
    📱 Portable Setup: Deploy child agents on secondary machines
    🌤️  Sample System:  Multi-framework weather agents for testing
    🎲 Generic Names:  No domain required - instant random agent identities

MORE INFO:
    📖 Documentation: https://github.com/HexaEightTeam/hexaeight-mcp-client
    🛒 License Store:  https://store.hexaeight.com
    📱 Mobile App:     Search "HexaEight Authenticator" in app stores

NOTE: Only 'hexaeight-start' command is available - clean, unified interface!
""")

# Enhanced help function for the main package
def get_cli_commands():
    """Get available CLI commands for the unified structure"""
    return {
        "hexaeight-start": "Unified command interface for all HexaEight MCP Client operations",
        "check-prerequisites": "Check system requirements and dependencies",
        "license-activation": "Setup and activate HexaEight license",
        "create-directory-linked-to-hexaeight-license": "Create organized project workspace",
        "generate-parent-or-child-agent-licenses": "Generate agent configurations",
        "deploy-multi-ai-agent-samples": "Deploy sample multi-agent systems",
        "setup-portable-child-agent-environment": "Setup child agents on secondary machines"
    }

def print_unified_cli_help():
    """Print unified CLI help information"""
    print(f"🔧 HexaEight MCP Client - Unified Command Interface")
    print("=" * 65)
    
    commands = get_cli_commands()
    
    print(f"\n📋 MAIN COMMAND:")
    print(f"  hexaeight-start <subcommand>    All operations through unified interface")
    
    print(f"\n🔧 SUBCOMMANDS:")
    subcommands = [
        ("check-prerequisites", "Check system requirements"),
        ("license-activation", "Setup and activate license"),
        ("create-directory-linked-to-hexaeight-license", "Create project workspace"),
        ("generate-parent-or-child-agent-licenses", "Generate agent configs"),
        ("deploy-multi-ai-agent-samples", "Deploy sample systems"),
        ("setup-portable-child-agent-environment", "Setup portable child agents")
    ]
    
    for cmd, desc in subcommands:
        print(f"  {cmd:<45} {desc}")
    
    print(f"\n🚀 WORKFLOW EXAMPLES:")
    print(f"  hexaeight-start check-prerequisites")
    print(f"  hexaeight-start license-activation")
    print(f"  hexaeight-start create-directory-linked-to-hexaeight-license my-project")
    print(f"  hexaeight-start generate-parent-or-child-agent-licenses")
    print(f"  hexaeight-start deploy-multi-ai-agent-samples")
    print(f"  hexaeight-start setup-portable-child-agent-environment child_config.json")
    
    print(f"\n🔗 Resources:")
    print(f"  📖 Documentation: https://github.com/HexaEightTeam/hexaeight-mcp-client")
    print(f"  🛒 License Store: https://store.hexaeight.com")
    print(f"  📱 Mobile App: Search 'HexaEight Authenticator'")
    
    print(f"\n💡 All commands now use the unified 'hexaeight-start' interface!")
