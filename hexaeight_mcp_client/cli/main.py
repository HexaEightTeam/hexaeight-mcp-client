"""
Main CLI dispatcher for HexaEight MCP Client
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
    """Main CLI entry point"""
    
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    try:
        if command == "license-activation":
            cli = LicenseActivationCLI()
            cli.run(args)
        elif command == "check-prerequisites":
            cli = PrerequisitesCLI()
            cli.run(args)
        elif command == "directory-linked-to-hexaeight-license":
            if not args:
                print("❌ Error: Directory name required")
                print("Usage: hexaeight-create directory-linked-to-hexaeight-license <directory_name>")
                sys.exit(1)
            cli = DirectorySetupCLI()
            cli.run(args[0])
        elif command == "generate-parent-or-child-agent-licenses":
            cli = AgentGenerationCLI()
            cli.run(args)
        elif command == "multi-ai-agent-samples":
            cli = SampleDeploymentCLI()
            cli.run(args)
        elif command == "portable-child-agent-environment":
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
    """Print main help"""
    print("""
🚀 HexaEight MCP Client CLI Tools

Available Commands:
  hexaeight-start license-activation                       - Setup machine token utility for license activation
  hexaeight-check check-prerequisites                      - Verify .NET and dotnet-script installation  
  hexaeight-create directory-linked-to-hexaeight-license <dir> - Create project directory with license hardlinks
  hexaeight-start generate-parent-or-child-agent-licenses - Generate agent configuration files
  hexaeight-deploy multi-ai-agent-samples                 - Deploy sample multi-agent weather system
  hexaeight-setup portable-child-agent-environment [config] - Setup portable child agent on secondary machine

Examples:
  hexaeight-start license-activation
  hexaeight-check check-prerequisites
  hexaeight-create directory-linked-to-hexaeight-license my-project
  hexaeight-start generate-parent-or-child-agent-licenses
  hexaeight-deploy multi-ai-agent-samples
  hexaeight-setup portable-child-agent-environment child_config.json

For more information, visit: https://github.com/HexaEightTeam/hexaeight-mcp-client
""")

# Console script entry points
def hexaeight_start():
    """Entry point for hexaeight-start commands"""
    
    # Handle help flags
    if len(sys.argv) < 2 or sys.argv[1] in ['--help', '-h', 'help']:
        print("🚀 HexaEight MCP Client - Start Commands")
        print("Usage: hexaeight-start <command>")
        print("")
        print("Available commands:")
        print("  license-activation                       - Setup machine token utility")
        print("  generate-parent-or-child-agent-licenses - Generate agent configs")
        print("")
        print("Examples:")
        print("  hexaeight-start license-activation")
        print("  hexaeight-start generate-parent-or-child-agent-licenses")
        return
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    if command == "license-activation":
        cli = LicenseActivationCLI()
        cli.run(args)
    elif command == "generate-parent-or-child-agent-licenses":
        cli = AgentGenerationCLI()
        cli.run(args)
    else:
        print(f"❌ Unknown hexaeight-start command: {command}")
        print("Run 'hexaeight-start --help' for available commands")
        sys.exit(1)

def hexaeight_check():
    """Entry point for hexaeight-check commands"""
    
    # Handle help flags
    if len(sys.argv) < 2 or sys.argv[1] in ['--help', '-h', 'help']:
        print("🔍 HexaEight MCP Client - Check Commands")
        print("Usage: hexaeight-check <command>")
        print("")
        print("Available commands:")
        print("  check-prerequisites - Verify system requirements")
        print("")
        print("Examples:")
        print("  hexaeight-check check-prerequisites")
        return
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    if command == "check-prerequisites":
        cli = PrerequisitesCLI()
        cli.run(args)
    else:
        print(f"❌ Unknown hexaeight-check command: {command}")
        print("Run 'hexaeight-check --help' for available commands")
        sys.exit(1)

def hexaeight_create():
    """Entry point for hexaeight-create commands"""
    
    # Handle help flags
    if len(sys.argv) < 2 or sys.argv[1] in ['--help', '-h', 'help']:
        print("📁 HexaEight MCP Client - Create Commands")
        print("Usage: hexaeight-create <command>")
        print("")
        print("Available commands:")
        print("  directory-linked-to-hexaeight-license <dir> - Create project directory")
        print("")
        print("Examples:")
        print("  hexaeight-create directory-linked-to-hexaeight-license my-project")
        return
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    if command == "directory-linked-to-hexaeight-license":
        if not args:
            print("❌ Error: Directory name required")
            print("Usage: hexaeight-create directory-linked-to-hexaeight-license <directory_name>")
            sys.exit(1)
        cli = DirectorySetupCLI()
        cli.run(args[0])
    else:
        print(f"❌ Unknown hexaeight-create command: {command}")
        print("Run 'hexaeight-create --help' for available commands")
        sys.exit(1)

def hexaeight_deploy():
    """Entry point for hexaeight-deploy commands"""
    
    # Handle help flags
    if len(sys.argv) < 2 or sys.argv[1] in ['--help', '-h', 'help']:
        print("🚀 HexaEight MCP Client - Deploy Commands")
        print("Usage: hexaeight-deploy <command>")
        print("")
        print("Available commands:")
        print("  multi-ai-agent-samples - Deploy sample weather agent system")
        print("")
        print("Examples:")
        print("  hexaeight-deploy multi-ai-agent-samples")
        return
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    if command == "multi-ai-agent-samples":
        cli = SampleDeploymentCLI()
        cli.run(args)
    else:
        print(f"❌ Unknown hexaeight-deploy command: {command}")
        print("Run 'hexaeight-deploy --help' for available commands")
        sys.exit(1)

def hexaeight_setup():
    """Entry point for hexaeight-setup commands"""
    
    # Handle help flags
    if len(sys.argv) < 2 or sys.argv[1] in ['--help', '-h', 'help']:
        print("🔧 HexaEight MCP Client - Setup Commands")
        print("Usage: hexaeight-setup <command>")
        print("")
        print("Available commands:")
        print("  portable-child-agent-environment [config] - Setup child agent on secondary machine")
        print("")
        print("Examples:")
        print("  hexaeight-setup portable-child-agent-environment")
        print("  hexaeight-setup portable-child-agent-environment child_config.json")
        return
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    if command == "portable-child-agent-environment":
        cli = PortableSetupCLI()
        cli.run(args)
    else:
        print(f"❌ Unknown hexaeight-setup command: {command}")
        print("Run 'hexaeight-setup --help' for available commands")
        sys.exit(1)
