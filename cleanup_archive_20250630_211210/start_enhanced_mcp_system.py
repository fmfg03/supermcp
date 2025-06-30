#!/usr/bin/env python3
"""
Production starter for Enhanced MCP Enterprise System
LangGraph + Graphiti + MCP Integration
"""

import asyncio
import logging
import signal
import sys
import os
from pathlib import Path

# Add langgraph_system to path
sys.path.append(str(Path(__file__).parent / "langgraph_system"))

from langgraph_system.production_deployment import ProductionMCPSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/enhanced_mcp_system.log')
    ]
)

logger = logging.getLogger(__name__)

class EnhancedMCPSystemRunner:
    """Production runner for Enhanced MCP System"""
    
    def __init__(self):
        self.production_system = None
        self.running = False
        
    async def start_system(self):
        """Start the enhanced MCP system"""
        
        try:
            logger.info("=" * 80)
            logger.info("🚀 STARTING ENHANCED MCP ENTERPRISE SYSTEM")
            logger.info("🧠 LangGraph + Graphiti + MCP Integration")
            logger.info("=" * 80)
            
            # Initialize production system
            self.production_system = ProductionMCPSystem()
            await self.production_system.initialize_production_system()
            
            self.running = True
            
            logger.info("✅ Enhanced MCP System started successfully!")
            logger.info("🌟 World's first MCP + LangGraph + Graphiti enterprise system is now running")
            
            # Display system information
            await self._display_system_info()
            
            # Keep system running
            await self._run_system_loop()
            
        except Exception as e:
            logger.error(f"❌ Failed to start Enhanced MCP System: {e}")
            sys.exit(1)
    
    async def _display_system_info(self):
        """Display system information and capabilities"""
        
        print("\n" + "=" * 80)
        print("🎯 ENHANCED MCP ENTERPRISE SYSTEM - CAPABILITIES")
        print("=" * 80)
        
        print("\n🧠 TRIPLE-LAYER MEMORY SYSTEM:")
        print("   • IMMEDIATE: LangGraph state management (current conversation)")
        print("   • SHORT-TERM: MCP Memory Analyzer (recent interactions, embeddings)")
        print("   • LONG-TERM: Graphiti Knowledge Graph (relationships, temporal context)")
        
        print("\n🤖 ENHANCED AGENTS:")
        print("   • SAM: Advanced reasoning with full context awareness")
        print("   • Multi-agent collaboration via shared knowledge graph")
        print("   • Real-time knowledge sharing and synthesis")
        
        print("\n🔗 KNOWLEDGE GRAPH FEATURES:")
        print("   • Temporal relationship tracking")
        print("   • Cross-agent insight sharing")
        print("   • User preference learning")
        print("   • Context-aware search and retrieval")
        
        print("\n🏢 ENTERPRISE FEATURES:")
        print("   • Production-grade security and authentication")
        print("   • High availability and auto-scaling")
        print("   • Comprehensive monitoring and alerting")
        print("   • Disaster recovery and backup systems")
        
        # Get and display health status
        health = await self.production_system.comprehensive_health_check()
        print(f"\n💊 SYSTEM HEALTH: {'🟢 HEALTHY' if health['overall_healthy'] else '🔴 UNHEALTHY'}")
        
        for component, status in health.get("components", {}).items():
            status_icon = "🟢" if status.get("healthy") else "🔴"
            print(f"   • {component}: {status_icon} {status.get('status', 'unknown')}")
        
        # Get and display metrics
        metrics = await self.production_system.get_system_metrics()
        uptime = metrics["system_info"]["uptime_seconds"]
        print(f"\n📊 SYSTEM METRICS:")
        print(f"   • Uptime: {uptime:.1f} seconds")
        print(f"   • Environment: {metrics['system_info']['environment']}")
        
        print("\n" + "=" * 80)
        print("🎉 System ready for enhanced AI interactions!")
        print("=" * 80 + "\n")
    
    async def _run_system_loop(self):
        """Main system loop"""
        
        logger.info("Starting system monitoring loop...")
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            while self.running:
                # Perform periodic health checks
                await asyncio.sleep(30)  # Check every 30 seconds
                
                if self.production_system:
                    health = await self.production_system.comprehensive_health_check()
                    if not health["overall_healthy"]:
                        logger.warning("System health check failed - investigating...")
                        await self._handle_health_issues(health)
                
        except asyncio.CancelledError:
            logger.info("System loop cancelled - shutting down gracefully")
        except Exception as e:
            logger.error(f"Error in system loop: {e}")
        finally:
            await self._shutdown_system()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum} - initiating graceful shutdown...")
        self.running = False
    
    async def _handle_health_issues(self, health_status):
        """Handle system health issues"""
        
        logger.warning("Health issues detected:")
        for component, status in health_status.get("components", {}).items():
            if not status.get("healthy"):
                logger.warning(f"  - {component}: {status.get('status')} - {status.get('error', 'No details')}")
        
        # Attempt automatic recovery
        await self._attempt_auto_recovery()
    
    async def _attempt_auto_recovery(self):
        """Attempt automatic system recovery"""
        
        logger.info("Attempting automatic system recovery...")
        
        try:
            # Re-initialize systems if possible
            if self.production_system:
                # Try to reinitialize core components
                await self.production_system._initialize_core_systems()
                logger.info("Core systems reinitialized successfully")
                
        except Exception as e:
            logger.error(f"Auto-recovery failed: {e}")
    
    async def _shutdown_system(self):
        """Gracefully shutdown the system"""
        
        logger.info("🛑 Shutting down Enhanced MCP System...")
        
        try:
            if self.production_system:
                # Close connections and cleanup
                if hasattr(self.production_system, 'graphiti_integration'):
                    await self.production_system.graphiti_integration.close()
                
                logger.info("✅ System shutdown complete")
        
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

async def main():
    """Main entry point"""
    
    # Ensure log directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Create and start the system runner
    runner = EnhancedMCPSystemRunner()
    await runner.start_system()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Enhanced MCP System stopped by user")
    except Exception as e:
        print(f"\n❌ Enhanced MCP System failed: {e}")
        sys.exit(1)