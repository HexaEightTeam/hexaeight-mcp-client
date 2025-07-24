"""
Enhanced License activation CLI for HexaEight MCP Client
"""

import os
import subprocess
from typing import List
from .utils import (
    download_machine_token_utility,
    print_section, 
    confirm_action,
    save_package_state,
    get_template_content
)

class LicenseActivationCLI:
    """CLI for license activation using machine token utility"""
    
    def run(self, args: List[str]) -> None:
        """Run license activation process"""
        
        print_section(
            "HexaEight License Activation",
            "Set up the machine token utility for AI agent license activation."
        )
        
        # Check current directory
        current_dir = os.getcwd()
        print(f"📁 Current directory: {current_dir}")
        
        # Warn about license file location
        print(f"\n⚠️  IMPORTANT: License File Location")
        print(f"   • The license file (hexaeight.mac) will be created in: {current_dir}")
        print(f"   • Once created, it CANNOT be moved to another location")
        print(f"   • Only hardlinks can be created to reference it from other directories")
        print(f"   • Make sure this is the correct directory for your license file")
        
        if not confirm_action("Continue with license activation setup in this directory?"):
            print("👋 License activation cancelled")
            return
        
        try:
            # Step 1: Extract machine token utility
            executable_path = self._extract_utility()
            
            # Step 2: Run system verification
            self._run_system_verification(executable_path)
            
            # Step 3: Show the updated guide from markdown
            self._show_activation_guide(executable_path)
            
        except Exception as e:
            print(f"❌ License activation setup failed: {e}")
            raise
    
    def _extract_utility(self) -> str:
        """Extract and setup machine token utility"""
        executable_path = download_machine_token_utility()
        
        # Save license directory for future reference
        save_package_state("license_directory", os.getcwd())
        
        print_section("Machine Token Utility Ready")
        print(f"✅ Machine token utility extracted: {executable_path}")
        print(f"📁 Working directory: {os.getcwd()}")
        
        return executable_path
    
    def _run_system_verification(self, executable_path: str) -> None:
        """Run system verification checks"""
        
        print_section("System Verification", "Checking your system for license compatibility...")
        
        # Always run CPU check
        print(f"🔍 Step 1: Checking CPU cores for license sizing...")
        if confirm_action("Check CPU cores now?", default=True):
            self._run_cpu_check(executable_path)
        
        print(f"\n🔍 Step 2: Verifying environment compatibility...")
        if confirm_action("Verify environment now?", default=True):
            self._run_environment_check(executable_path)
        
        print_section("✅ System Verification Complete", "Your system is ready for HexaEight license activation!")
    
    def _show_activation_guide(self, executable_path: str) -> None:
        """Show the complete activation guide from markdown template"""
        
        try:
            # Load the markdown content
            guide_content = get_template_content("license_activation_guide.md")
            
            # Replace placeholder with actual license directory
            guide_content = guide_content.replace("{license_directory}", os.getcwd())
            
            # Convert markdown to formatted console output
            self._display_formatted_guide(guide_content, executable_path)
            
        except Exception as e:
            print(f"⚠️  Could not load activation guide: {e}")
            # Fallback to basic guide
            self._show_basic_activation_guide(executable_path)
    
    def _display_formatted_guide(self, content: str, executable_path: str) -> None:
        """Display the markdown content in a formatted way for console"""
        
        lines = content.split('\n')
        
        for line in lines:
            # Skip markdown headers that are just # symbols
            if line.strip().startswith('#') and not line.strip().startswith('##'):
                continue
                
            # Convert ## headers to section breaks
            if line.strip().startswith('##'):
                title = line.replace('##', '').strip()
                print_section(title)
                continue
            
            # Convert ### headers to bold text
            if line.strip().startswith('###'):
                title = line.replace('###', '').strip()
                print(f"\n{title}")
                print("─" * len(title))
                continue
            
            # Handle code blocks
            if line.strip().startswith('```'):
                continue
                
            # Handle lists and regular content
            if line.strip():
                print(line)
            else:
                print()  # Empty line
        
        # Show the final activation prompt
        self._show_activation_prompt(executable_path)
    
    def _show_basic_activation_guide(self, executable_path: str) -> None:
        """Fallback basic activation guide"""
        
        print_section("🎯 ✨ AI Agent License Activation! ✨ 🎯")
        
        print(f"🎲 **NEW: No Domain Required!**")
        print(f"   Generate unique agent names instantly with HexaEight app")
        print(f"   Examples: storm23-cloud-wave-bright09, app8-metal-zip-forward07")
        print(f"")
        print(f"📱 **Quick Setup (2 minutes):**")
        print(f"   1. Download 'HexaEight Authenticator' app")
        print(f"   2. Register with any email address")
        print(f"   3. Tap 'Create Generic Resource' → get random name")
        print(f"   4. Ready to use!")
        print(f"")
        print(f"💰 **Incredible Value:**")
        print(f"   • License: ~$25-50")
        print(f"   • Create unlimited child agents")
        print(f"   • Child agents work forever!")
        print(f"   • Deploy anywhere globally")
        print(f"")
        print(f"🚀 **Activation Steps:**")
        print(f"   1. Visit: https://store.hexaeight.com")
        print(f"   2. Run: ./{os.path.basename(executable_path)} --newtoken")
        print(f"   3. Enter your generic resource name")
        print(f"   4. Scan QR code with app")
        print(f"   5. BOOM! Licensed and ready!")
        
        self._show_activation_prompt(executable_path)
    
    def _show_activation_prompt(self, executable_path: str) -> None:
        """Show the activation prompt"""
        
        print(f"\n🎪 Ready to join the AI revolution?")
        
        if confirm_action("🚀 Start license activation now? (Have your generic resource ready!)", default=False):
            self._start_license_activation(executable_path)
        else:
            print(f"\n🎯 No worries! Complete these quick steps:")
            print(f"")
            print(f"   📱 Download HexaEight app → 🎲 Create generic resource → 🛒 Purchase license")
            print(f"")
            print(f"🎊 Then return and run:")
            print(f"   ✨ ./{os.path.basename(executable_path)} --newtoken")
            print(f"")
            print(f"🎈 Your machine is ready at: {os.getcwd()}")
        
        print(f"\n🔄 Future renewals:")
        print(f"   ⚡ ./{os.path.basename(executable_path)} --renewtoken")
    
    def _start_license_activation(self, executable_path: str) -> None:
        """Start interactive license activation"""
        
        print_section("🚀 License Activation", "Activating your AI agent identity license...")
        
        print(f"🔑 **License Activation Process Starting**")
        print(f"")
        print(f"The machine token utility will now:")
        print(f"   1. 🎲 Ask for your generic resource name (e.g., storm23-cloud-wave-bright09)")
        print(f"   2. 📱 Display a QR code URL for verification")
        print(f"   3. ⏳ Wait for your approval via HexaEight Authenticator app")
        print(f"   4. ✅ Create your license file upon verification")
        print(f"")
        print(f"📋 Running: {os.path.basename(executable_path)} --newtoken")
        print(f"=" * 60)
        
        try:
            # Run license activation interactively
            result = subprocess.run([executable_path, "--newtoken"], check=True)
            
            print(f"=" * 60)
            print_section("🎉 License Activation Complete!")
            
            # Check if license file was created
            license_file = os.path.join(os.getcwd(), "hexaeight.mac")
            if os.path.exists(license_file):
                print(f"✅ License file created: {license_file}")
                print(f"🔒 This file contains your HexaEight AI agent license")
                print(f"⚠️  Keep this file secure and do not move it from this directory")
                
                # Show the exciting next steps
                self._show_license_success_next_steps()
            else:
                print(f"⚠️  License file not found - activation may have failed")
                print(f"💡 Check the output above for any error messages")
                print(f"🔄 You can try again with: ./{os.path.basename(executable_path)} --newtoken")
        
        except subprocess.CalledProcessError as e:
            print(f"=" * 60)
            print(f"❌ License activation failed with exit code: {e.returncode}")
            print(f"💡 Please check the error messages above")
            print(f"🔄 You can try again with: ./{os.path.basename(executable_path)} --newtoken")
        
        except KeyboardInterrupt:
            print(f"\n👋 License activation cancelled by user")
            print(f"💡 You can resume anytime with: ./{os.path.basename(executable_path)} --newtoken")
        
        except Exception as e:
            print(f"❌ License activation error: {e}")
    
    def _show_license_success_next_steps(self) -> None:
        """Show exciting next steps after successful license activation"""
        
        print_section("🚀 Your AI Agent Empire Begins Now!", "What you can do with your new license...")
        
        print(f"🎊 **Congratulations! Your AI Agent License is Active!**")
        print(f"")
        print(f"💪 **You Now Have Super Powers:**")
        print(f"")
        print(f"🏢 **Next Steps - Execute These Commands:**")
        print(f"")
        print(f"   1. 🏗️  Create organized workspace:")
        print(f"      hexaeight-start create-directory-linked-to-hexaeight-license my-ai-project")
        print(f"")
        print(f"   2. 🎯 Generate agent configurations:")
        print(f"      hexaeight-start generate-parent-or-child-agent-licenses")
        print(f"")
        print(f"   3. 🌤️  Deploy sample multi-agent system:")
        print(f"      hexaeight-start deploy-multi-ai-agent-samples")
        print(f"")
        print(f"   4. 📱 Setup portable child agents:")
        print(f"      hexaeight-start setup-portable-child-agent-environment")
        print(f"")
        print(f"👥 **Build Your Agent Army Strategy:**")
        print(f"   • Create parent agent config (machine-bound, no password)")
        print(f"   • Generate unlimited child agents (32+ char passwords)")
        print(f"   • Deploy child agents to cloud, edge devices, anywhere!")
        print(f"   • Child agents work forever, even after license expires!")
        print(f"")
        print(f"🌟 **Remember the Winning Strategy:**")
        print(f"   ⏰ License Duration: Limited time to create agents")
        print(f"   👥 Child Agents: Unlimited creation during license period")
        print(f"   ♾️  Child Longevity: Work forever, even after license expires")
        print(f"   💎 Value: Permanent AI infrastructure from temporary license")
        print(f"")
        print(f"🎯 **Your license directory:** {os.getcwd()}")
        print(f"💪 **Time to build the future!**")
    
    def _run_cpu_check(self, executable_path: str) -> None:
        """Run CPU cores check"""
        try:
            print(f"📋 Command: {os.path.basename(executable_path)} --cpucores")
            print(f"=" * 50)
            
            # Run without capturing output - let it run interactively
            result = subprocess.run([executable_path, "--cpucores"], check=True)
            
            print(f"=" * 50)
            print(f"✅ CPU check completed")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ CPU check failed with exit code: {e.returncode}")
        except Exception as e:
            print(f"❌ CPU check error: {e}")
    
    def _run_environment_check(self, executable_path: str) -> None:
        """Run environment verification"""
        try:
            print(f"📋 Command: {os.path.basename(executable_path)} --verifyenvironment")
            print(f"=" * 50)
            
            # Run without capturing output - let it run interactively
            result = subprocess.run([executable_path, "--verifyenvironment"], check=True)
            
            print(f"=" * 50)
            print(f"✅ Environment verification completed")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Environment verification failed with exit code: {e.returncode}")
        except Exception as e:
            print(f"❌ Environment verification error: {e}")
