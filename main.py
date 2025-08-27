#!/usr/bin/env python3
"""
Enhanced DataTobiz Brand Monitoring System - Main Application (Stage 2)

This is the main entry point for the enhanced brand monitoring system with
support for 3 LLM agents, ranking detection, cost tracking, and advanced analytics.

Features:
- Multi-agent orchestration (OpenAI, Perplexity, Gemini)
- Advanced ranking detection and analysis
- Cost tracking and performance monitoring
- Comprehensive analytics and reporting
- Enhanced Google Sheets integration
- Real-time progress tracking
"""

import asyncio
import argparse
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import time

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.workflow.graph import create_enhanced_workflow
from src.config.settings import get_settings, validate_stage2_requirements
from src.utils.logger import setup_logging, get_logger
from src.analytics.analytics_engine import generate_comprehensive_report

# Setup enhanced logging
setup_logging(log_level="INFO")
logger = get_logger(__name__)

class EnhancedBrandMonitoringAPI:
    """
    Enhanced API class for the DataTobiz Brand Monitoring System with Stage 2 features.
    
    Provides a comprehensive interface for brand monitoring with multi-agent
    orchestration, ranking detection, and advanced analytics.
    """
    
    def __init__(self, config_file: str = "config.yaml"):
        """Initialize the enhanced API with configuration."""
        self.config_file = config_file
        self.settings = None
        self.workflow = None
        self.execution_history: List[Dict[str, Any]] = []
        
        logger.info("🚀 Initializing Enhanced DataTobiz Brand Monitoring System (Stage 2)")
    
    async def initialize(self) -> bool:
        """
        Initialize the enhanced system with all Stage 2 components.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Load and validate configuration
            logger.info("Loading enhanced configuration...")
            self.settings = get_settings(self.config_file)
            
            # Validate Stage 2 requirements
            validation = validate_stage2_requirements()
            if not validation["valid"]:
                for error in validation["errors"]:
                    logger.error(f"❌ Configuration error: {error}")
                return False
            
            for warning in validation["warnings"]:
                logger.warning(f"⚠️  {warning}")
            
            # Log available features
            features = self.settings.get_stage2_features()
            enabled_features = [name for name, enabled in features.items() if enabled]
            logger.info(f"🎯 Stage 2 features enabled: {', '.join(enabled_features)}")
            
            # Initialize enhanced workflow
            logger.info("Initializing enhanced workflow with multi-agent support...")
            self.workflow = await create_enhanced_workflow(self.settings)
            
            # Log agent availability
            available_agents = list(self.workflow.agents.keys())
            logger.info(f"🤖 Available agents: {', '.join(available_agents)}")
            
            if len(available_agents) >= 3:
                logger.info("🎉 Full Stage 2 capability with 3 agents!")
            elif len(available_agents) >= 2:
                logger.info("✅ Multi-agent capability enabled")
            else:
                logger.warning("⚠️  Limited capability with only 1 agent")
            
            logger.info("✅ Enhanced system initialization completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Enhanced system initialization failed: {str(e)}")
            return False
    
    async def test_connections(self) -> Dict[str, Any]:
        """
        Test all system connections and capabilities.
        
        Returns:
            Dictionary with connection test results
        """
        logger.info("🔍 Testing enhanced system connections...")
        
        test_results = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "agents": {},
            "storage": {},
            "analytics": {},
            "stage2_features": {}
        }
        
        try:
            # Test agent connections
            if self.workflow and self.workflow.agents:
                for agent_name, agent in self.workflow.agents.items():
                    try:
                        logger.info(f"Testing {agent_name} agent...")
                        health_status = await agent.health_check()
                        
                        test_results["agents"][agent_name] = {
                            "available": True,
                            "healthy": health_status,
                            "model": agent._get_model_name(),
                            "provider": agent.__class__.__name__.replace('Agent', '')
                        }
                        
                        if health_status:
                            logger.info(f"✅ {agent_name} agent is healthy")
                        else:
                            logger.warning(f"⚠️  {agent_name} agent failed health check")
                            
                    except Exception as e:
                        logger.error(f"❌ {agent_name} agent test failed: {str(e)}")
                        test_results["agents"][agent_name] = {
                            "available": False,
                            "error": str(e)
                        }
                        test_results["success"] = False
            
            # Test storage connection
            if self.workflow and self.workflow.storage_manager:
                try:
                    logger.info("Testing enhanced Google Sheets storage...")
                    # Simple test by trying to get stats
                    stats = await self.workflow.storage_manager.get_enhanced_summary_stats()
                    test_results["storage"]["google_sheets"] = {
                        "available": True,
                        "records_found": len(stats) > 0,
                        "last_updated": stats.get("last_updated", "No data")
                    }
                    logger.info("✅ Enhanced Google Sheets storage is accessible")
                    
                except Exception as e:
                    logger.warning(f"⚠️  Enhanced Google Sheets test failed: {str(e)}")
                    test_results["storage"]["google_sheets"] = {
                        "available": False,
                        "error": str(e)
                    }
            else:
                test_results["storage"]["google_sheets"] = {
                    "available": False,
                    "reason": "Not configured"
                }
                logger.info("ℹ️  Google Sheets storage not configured")
            
            # Test analytics engine
            if self.workflow and self.workflow.analytics_engine:
                test_results["analytics"]["engine"] = {
                    "available": True,
                    "capabilities": ["trend_analysis", "performance_metrics", "competitive_intelligence"]
                }
                logger.info("✅ Analytics engine is available")
            else:
                test_results["analytics"]["engine"] = {
                    "available": False,
                    "reason": "Not initialized"
                }
            
            # Test Stage 2 features
            stage2_features = self.settings.get_stage2_features()
            test_results["stage2_features"] = stage2_features
            
            enabled_count = sum(1 for enabled in stage2_features.values() if enabled)
            logger.info(f"🎯 Stage 2 features: {enabled_count}/{len(stage2_features)} enabled")
            
        except Exception as e:
            logger.error(f"❌ Connection testing failed: {str(e)}")
            test_results["success"] = False
            test_results["error"] = str(e)
        
        return test_results
    
    async def monitor_queries(
        self,
        queries: List[str],
        mode: str = "parallel",
        enable_ranking: bool = None,
        enable_analytics: bool = None
    ) -> Dict[str, Any]:
        """
        Monitor brand mentions across queries with enhanced Stage 2 features.
        
        Args:
            queries: List of search queries to monitor
            mode: Execution mode ("parallel" or "sequential")
            enable_ranking: Override ranking detection setting
            enable_analytics: Override analytics setting
            
        Returns:
            Dictionary with enhanced monitoring results
        """
        if not self.workflow:
            return {"success": False, "error": "System not initialized"}
        
        logger.info(f"🔍 Starting enhanced brand monitoring for {len(queries)} queries in {mode} mode")
        
        start_time = time.time()
        
        try:
            # Override settings if specified
            original_ranking = self.settings.stage2.enable_ranking_detection
            original_analytics = self.settings.stage2.enable_analytics
            
            if enable_ranking is not None:
                self.settings.stage2.enable_ranking_detection = enable_ranking
            if enable_analytics is not None:
                self.settings.stage2.enable_analytics = enable_analytics
            
            # Execute enhanced workflow
            workflow_state = await self.workflow.execute_enhanced_workflow(
                queries=queries,
                processing_mode=mode,
                enable_analytics=enable_analytics
            )
            
            # Generate enhanced results
            results = await self._format_enhanced_results(workflow_state)
            
            # Add execution to history
            execution_record = {
                "timestamp": datetime.now().isoformat(),
                "queries": queries,
                "mode": mode,
                "results": results,
                "execution_time": time.time() - start_time,
                "stage2_features_used": {
                    "ranking_detection": self.settings.stage2.enable_ranking_detection,
                    "analytics": self.settings.stage2.enable_analytics,
                    "cost_tracking": self.settings.stage2.enable_cost_tracking
                }
            }
            self.execution_history.append(execution_record)
            
            logger.info(f"✅ Enhanced monitoring completed in {time.time() - start_time:.2f} seconds")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Enhanced monitoring failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        
        finally:
            # Restore original settings
            if enable_ranking is not None:
                self.settings.stage2.enable_ranking_detection = original_ranking
            if enable_analytics is not None:
                self.settings.stage2.enable_analytics = original_analytics
    
    async def _format_enhanced_results(self, workflow_state) -> Dict[str, Any]:
        """Format enhanced workflow results for API response."""
        # Basic summary
        total_queries = len(workflow_state.queries)
        processed_queries = len(workflow_state.query_states)
        
        brand_mentions = sum(
            1 for query_state in workflow_state.query_states.values()
            if query_state.overall_found
        )
        
        ranked_mentions = sum(
            1 for query_state in workflow_state.query_states.values()
            if query_state.overall_found and query_state.best_ranking
        )
        
        # Enhanced summary with Stage 2 metrics
        summary = {
            "total_queries": total_queries,
            "processed": processed_queries,
            "success_rate": processed_queries / max(total_queries, 1),
            "brand_mentions_found": brand_mentions,
            "brand_detection_rate": brand_mentions / max(processed_queries, 1),
            "ranked_mentions_found": ranked_mentions,
            "ranking_detection_rate": ranked_mentions / max(brand_mentions, 1),
            "execution_time": (workflow_state.end_time - workflow_state.start_time).total_seconds() if workflow_state.end_time and workflow_state.start_time else None
        }
        
        # Detailed results per query
        detailed_results = {}
        for query, query_state in workflow_state.query_states.items():
            query_result = {
                "found": query_state.overall_found,
                "confidence": query_state.consensus_confidence,
                "ranking": query_state.best_ranking,
                "ranking_sources": query_state.ranking_sources,
                "execution_time": query_state.total_execution_time if hasattr(query_state, 'total_execution_time') and query_state.total_execution_time is not None else None,
                "agents": {}
            }
            
            # Agent-level results
            for agent_name, agent_result in query_state.agent_results.items():
                agent_info = {
                    "status": agent_result.status.value,
                    "found": agent_result.brand_detection.found if agent_result.brand_detection else False,
                    "confidence": agent_result.brand_detection.confidence if agent_result.brand_detection else 0.0,
                    "ranking": agent_result.brand_detection.ranking_position if agent_result.brand_detection else None,
                    "execution_time": agent_result.execution_time if hasattr(agent_result, 'execution_time') and agent_result.execution_time is not None else None,
                    "model": agent_result.model_name,
                    "cost": agent_result.cost_estimate,
                    "error": agent_result.error_message
                }
                
                # Stage 2 enhanced data
                if agent_result.brand_detection:
                    agent_info.update({
                        "matches": agent_result.brand_detection.matches,
                        "context": agent_result.brand_detection.context,
                        "ranking_context": agent_result.brand_detection.ranking_context
                    })
                
                query_result["agents"][agent_name] = agent_info
            
            # Add quality metrics if available
            if hasattr(query_state, 'analysis'):
                query_result["quality_metrics"] = query_state.analysis
            
            detailed_results[query] = query_result
        
        # Analytics report if available
        analytics_report = None
        if (self.settings.stage2.enable_analytics and 
            hasattr(workflow_state, 'analytics_report')):
            analytics_report = workflow_state.analytics_report
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "results": detailed_results,
            "analytics": analytics_report,
            "agents_used": list(self.workflow.agents.keys()),
            "stage2_features": self.settings.get_stage2_features()
        }
    
    async def get_enhanced_stats(self) -> Dict[str, Any]:
        """Get enhanced historical statistics and analytics."""
        logger.info("📊 Retrieving enhanced statistics...")
        
        try:
            stats_result = {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "stats": None,
                "agent_performance": None,
                "execution_history": None
            }
            
            # Get storage statistics
            if self.workflow and self.workflow.storage_manager:
                try:
                    storage_stats = await self.workflow.storage_manager.get_enhanced_summary_stats()
                    stats_result["stats"] = storage_stats
                    logger.info("✅ Enhanced storage statistics retrieved")
                except Exception as e:
                    logger.warning(f"⚠️  Could not retrieve storage stats: {str(e)}")
            
            # Get agent performance statistics
            if self.workflow:
                try:
                    agent_stats = self.workflow.get_enhanced_performance_stats()
                    stats_result["agent_performance"] = agent_stats
                    logger.info("✅ Agent performance statistics retrieved")
                except Exception as e:
                    logger.warning(f"⚠️  Could not retrieve agent stats: {str(e)}")
            
            # Get execution history summary
            if self.execution_history:
                history_summary = {
                    "total_executions": len(self.execution_history),
                    "recent_executions": self.execution_history[-5:],  # Last 5 executions
                    "total_queries_processed": sum(
                        len(exec_record["queries"]) for exec_record in self.execution_history
                    )
                }
                stats_result["execution_history"] = history_summary
                logger.info("✅ Execution history retrieved")
            
            return stats_result
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve enhanced statistics: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def generate_analytics_report(self, days_back: int = 30) -> Dict[str, Any]:
        """Generate comprehensive analytics report for specified time period."""
        logger.info(f"📈 Generating comprehensive analytics report for last {days_back} days...")
        
        try:
            if not self.workflow or not self.workflow.analytics_engine:
                return {
                    "success": False,
                    "error": "Analytics engine not available"
                }
            
            # Get historical data
            if self.workflow.storage_manager:
                historical_data = await self.workflow.storage_manager.get_enhanced_historical_data(
                    days_back=days_back,
                    include_ranking_data=True
                )
                
                if not historical_data:
                    return {
                        "success": False,
                        "error": f"No data available for the last {days_back} days"
                    }
                
                # Generate comprehensive report
                # Note: This would require enhancing the analytics engine to work with historical data
                # For now, return a summary of the historical data
                
                report = {
                    "success": True,
                    "timestamp": datetime.now().isoformat(),
                    "time_period": f"Last {days_back} days",
                    "data_points": len(historical_data),
                    "summary": self._analyze_historical_data(historical_data)
                }
                
                logger.info("✅ Analytics report generated successfully")
                return report
            
            else:
                return {
                    "success": False,
                    "error": "Storage manager not available for historical analysis"
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to generate analytics report: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _analyze_historical_data(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze historical data for trends and insights."""
        if not historical_data:
            return {}
        
        # Basic analysis
        total_records = len(historical_data)
        brand_mentions = len([r for r in historical_data if r.get('Found_Y/N') == 'Y'])
        ranked_mentions = len([r for r in historical_data if r.get('Ranking_Position', '').strip()])
        
        # Agent analysis
        agent_usage = {}
        for record in historical_data:
            agent = record.get('Model_Name', 'Unknown')
            if agent not in agent_usage:
                agent_usage[agent] = {"total": 0, "found": 0}
            agent_usage[agent]["total"] += 1
            if record.get('Found_Y/N') == 'Y':
                agent_usage[agent]["found"] += 1
        
        # Ranking analysis
        rankings = []
        for record in historical_data:
            ranking_str = record.get('Ranking_Position', '').strip()
            if ranking_str:
                try:
                    rankings.append(int(ranking_str))
                except ValueError:
                    pass
        
        ranking_analysis = {}
        if rankings:
            ranking_analysis = {
                "total_ranked": len(rankings),
                "average_ranking": sum(rankings) / len(rankings),
                "best_ranking": min(rankings),
                "worst_ranking": max(rankings),
                "top_3_count": len([r for r in rankings if r <= 3]),
                "top_10_count": len([r for r in rankings if r <= 10])
            }
        
        return {
            "total_records": total_records,
            "brand_detection_rate": brand_mentions / max(total_records, 1),
            "ranking_detection_rate": ranked_mentions / max(brand_mentions, 1),
            "agent_performance": agent_usage,
            "ranking_analysis": ranking_analysis
        }
    
    async def cleanup(self):
        """Clean up system resources."""
        logger.info("🧹 Cleaning up enhanced system resources...")
        
        if self.workflow:
            await self.workflow.cleanup()
        
        logger.info("✅ Enhanced system cleanup completed")

# CLI Interface
async def main():
    """Main CLI interface for the enhanced brand monitoring system."""
    parser = argparse.ArgumentParser(
        description="Enhanced DataTobiz Brand Monitoring System (Stage 2)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --query "best data analytics companies"
  python main.py --query "top BI tools" "enterprise analytics platforms" --mode sequential
  python main.py --test-connections
  python main.py --stats
  python main.py --analytics-report --days 7
  python main.py --config custom_config.yaml
        """
    )
    
    parser.add_argument(
        "--query", "-q",
        nargs="+",
        help="Query or queries to monitor"
    )
    
    parser.add_argument(
        "--mode", "-m",
        choices=["parallel", "sequential"],
        default="parallel",
        help="Execution mode (default: parallel)"
    )
    
    parser.add_argument(
        "--config", "-c",
        default="config.yaml",
        help="Configuration file path (default: config.yaml)"
    )
    
    parser.add_argument(
        "--test-connections",
        action="store_true",
        help="Test all system connections"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show enhanced statistics"
    )
    
    parser.add_argument(
        "--analytics-report",
        action="store_true",
        help="Generate comprehensive analytics report"
    )
    
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days for analytics report (default: 30)"
    )
    
    parser.add_argument(
        "--enable-ranking",
        action="store_true",
        help="Enable ranking detection for this execution"
    )
    
    parser.add_argument(
        "--disable-ranking",
        action="store_true",
        help="Disable ranking detection for this execution"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output file for results (JSON format)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        setup_logging(log_level="DEBUG")
    
    # Initialize the enhanced system
    api = EnhancedBrandMonitoringAPI(args.config)
    
    try:
        # Initialize
        if not await api.initialize():
            print("❌ Failed to initialize the enhanced system")
            return 1
        
        # Handle different operations
        if args.test_connections:
            print("\n🔍 Testing Enhanced System Connections")
            print("=" * 50)
            
            result = await api.test_connections()
            
            if result["success"]:
                print("✅ Overall Status: HEALTHY")
            else:
                print("❌ Overall Status: ISSUES DETECTED")
            
            # Print agent status
            print(f"\n🤖 Agents ({len(result['agents'])} available):")
            for agent_name, agent_info in result["agents"].items():
                status = "✅" if agent_info.get("healthy", False) else "⚠️"
                model = agent_info.get("model", "Unknown")
                print(f"   {status} {agent_name:<12} ({model})")
            
            # Print storage status
            storage_info = result["storage"].get("google_sheets", {})
            if storage_info.get("available"):
                print(f"\n📊 Storage: ✅ Google Sheets Connected")
            else:
                print(f"\n📊 Storage: ⚠️  Google Sheets Not Available")
            
            # Print Stage 2 features
            features = result["stage2_features"]
            enabled_features = [name for name, enabled in features.items() if enabled]
            print(f"\n🎯 Stage 2 Features: {', '.join(enabled_features) if enabled_features else 'None enabled'}")
            
        elif args.stats:
            print("\n📊 Enhanced System Statistics")
            print("=" * 40)
            
            stats_result = await api.get_enhanced_stats()
            
            if stats_result["success"]:
                stats = stats_result.get("stats", {})
                if stats:
                    print(f"Total Results: {stats.get('total_results', 0)}")
                    print(f"Brand Mentions: {stats.get('brand_mentions_found', 0)} ({stats.get('detection_rate', 0):.1%})")
                    print(f"Ranked Mentions: {stats.get('ranked_mentions_found', 0)} ({stats.get('ranking_detection_rate', 0):.1%})")
                    print(f"Top 10 Rate: {stats.get('top_10_rate', 0):.1%}")
                    print(f"Average Execution Time: {stats.get('average_execution_time', 0):.2f}s")
                    
                    if stats.get('total_cost_estimate', 0) > 0:
                        print(f"Total Cost: ${stats['total_cost_estimate']:.4f}")
                else:
                    print("No historical data available")
                
                # Agent performance
                agent_perf = stats_result.get("agent_performance", {})
                if agent_perf:
                    print(f"\n🤖 Agent Performance:")
                    for agent_name, perf in agent_perf.items():
                        success_rate = perf.get("success_rate", 0)
                        avg_time = perf.get("average_execution_time", 0)
                        print(f"   {agent_name}: {success_rate:.1%} success, {avg_time:.2f}s avg")
            else:
                print(f"❌ Failed to retrieve statistics: {stats_result.get('error')}")
        
        elif args.analytics_report:
            print(f"\n📈 Generating Analytics Report (Last {args.days} days)")
            print("=" * 50)
            
            report = await api.generate_analytics_report(args.days)
            
            if report["success"]:
                summary = report.get("summary", {})
                print(f"Data Points: {report.get('data_points', 0)}")
                print(f"Detection Rate: {summary.get('brand_detection_rate', 0):.1%}")
                print(f"Ranking Rate: {summary.get('ranking_detection_rate', 0):.1%}")
                
                ranking_analysis = summary.get("ranking_analysis", {})
                if ranking_analysis:
                    print(f"Average Ranking: {ranking_analysis.get('average_ranking', 0):.1f}")
                    print(f"Best Ranking: {ranking_analysis.get('best_ranking', 'N/A')}")
                    print(f"Top 3 Mentions: {ranking_analysis.get('top_3_count', 0)}")
            else:
                print(f"❌ Failed to generate report: {report.get('error')}")
        
        elif args.query:
            print(f"\n🔍 Enhanced Brand Monitoring ({len(args.query)} queries)")
            print("=" * 50)
            
            # Handle ranking override
            enable_ranking = None
            if args.enable_ranking:
                enable_ranking = True
            elif args.disable_ranking:
                enable_ranking = False
            
            result = await api.monitor_queries(
                queries=args.query,
                mode=args.mode,
                enable_ranking=enable_ranking
            )
            
            if result["success"]:
                summary = result["summary"]
                print(f"✅ Monitoring completed successfully!")
                print(f"   Queries processed: {summary['processed']}/{summary['total_queries']}")
                print(f"   Brand mentions: {summary['brand_mentions_found']} ({summary['brand_detection_rate']:.1%})")
                print(f"   Ranked mentions: {summary['ranked_mentions_found']} ({summary['ranking_detection_rate']:.1%})")
                
                if summary.get('execution_time'):
                    print(f"   Execution time: {summary['execution_time'].total_seconds():.2f} seconds")
                
                print(f"\n📋 Detailed Results:")
                for query, query_result in result["results"].items():
                    status = "🎯 FOUND" if query_result["found"] else "❌ NOT FOUND"
                    confidence = f"({query_result['confidence']:.1%})" if query_result["found"] else ""
                    ranking = f" [Rank #{query_result['ranking']}]" if query_result.get("ranking") else ""
                    
                    print(f"   {query[:50]:<50} {status} {confidence}{ranking}")
                    
                    # Show agent breakdown
                    for agent_name, agent_result in query_result["agents"].items():
                        agent_status = "✅" if agent_result["status"] == "completed" else "❌"
                        agent_found = "🎯" if agent_result["found"] else "❌"
                        time_taken = f"{agent_result['execution_time']:.2f}s" if agent_result['execution_time'] else "N/A"
                        cost = f"${agent_result['cost']:.4f}" if agent_result.get('cost') else ""
                        
                        print(f"     └─ {agent_name:<12} {agent_status} {agent_found} ({time_taken}) {cost}")
                
                # Save output if requested
                if args.output:
                    with open(args.output, 'w') as f:
                        json.dump(result, f, indent=2, default=str)
                    print(f"\n💾 Results saved to {args.output}")
                
            else:
                print(f"❌ Monitoring failed: {result.get('error')}")
                return 1
        
        else:
            parser.print_help()
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation interrupted by user")
        return 1
    
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        return 1
    
    finally:
        await api.cleanup()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)