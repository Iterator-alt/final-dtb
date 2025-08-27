"""
Analytics Engine for DataTobiz Brand Monitoring System - Stage 2

This module provides comprehensive analytics capabilities including:
- Performance metrics analysis
- Trend analysis
- Competitive intelligence
- Cost analysis
- Quality metrics
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from src.workflow.state import WorkflowState, QueryState, AgentResult
from src.config.settings import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class AnalyticsMetrics:
    """Container for analytics metrics."""
    detection_rate: float
    ranking_detection_rate: float
    average_confidence: float
    average_execution_time: float
    total_cost: float
    agent_performance: Dict[str, Dict[str, Any]]
    quality_score: float
    trend_analysis: Dict[str, Any]

class BrandMonitoringAnalytics:
    """Advanced analytics engine for brand monitoring results."""
    
    def __init__(self, config=None):
        """Initialize the analytics engine."""
        self.config = config or get_settings()
        self.metrics_history: List[AnalyticsMetrics] = []
        
        logger.info("Analytics engine initialized")
    
    async def analyze_workflow_results(self, workflow_state: WorkflowState) -> Dict[str, Any]:
        """
        Analyze workflow results and generate comprehensive analytics.
        
        Args:
            workflow_state: The workflow state containing results
            
        Returns:
            Dictionary with comprehensive analytics
        """
        try:
            logger.info("Starting comprehensive analytics analysis")
            
            # Basic metrics
            basic_metrics = self._calculate_basic_metrics(workflow_state)
            
            # Performance analysis
            performance_metrics = self._analyze_performance(workflow_state)
            
            # Quality analysis
            quality_metrics = self._analyze_quality(workflow_state)
            
            # Cost analysis
            cost_metrics = self._analyze_costs(workflow_state)
            
            # Agent comparison
            agent_metrics = self._analyze_agent_performance(workflow_state)
            
            # Trend analysis
            trend_metrics = self._analyze_trends(workflow_state)
            
            # Compile comprehensive report
            analytics_report = {
                "timestamp": datetime.now().isoformat(),
                "workflow_id": workflow_state.workflow_id,
                "basic_metrics": basic_metrics,
                "performance_metrics": performance_metrics,
                "quality_metrics": quality_metrics,
                "cost_metrics": cost_metrics,
                "agent_metrics": agent_metrics,
                "trend_metrics": trend_metrics,
                "recommendations": self._generate_recommendations(
                    basic_metrics, performance_metrics, quality_metrics, cost_metrics
                )
            }
            
            logger.info("Comprehensive analytics analysis completed")
            return analytics_report
            
        except Exception as e:
            logger.error(f"Analytics analysis failed: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_basic_metrics(self, workflow_state: WorkflowState) -> Dict[str, Any]:
        """Calculate basic detection and success metrics."""
        total_queries = len(workflow_state.queries)
        successful_queries = len(workflow_state.query_states)
        
        brand_mentions = sum(
            1 for query_state in workflow_state.query_states.values()
            if query_state.overall_found
        )
        
        ranked_mentions = sum(
            1 for query_state in workflow_state.query_states.values()
            if query_state.overall_found and query_state.best_ranking
        )
        
        total_agents = sum(
            len(query_state.agent_results) 
            for query_state in workflow_state.query_states.values()
        )
        
        successful_agents = sum(
            sum(1 for result in query_state.agent_results.values() 
                if result.status.value == "completed")
            for query_state in workflow_state.query_states.values()
        )
        
        return {
            "total_queries": total_queries,
            "successful_queries": successful_queries,
            "success_rate": successful_queries / max(total_queries, 1),
            "brand_mentions_found": brand_mentions,
            "detection_rate": brand_mentions / max(successful_queries, 1),
            "ranked_mentions_found": ranked_mentions,
            "ranking_detection_rate": ranked_mentions / max(brand_mentions, 1),
            "total_agent_executions": total_agents,
            "successful_agent_executions": successful_agents,
            "agent_success_rate": successful_agents / max(total_agents, 1)
        }
    
    def _analyze_performance(self, workflow_state: WorkflowState) -> Dict[str, Any]:
        """Analyze execution performance metrics."""
        execution_times = []
        agent_times = {}
        
        for query_state in workflow_state.query_states.values():
            if query_state.total_execution_time:
                execution_times.append(query_state.total_execution_time)
            
            for agent_name, agent_result in query_state.agent_results.items():
                if agent_result.execution_time:
                    if agent_name not in agent_times:
                        agent_times[agent_name] = []
                    agent_times[agent_name].append(agent_result.execution_time)
        
        # Calculate performance metrics
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
        min_execution_time = min(execution_times) if execution_times else 0
        max_execution_time = max(execution_times) if execution_times else 0
        
        # Agent performance
        agent_performance = {}
        for agent_name, times in agent_times.items():
            agent_performance[agent_name] = {
                "average_time": sum(times) / len(times),
                "min_time": min(times),
                "max_time": max(times),
                "total_executions": len(times)
            }
        
        return {
            "average_execution_time": avg_execution_time,
            "min_execution_time": min_execution_time,
            "max_execution_time": max_execution_time,
            "total_execution_time": sum(execution_times),
            "agent_performance": agent_performance,
            "performance_efficiency": self._calculate_performance_efficiency(execution_times)
        }
    
    def _analyze_quality(self, workflow_state: WorkflowState) -> Dict[str, Any]:
        """Analyze result quality metrics."""
        confidences = []
        ranking_positions = []
        context_qualities = []
        
        for query_state in workflow_state.query_states.values():
            if query_state.consensus_confidence:
                confidences.append(query_state.consensus_confidence)
            
            if query_state.best_ranking:
                ranking_positions.append(query_state.best_ranking)
            
            # Analyze context quality for each agent result
            for agent_result in query_state.agent_results.values():
                if agent_result.brand_detection and agent_result.brand_detection.context:
                    context_length = len(agent_result.brand_detection.context)
                    context_qualities.append(min(1.0, context_length / 500))  # Normalize to 0-1
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        avg_ranking = sum(ranking_positions) / len(ranking_positions) if ranking_positions else None
        avg_context_quality = sum(context_qualities) / len(context_qualities) if context_qualities else 0
        
        return {
            "average_confidence": avg_confidence,
            "confidence_distribution": self._calculate_confidence_distribution(confidences),
            "average_ranking_position": avg_ranking,
            "best_ranking": min(ranking_positions) if ranking_positions else None,
            "top_10_rate": len([r for r in ranking_positions if r <= 10]) / len(ranking_positions) if ranking_positions else 0,
            "top_5_rate": len([r for r in ranking_positions if r <= 5]) / len(ranking_positions) if ranking_positions else 0,
            "average_context_quality": avg_context_quality,
            "quality_score": self._calculate_overall_quality_score(avg_confidence, avg_ranking, avg_context_quality)
        }
    
    def _analyze_costs(self, workflow_state: WorkflowState) -> Dict[str, Any]:
        """Analyze cost metrics if cost tracking is enabled."""
        if not self.config.stage2.enable_cost_tracking:
            return {"enabled": False}
        
        costs = []
        agent_costs = {}
        
        for query_state in workflow_state.query_states.values():
            for agent_name, agent_result in query_state.agent_results.items():
                if agent_result.cost_estimate:
                    costs.append(agent_result.cost_estimate)
                    
                    if agent_name not in agent_costs:
                        agent_costs[agent_name] = []
                    agent_costs[agent_name].append(agent_result.cost_estimate)
        
        total_cost = sum(costs) if costs else 0
        avg_cost = total_cost / len(costs) if costs else 0
        
        # Agent cost analysis
        agent_cost_analysis = {}
        for agent_name, agent_cost_list in agent_costs.items():
            agent_cost_analysis[agent_name] = {
                "total_cost": sum(agent_cost_list),
                "average_cost": sum(agent_cost_list) / len(agent_cost_list),
                "cost_per_query": sum(agent_cost_list) / len(workflow_state.queries)
            }
        
        return {
            "enabled": True,
            "total_cost": total_cost,
            "average_cost_per_result": avg_cost,
            "cost_per_query": total_cost / len(workflow_state.queries),
            "agent_costs": agent_cost_analysis,
            "cost_efficiency": self._calculate_cost_efficiency(costs, workflow_state)
        }
    
    def _analyze_agent_performance(self, workflow_state: WorkflowState) -> Dict[str, Any]:
        """Analyze individual agent performance."""
        agent_stats = {}
        
        for query_state in workflow_state.query_states.values():
            for agent_name, agent_result in query_state.agent_results.items():
                if agent_name not in agent_stats:
                    agent_stats[agent_name] = {
                        "total_executions": 0,
                        "successful_executions": 0,
                        "detections": 0,
                        "rankings": 0,
                        "execution_times": [],
                        "confidences": [],
                        "costs": []
                    }
                
                stats = agent_stats[agent_name]
                stats["total_executions"] += 1
                
                if agent_result.status.value == "completed":
                    stats["successful_executions"] += 1
                
                if agent_result.brand_detection and agent_result.brand_detection.found:
                    stats["detections"] += 1
                    if agent_result.brand_detection.confidence:
                        stats["confidences"].append(agent_result.brand_detection.confidence)
                
                if agent_result.brand_detection and agent_result.brand_detection.ranking_position:
                    stats["rankings"] += 1
                
                if agent_result.execution_time:
                    stats["execution_times"].append(agent_result.execution_time)
                
                if agent_result.cost_estimate:
                    stats["costs"].append(agent_result.cost_estimate)
        
        # Calculate derived metrics
        for agent_name, stats in agent_stats.items():
            stats["success_rate"] = stats["successful_executions"] / max(stats["total_executions"], 1)
            stats["detection_rate"] = stats["detections"] / max(stats["successful_executions"], 1)
            stats["ranking_rate"] = stats["rankings"] / max(stats["detections"], 1)
            stats["average_execution_time"] = sum(stats["execution_times"]) / len(stats["execution_times"]) if stats["execution_times"] else 0
            stats["average_confidence"] = sum(stats["confidences"]) / len(stats["confidences"]) if stats["confidences"] else 0
            stats["total_cost"] = sum(stats["costs"]) if stats["costs"] else 0
            stats["average_cost"] = sum(stats["costs"]) / len(stats["costs"]) if stats["costs"] else 0
        
        return agent_stats
    
    def _analyze_trends(self, workflow_state: WorkflowState) -> Dict[str, Any]:
        """Analyze trends in the data (placeholder for future implementation)."""
        # This would typically analyze historical data
        # For now, return basic trend indicators
        return {
            "trend_analysis_available": False,
            "note": "Trend analysis requires historical data comparison"
        }
    
    def _calculate_performance_efficiency(self, execution_times: List[float]) -> float:
        """Calculate performance efficiency score."""
        if not execution_times:
            return 0.0
        
        # Efficiency based on consistency and speed
        avg_time = sum(execution_times) / len(execution_times)
        variance = sum((t - avg_time) ** 2 for t in execution_times) / len(execution_times)
        
        # Lower variance and lower average time = higher efficiency
        consistency_score = 1.0 / (1.0 + variance)
        speed_score = 1.0 / (1.0 + avg_time / 30.0)  # Normalize to 30 seconds
        
        return (consistency_score + speed_score) / 2.0
    
    def _calculate_confidence_distribution(self, confidences: List[float]) -> Dict[str, int]:
        """Calculate distribution of confidence scores."""
        if not confidences:
            return {}
        
        distribution = {
            "high": len([c for c in confidences if c >= 0.8]),
            "medium": len([c for c in confidences if 0.6 <= c < 0.8]),
            "low": len([c for c in confidences if c < 0.6])
        }
        
        return distribution
    
    def _calculate_overall_quality_score(self, avg_confidence: float, avg_ranking: Optional[float], avg_context_quality: float) -> float:
        """Calculate overall quality score."""
        quality_score = avg_confidence * 0.4  # 40% weight to confidence
        
        # Ranking bonus (better ranking = higher score)
        if avg_ranking:
            ranking_score = max(0, 1.0 - (avg_ranking - 1) / 20.0)  # Scale 1-20 to 0-1
            quality_score += ranking_score * 0.3  # 30% weight to ranking
        else:
            quality_score += 0.0
        
        # Context quality
        quality_score += avg_context_quality * 0.3  # 30% weight to context
        
        return min(1.0, quality_score)
    
    def _calculate_cost_efficiency(self, costs: List[float], workflow_state: WorkflowState) -> float:
        """Calculate cost efficiency score."""
        if not costs:
            return 0.0
        
        total_cost = sum(costs)
        total_results = len(costs)
        
        # Efficiency = results per dollar spent
        efficiency = total_results / max(total_cost, 0.01)
        
        # Normalize to 0-1 scale (assuming $1 per result is baseline)
        return min(1.0, efficiency)
    
    def _generate_recommendations(self, basic_metrics: Dict, performance_metrics: Dict, 
                                quality_metrics: Dict, cost_metrics: Dict) -> List[str]:
        """Generate actionable recommendations based on analytics."""
        recommendations = []
        
        # Detection rate recommendations
        if basic_metrics.get("detection_rate", 0) < 0.5:
            recommendations.append("Consider expanding brand variations or adjusting detection sensitivity")
        
        # Performance recommendations
        if performance_metrics.get("average_execution_time", 0) > 30:
            recommendations.append("Consider optimizing agent configurations or using faster models")
        
        # Quality recommendations
        if quality_metrics.get("average_confidence", 0) < 0.6:
            recommendations.append("Review agent prompts and consider using more specific queries")
        
        # Cost recommendations
        if cost_metrics.get("enabled", False) and cost_metrics.get("total_cost", 0) > 1.0:
            recommendations.append("Monitor costs and consider using more cost-effective models for routine queries")
        
        # Agent recommendations
        if basic_metrics.get("agent_success_rate", 0) < 0.8:
            recommendations.append("Review agent configurations and check API key validity")
        
        if not recommendations:
            recommendations.append("System is performing well. Continue monitoring for trends.")
        
        return recommendations

# Utility function for generating comprehensive reports
async def generate_comprehensive_report(workflow_state: WorkflowState) -> Dict[str, Any]:
    """
    Generate a comprehensive analytics report for a workflow state.
    
    Args:
        workflow_state: The workflow state to analyze
        
    Returns:
        Comprehensive analytics report
    """
    analytics_engine = BrandMonitoringAnalytics()
    return await analytics_engine.analyze_workflow_results(workflow_state)
