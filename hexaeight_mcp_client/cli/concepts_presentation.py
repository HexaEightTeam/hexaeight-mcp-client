"""
HexaEight Concepts Presentation CLI
Show educational slides about HexaEight AI Agent concepts
"""

import time
from typing import List
from .utils import print_section, confirm_action

class ConceptsPresentationCLI:
    """CLI for showing HexaEight concepts presentation"""
    
    def run(self, args: List[str]) -> None:
        """Run concepts presentation"""
        
        print_section(
            "HexaEight AI Agent Concepts",
            "Educational presentation about enterprise AI agents"
        )
        
        # Check if user wants interactive mode
        interactive = len(args) == 0 or "--interactive" in args
        auto_advance = "--auto" in args
        
        if interactive and not auto_advance:
            print("🎯 Press Enter to advance slides, 'q' to quit, 's' to skip to end")
            print()
        
        slides = self._get_slides()
        
        for i, (title, content) in enumerate(slides, 1):
            print_section(f"Slide {i}: {title}")
            print(content)
            print(f"\n{'─' * 60}")
            print(f"Slide {i} of {len(slides)}")
            
            if interactive and not auto_advance:
                user_input = input("\nPress Enter for next slide (or 'q' to quit, 's' to skip): ").strip().lower()
                if user_input == 'q':
                    print("👋 Presentation ended")
                    return
                elif user_input == 's':
                    break
                print()
            elif auto_advance:
                time.sleep(3)  # Auto-advance after 3 seconds
            else:
                print("\n" + "="*60 + "\n")
        
        # Show completion message
        print_section("🎉 Concepts Presentation Complete!")
        print("🚀 Ready to start building your AI agent infrastructure?")
        print()
        print("Next steps:")
        print("   hexaeight-start license-activation")
        print("   hexaeight-start create-directory-linked-to-hexaeight-license my-project")
    
    def _get_slides(self) -> List[tuple]:
        """Get all presentation slides"""
        return [
            ("Welcome to Enterprise AI Agents 🚀", """
**Transform Your Business with Professional AI Agents**

• 🏢 **Enterprise-Grade Security**: Military-grade encryption and identity management
• 🌍 **Global Deployment**: Deploy anywhere with secure communication
• ⚡ **Instant Setup**: 2-minute activation with mobile app
• 💰 **Cost-Effective**: Build permanent AI workforce from temporary license
"""),
            
            ("Revolutionary Identity System 🎯", """
**Two Identity Options for Every Business Need**

**Option A: Generic Resources (2 minutes)**
🎲 Examples: storm23-cloud-wave-bright09, sec45-sensor-gale-glow25
✅ Instant deployment, no domain required
📱 Generate via HexaEight Authenticator app

**Option B: Domain Resources (4 minutes)**
🌐 Examples: weather-agent.yourcompany.com, api-bot.acme.corp
💼 Professional branding with your domain
📧 Requires domain email verification
"""),
            
            ("License Architecture 💡", """
**CPU-Based Pricing Model**

| CPU Count | 5-Day License | Strategy            |
|-----------|---------------|---------------------|
| 1 CPU     | $15          | Perfect for testing |
| 2 CPU     | $30          | Small business      |
| 4 CPU     | $59          | Enterprise          |

**🎯 Winning Strategy:**
• Buy minimal CPU license (5 days)
• Generate unlimited child agents (permanent)
• Deploy child agents everywhere
• Child agents work forever!
"""),
            
            ("Agent Architecture 🏗️", """
**Parent Agent (Licensed Machine)**
👑 Capabilities:
├── 🏭 Generate unlimited child agents
├── 📋 Create and delegate complex tasks  
├── 🌐 Direct cross-domain communication
└── 🔐 Enterprise security management

**Child Agents (Deployed Anywhere)**
👥 Characteristics:
├── ♾️  Never expire (work forever)
├── 🌍 Deploy anywhere (cloud, edge, IoT)
├── 🔐 Full encryption capabilities
└── 💰 Zero ongoing licensing costs
"""),
            
            ("Communication Architecture 🌐", """
┌─────────────────┐    Direct Secure    ┌─────────────────┐
│   Parent Agent  │ ←──── Channel ────→ │   Parent Agent  │
│ (weatherapi.com)│                     │  (hotelapi.com) │
└─────────────────┘                     └─────────────────┘
         │                                       │
         │ Delegates                             │ Delegates
         ▼                                       ▼
┌─────────────────┐    PubSub Channel    ┌─────────────────┐
│   Child Agents  │ ←──── Same App ────→ │   Child Agents  │
│   (App Bound)   │                      │   (App Bound)   │
└─────────────────┘                      └─────────────────┘

**Key Points:**
• 🔗 Parent-to-Parent: Direct secure communication across domains
• 👥 Child-to-Child: PubSub communication within same application
• 🏢 Enterprise: No application boundaries for parent agents
"""),
            
            ("Strategic Recommendations 🎯", """
**During License Period (5 days):**
✅ Create parent agent configuration immediately
✅ Generate 10-20 child agents (they're permanent!)
✅ Test multi-agent coordination with samples
✅ Deploy child agents to target environments

**Post-License Period (Forever):**
✅ Child agents continue working indefinitely
✅ Use parent agent for task delegation (while license active)
✅ Leverage cross-domain communication capabilities
✅ Scale with additional child agents as needed
"""),
            
            ("ROI Analysis 📊", """
**Investment vs. Return**

Initial Investment:
├── 1 CPU License (5 days): $15
├── Domain (optional): $12/year
└── Development time: 2-4 hours
   ─────────────────────────
   Total: ~$27 + 2-4 hours

Permanent Assets Created:
├── 1 Parent agent configuration
├── 10-20 Child agents (never expire)
├── Multi-agent coordination system
└── Enterprise security infrastructure
   ─────────────────────────
   Cost per permanent agent: $0.75 - $1.50

**Business Impact:**
• 🏭 Operational Efficiency: Automated workflows
• 🔐 Security Compliance: Military-grade encryption
• 📈 Scalability: No licensing overhead for child agents
• 🌍 Global Reach: Cross-domain enterprise integration
"""),
            
            ("Quick Start Workflow 🚀", """
**1. Prerequisites & License**
hexaeight-start check-prerequisites
hexaeight-start license-activation

**2. Organized Development**
hexaeight-start create-directory-linked-to-hexaeight-license my-ai-project
cd my-ai-project

**3. Agent Generation**
hexaeight-start generate-parent-or-child-agent-licenses

**4. Deploy & Test**
hexaeight-start deploy-multi-ai-agent-samples

**5. Scale Globally**
hexaeight-start setup-portable-child-agent-environment child_config.json
"""),
            
            ("Success Metrics 📈", """
**Technical Metrics**
• ⚡ Activation Time: 2-5 minutes from zero to licensed
• 🔐 Security Level: Military-grade encryption standard
• 🌍 Deployment Scope: Global, no geographic limitations
• ♾️ Agent Longevity: Child agents work indefinitely

**Business Metrics**
• 💰 Cost Efficiency: $0.75-$1.50 per permanent agent
• 📈 Scalability: Unlimited child agents per license
• 🚀 Time to Value: Deploy working agents in hours
• 🔄 ROI Timeline: Immediate value, permanent assets
"""),
            
            ("Ready to Start? 🎯", """
**Immediate Actions**
1. 📱 Download HexaEight Authenticator app
2. 🎲 Create generic resource or setup domain
3. 🛒 Purchase license at store.hexaeight.com
4. ⚡ Run activation process

**Development Journey**
1. 🔧 Generate agent configurations
2. 🌤️ Deploy sample multi-agent system
3. 🌍 Scale with portable child agents
4. 🏢 Build enterprise AI infrastructure

**Ready to transform your business with AI agents?**

Start with: hexaeight-start license-activation
""")
        ]

# Utility function to show concepts from anywhere
def show_hexaeight_concepts(interactive: bool = True, auto_advance: bool = False):
    """Show HexaEight concepts presentation"""
    cli = ConceptsPresentationCLI()
    args = []
    if interactive:
        args.append("--interactive")
    if auto_advance:
        args.append("--auto")
    cli.run(args)
