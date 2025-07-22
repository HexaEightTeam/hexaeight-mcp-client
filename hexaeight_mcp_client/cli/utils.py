"""
Common utilities for HexaEight CLI tools
"""

import os
import sys
import platform
import subprocess
import zipfile
import shutil
import json
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import pkg_resources

def get_platform_info() -> Tuple[str, str]:
    """Get platform information for selecting correct binary"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "windows":
        return "win-x64", "HexaEight-Machine-Tokens-Utility.exe"
    elif system == "darwin":  # macOS
        return "osx-64", "HexaEight-Machine-Tokens-Utility"
    elif system == "linux":
        if machine in ["arm", "aarch64", "arm64"]:
            return "arm-x64", "HexaEight-Machine-Tokens-Utility"
        else:
            return "linux-64", "HexaEight-Machine-Tokens-Utility"
    else:
        raise Exception(f"Unsupported platform: {system}")

def extract_machine_token_utility() -> str:
    """Extract machine token utility to current directory"""
    platform_name, executable_name = get_platform_info()
    
    print(f"🔍 Detected platform: {platform_name}")
    print(f"📦 Extracting machine token utility for {platform_name}...")
    
    try:
        # Get the zip file from package resources
        zip_filename = f"{platform_name}.zip"
        zip_data = pkg_resources.resource_string('hexaeight_mcp_client', f'bin/{zip_filename}')
        
        # Write zip to temp file and extract
        temp_zip = f"temp_{zip_filename}"
        with open(temp_zip, 'wb') as f:
            f.write(zip_data)
        
        # Extract to current directory
        with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
            zip_ref.extractall('.')
        
        # Clean up temp zip
        os.remove(temp_zip)
        
        # NEW: Move files from subdirectory to current directory
        extracted_dir = os.path.join('.', platform_name)
        if os.path.exists(extracted_dir):
            print(f"📁 Moving files from {extracted_dir}/ to current directory...")
            
            # Move all files from subdirectory to current directory
            for filename in os.listdir(extracted_dir):
                source_path = os.path.join(extracted_dir, filename)
                dest_path = os.path.join('.', filename)
                
                # Remove destination if it exists
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                
                # Move file
                shutil.move(source_path, dest_path)
                print(f"📄 Moved: {filename}")
            
            # Remove empty subdirectory
            os.rmdir(extracted_dir)
            print(f"🗑️  Removed empty directory: {extracted_dir}")
        
        # Make executable on Unix systems
        executable_path = os.path.join('.', executable_name)
        if os.path.exists(executable_path) and platform.system() != "Windows":
            os.chmod(executable_path, 0o755)
        
        print(f"✅ Machine token utility extracted: {executable_path}")
        return executable_path
        
    except Exception as e:
        raise Exception(f"Failed to extract machine token utility: {e}")

def run_command(command: List[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=check)
        return result
    except subprocess.CalledProcessError as e:
        raise Exception(f"Command failed: {' '.join(command)}\nError: {e.stderr}")

def check_command_exists(command: str) -> bool:
    """Check if a command exists in PATH"""
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def find_license_directory() -> Optional[str]:
    """Find directory containing hexaeight.mac license file"""
    # Check current directory first
    if os.path.exists("hexaeight.mac"):
        return os.getcwd()
    
    # Check parent directories
    current = os.getcwd()
    while current != os.path.dirname(current):  # Not root
        parent = os.path.dirname(current)
        license_path = os.path.join(parent, "hexaeight.mac")
        if os.path.exists(license_path):
            return parent
        current = parent
    
    return None

def create_hardlink(source: str, destination: str) -> bool:
    """Create a hardlink, with fallback to copy on Windows"""
    try:
        os.link(source, destination)
        return True
    except OSError:
        # Fallback to copy on systems that don't support hardlinks
        shutil.copy2(source, destination)
        print(f"⚠️  Created copy instead of hardlink: {destination}")
        return False

def get_template_content(template_path: str) -> str:
    """Get content from package template"""
    try:
        return pkg_resources.resource_string('hexaeight_mcp_client', f'templates/{template_path}').decode('utf-8')
    except Exception as e:
        raise Exception(f"Failed to read template {template_path}: {e}")

def write_template_file(template_path: str, destination: str, replacements: Dict[str, str] = None) -> None:
    """Write template file with optional string replacements"""
    content = get_template_content(template_path)
    
    if replacements:
        for key, value in replacements.items():
            content = content.replace(key, value)
    
    with open(destination, 'w') as f:
        f.write(content)
    
    print(f"✅ Created: {destination}")

def confirm_action(message: str, default: bool = False) -> bool:
    """Ask user for confirmation"""
    default_str = "Y/n" if default else "y/N"
    response = input(f"{message} ({default_str}): ").strip().lower()
    
    if not response:
        return default
    
    return response in ['y', 'yes']

def print_section(title: str, content: str = None):
    """Print a formatted section"""
    print(f"\n{'='*60}")
    print(f"🔧 {title}")
    print(f"{'='*60}")
    if content:
        print(content)

def validate_environment_variables(required_vars: List[str]) -> Dict[str, str]:
    """Validate that required environment variables are set"""
    missing = []
    values = {}
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
        else:
            values[var] = value
    
    if missing:
        raise Exception(f"Missing required environment variables: {', '.join(missing)}")
    
    return values

def save_package_state(key: str, value: Any) -> None:
    """Save state information for the package"""
    state_dir = os.path.expanduser("~/.hexaeight-mcp-client")
    os.makedirs(state_dir, exist_ok=True)
    
    state_file = os.path.join(state_dir, "state.json")
    
    # Load existing state
    state = {}
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
        except:
            pass
    
    # Update and save
    state[key] = value
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

def load_package_state() -> Dict[str, Any]:
    """Load package state information"""
    state_file = os.path.expanduser("~/.hexaeight-mcp-client/state.json")
    
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r') as f:
                return json.load(f)
        except:
            pass
    
    return {}
