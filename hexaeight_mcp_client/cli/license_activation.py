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
    save_package_state
)

class LicenseActivationCLI:
    """CLI for license activation using machine token utility"""
    
    def run(self, args: List[str]) -> None:
        """Run license activation process"""
        
        print_section(
            "HexaEight License Activation",
            "This will set up the machine token utility for license activation."
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
            
            # Step 3: Guide through purchase and activation
            self._guide_license_purchase_and_activation(executable_path)
            
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
    
    def _guide_license_purchase_and_activation(self, executable_path: str) -> None:
        """Guide user through license purchase and activation"""
        
        print_section("AI Agent Identity & License Setup", "Understanding the HexaEight AI Agent Identity System...")
        
        # Explain the concept
        self._explain_agent_identity_concept()
        
        # Guide through domain setup
        self._guide_domain_setup()
        
        # Explain the value proposition
        self._explain_license_value_proposition()
        
        # Show activation process
        self._show_activation_process(executable_path)
    def _start_license_activation(self, executable_path: str) -> None:
        """Start interactive license activation"""
        
        print_section("🚀 License Activation", "Activating your AI agent identity license...")
        
        print(f"🔑 **License Activation Process Starting**")
        print(f"")
        print(f"The machine token utility will now:")
        print(f"   1. 🔤 Ask for your resource name (e.g., weather-agent.yourdomain.com)")
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
        print(f"🏢 **Immediate Actions Available:**")
        print(f"   1. 🎯 Create Parent Agent (runs on this machine)")
        print(f"      hexaeight-start generate-parent-or-child-agent-licenses")
        print(f"")
        print(f"   2. 🏗️  Create Project Directories")
        print(f"      hexaeight-create directory-linked-to-hexaeight-license my-ai-project")
        print(f"")
        print(f"   3. 🌤️  Deploy Sample Multi-Agent Weather System")
        print(f"      hexaeight-deploy multi-ai-agent-samples")
        print(f"")
        print(f"👥 **Start Building Your Agent Army:**")
        print(f"   • Create parent agent config (machine-bound, no password)")
        print(f"   • Generate unlimited child agents (32+ char passwords)")
        print(f"   • Deploy child agents to cloud, edge devices, anywhere!")
        print(f"   • Build secure multi-agent AI applications")
        print(f"")
        print(f"🌟 **Remember the Strategy:**")
        print(f"   ⏰ License Duration: Limited time to create agents")
        print(f"   👥 Child Agents: Unlimited creation during license period")
        print(f"   ♾️  Child Longevity: Work forever, even after license expires")
        print(f"   💎 Value: Permanent AI infrastructure from temporary license")
        print(f"")
        print(f"🚀 **Recommended First Steps:**")
        print(f"   1. Create a parent agent configuration")
        print(f"   2. Create 5-10 child agents immediately")
        print(f"   3. Test the sample weather system")
        print(f"   4. Build your own AI applications")
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
    
    def _explain_agent_identity_concept(self) -> None:
        """Explain the AI agent identity concept in an exciting way"""
        
        print(f"\n🎭 ✨ 🚀 Welcome to the Future of AI! 🚀 ✨ 🎭")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"")
        print(f"💫 You're about to create something AMAZING...")
        print(f"🤖 Professional AI agents with their own digital identities!")
        print(f"")
        print(f"🌟 Think Netflix, but for AI agents → weather-agent.yourcompany.com")
        print(f"🌟 Think Gmail, but for AI agents → assistant-bot.yourbusiness.net")
        print(f"🌟 Think Slack, but for AI agents → data-analyst.myservices.org")
        print(f"")
        print(f"🎯 Why is this REVOLUTIONARY?")
        print(f"   💼 Professional business identity")
        print(f"   🔐 Military-grade security") 
        print(f"   🌍 Works globally, anywhere")
        print(f"   ⚡ Enterprise-ready from day one")
        print(f"")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    def _guide_domain_setup(self) -> None:
        """Guide through domain and email setup with visual appeal"""
        
        print(f"\n🛠️  ✨ Quick Setup Guide (Super Easy!) ✨ 🛠️")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"")
        
        print(f"🌐 ① Get a Domain (5 minutes)")
        print(f"   💡 Need: yourcompany.com or yourbusiness.net")
        print(f"   💰 Cost: ~$10-15/year (coffee money!)")
        print(f"   🛒 Where: GoDaddy, Namecheap, Google Domains")
        print(f"")
        
        print(f"📧 ② Create Domain Email (2 minutes)")
        print(f"   ✨ Examples: admin@yourdomain.com")
        print(f"   ✨ Examples: ai@yourbusiness.com")
        print(f"")
        
        print(f"📱 ③ Download HexaEight App (1 minute)")
        print(f"   🎯 Search: 'HexaEight Authenticator'")
        print(f"   📲 Available: iOS & Android")
        print(f"   ✅ Register with your domain email")
        print(f"")
        
        print(f"🔧 ④ Create AI Agent Resource (3 minutes)")
        print(f"   🎨 Name: weather-agent.yourdomain.com")
        print(f"   📝 App gives you DNS record → copy to domain")
        print(f"   ✅ Verify ownership → DONE!")
        print(f"")
        print(f"⏰ Total time: ~11 minutes to AI agent greatness!")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    def _explain_license_value_proposition(self) -> None:
        """Explain the value proposition with excitement and visual appeal"""
        
        print(f"\n💎 🚀 🎉 The INCREDIBLE License Deal! 🎉 🚀 💎")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"")
        
        print(f"🤯 Here's the MIND-BLOWING part...")
        print(f"")
        print(f"👑 Parent Agent:")
        print(f"   🏢 Runs on your machine")
        print(f"   ⏰ Valid for license duration")
        print(f"   🔑 No passwords needed")
        print(f"")
        
        print(f"🌟 Child Agents (THE MAGIC!):")
        print(f"   ♾️  UNLIMITED creation!")
        print(f"   💪 NEVER EXPIRE!")
        print(f"   🌍 Run ANYWHERE!")
        print(f"   🔐 Military-grade security!")
        print(f"")
        
        print(f"💰 The Math That Will Blow Your Mind:")
        print(f"")
        print(f"   💵 License cost: ~$25-50")
        print(f"   ⚡ Create 20 child agents in 5 days")
        print(f"   ♾️  Those agents work FOREVER")
        print(f"   📊 Cost per agent: $1.25-2.50")
        print(f"   🎯 Value: PRICELESS!")
        print(f"")
        
        print(f"🚀 Your Strategy:")
        print(f"   ① Buy short license (smart move!)")
        print(f"   ② Create MANY child agents (go crazy!)")
        print(f"   ③ Deploy everywhere (cloud, edge, mobile!)")
        print(f"   ④ Profit from permanent AI workforce!")
        print(f"")
        
        print(f"🎊 BONUS FEATURES:")
        print(f"   🔒 Zero external threats")
        print(f"   🤝 Agents talk to each other securely")
        print(f"   📡 Global PubSub network")
        print(f"   🎯 Enterprise-ready instantly")
        print(f"")
        
        print(f"🏆 Bottom Line: One coffee's worth = AI empire!")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    def _show_activation_process(self, executable_path: str) -> None:
        """Show the activation process with visual excitement"""
        
        print(f"\n🎯 ✨ License Activation Magic! ✨ 🎯")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"")
        
        print(f"🛒 ① Visit Store")
        print(f"   🌐 https://store.hexaeight.com")
        print(f"   💡 Pick your license duration")
        print(f"")
        
        print(f"🔧 ② Run Magic Command")
        print(f"   ✨ ./{os.path.basename(executable_path)} --newtoken")
        print(f"   🎯 Enter: weather-agent.yourdomain.com")
        print(f"")
        
        print(f"📱 ③ QR Code Fun")
        print(f"   📸 Machine shows QR code")
        print(f"   👆 Tap your resource in app")
        print(f"   ⚡ Scan & approve")
        print(f"")
        
        print(f"🎉 ④ BOOM! Licensed!")
        print(f"   ⏎  Press Enter")
        print(f"   📄 hexaeight.mac created")
        print(f"   🚀 Ready to build!")
        print(f"")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # Ask with more excitement
        print(f"\n🎪 Ready to join the AI revolution?")
        
        if confirm_action("🚀 Start activation now? (Have your domain resource ready!)", default=False):
            self._start_license_activation(executable_path)
        else:
            print(f"\n🎯 No worries! Complete these quick steps:")
            print(f"")
            print(f"   🌐 Get domain → 📧 Create email → 📱 Setup app → 🔧 Create resource")
            print(f"")
            print(f"🎊 Then return and run:")
            print(f"   ✨ ./{os.path.basename(executable_path)} --newtoken")
            print(f"")
            print(f"🎈 Your machine is ready at: {os.getcwd()}")
        
        print(f"\n🔄 Renewal when needed:")
        print(f"   ⚡ ./{os.path.basename(executable_path)} --renewtoken")
