"""
Enhanced LangGraph Workflow Implementation - Stage 2

This module implements the enhanced LangGraph workflow for orchestrating
multi-agent brand monitoring with 3 LLMs, ranking detection, and advanced analytics.
"""

import asyncio
import uuid
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import os

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from src.workflow.state import (
    WorkflowState, QueryState, AgentResult, AgentStatus,
    state_to_dict, dict_to_state, update_agent_result, finalize_query_state
)
from src.agents.base_agent import BaseAgent, AgentFactory
from src.agents.openai_agent import create_openai_agent
from src.agents.perplexity_agent import create_perplexity_agent
from src.agents.gemini_agent import create_gemini_agent
from src.agents.web_search_agent import create_web_search_agent
from src.storage.google_sheets import EnhancedGoogleSheetsManager
from src.analytics.analytics_engine import BrandMonitoringAnalytics, generate_comprehensive_report
from src.config.settings import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

class EnhancedBrandMonitoringWorkflow:
    """
    Enhanced LangGraph-based workflow for multi-agent brand monitoring with Stage 2 features.
    
    This class implements a sophisticated workflow that orchestrates multiple
    LLM agents (OpenAI, Perplexity, Gemini) to search for brand mentions with 
    ranking detection, cost tracking, and advanced analytics.
    """
    
    def __init__(self, config=None):
        """Initialize the enhanced workflow with configuration."""
        self.config = config or get_settings()
        self.agents: Dict[str, BaseAgent] = {}
        self.storage_manager: Optional[EnhancedGoogleSheetsManager] = None
        self.analytics_engine: Optional[BrandMonitoringAnalytics] = None
        self.graph = None
        
        # Enhanced workflow execution tracking
        self.execution_history: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, Any] = {}
        
        logger.info("Initializing Enhanced BrandMonitoringWorkflow (Stage 2)")
    
    async def initialize(self) -> bool:
        """
        Initialize the enhanced workflow components.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Initialize agents
            agent_factories = {
                "openai": create_openai_agent,
                "perplexity": create_perplexity_agent,
                "gemini": create_gemini_agent,
                "web_search": create_web_search_agent
            }
            
            # Initialize enhanced agents
            await self._initialize_enhanced_agents(agent_factories)
            
            # Initialize enhanced storage
            await self._initialize_enhanced_storage()
            
            # Initialize analytics engine
            self._initialize_analytics_engine()
            
            # Build the enhanced LangGraph
            self._build_enhanced_graph()
            
            logger.info("Enhanced workflow initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Enhanced workflow initialization failed: {str(e)}")
            return False
    
    async def _initialize_enhanced_agents(self, agent_factories: Dict[str, Callable]) -> bool:
        """Initialize all configured agents including Gemini for Stage 2."""
        logger.info("Initializing enhanced agents (Stage 2)...")
        
        success_count = 0
        total_agents = 0
        
        for agent_name, factory_func in agent_factories.items():
            if agent_name not in self.config.llm_configs:
                continue
                
            total_agents += 1
            try:
                agent_config = self.config.llm_configs[agent_name]
                # Convert LLMConfig to dictionary if needed
                if hasattr(agent_config, 'model_dump'):
                    agent_config_dict = agent_config.model_dump()
                elif isinstance(agent_config, dict):
                    agent_config_dict = agent_config
                else:
                    agent_config_dict = agent_config.__dict__ if hasattr(agent_config, '__dict__') else {}
                
                agent = factory_func(agent_name, agent_config_dict)
                
                # Test health check for agents that support it
                if hasattr(agent, 'test_connection'):
                    if await agent.test_connection():
                        self.agents[agent_name] = agent
                        success_count += 1
                        logger.info(f"Agent '{agent_name}' initialized successfully")
                    else:
                        logger.error(f"Agent '{agent_name}' failed health check; skipping")
                else:
                    # For agents without health check, add them directly
                    self.agents[agent_name] = agent
                    success_count += 1
                    logger.info(f"Agent '{agent_name}' initialized successfully")
                    
            except Exception as e:
                logger.error(f"Failed to initialize agent '{agent_name}': {str(e)}")
        
        if success_count == 0:
            logger.error("No agents initialized successfully")
            return False
        
        logger.info(f"Initialized {success_count}/{total_agents} agents successfully")
        logger.info(f"Available agents: {list(self.agents.keys())}")
        
        if success_count >= 2:
            logger.info("✅ Multi-agent capability with {} agents".format(success_count))
        else:
            logger.warning("⚠️ Limited capability with only {} agent".format(success_count))
        
        return True
    
    async def _initialize_enhanced_storage(self) -> bool:
        """Initialize enhanced Google Sheets storage manager."""
        try:
            gs_cfg = self.config.google_sheets
            if not gs_cfg.spreadsheet_id or not os.path.exists(gs_cfg.credentials_file):
                logger.warning("Google Sheets not configured or credentials missing; storage disabled")
                self.storage_manager = None
                return True
            
            self.storage_manager = EnhancedGoogleSheetsManager(self.config.google_sheets)
            ok = await self.storage_manager.initialize()
            if not ok:
                logger.warning("Enhanced Google Sheets initialization failed; continuing without storage")
                self.storage_manager = None
            else:
                logger.info("Enhanced Google Sheets storage initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Enhanced storage initialization failed: {str(e)}")
            self.storage_manager = None
            return True
    
    def _initialize_analytics_engine(self):
        """Initialize the analytics engine for Stage 2."""
        try:
            self.analytics_engine = BrandMonitoringAnalytics(self.config)
            logger.info("Analytics engine initialized successfully")
        except Exception as e:
            logger.error(f"Analytics engine initialization failed: {str(e)}")
            self.analytics_engine = None
    
    def _build_enhanced_graph(self):
        """Build the enhanced LangGraph workflow with Stage 2 features."""
        # Create state graph
        workflow = StateGraph(dict)
        
        # Add enhanced nodes
        workflow.add_node("start", self._start_node)
        workflow.add_node("process_query", self._process_query_node)
        workflow.add_node("run_agents_parallel", self._run_agents_parallel_node)
        workflow.add_node("run_agents_sequential", self._run_agents_sequential_node)
        workflow.add_node("aggregate_results", self._enhanced_aggregate_results_node)  # Enhanced
        workflow.add_node("analyze_results", self._analyze_results_node)  # New for Stage 2
        workflow.add_node("store_results", self._enhanced_store_results_node)  # Enhanced
        workflow.add_node("finalize", self._enhanced_finalize_node)  # Enhanced
        workflow.add_node("handle_error", self._handle_error_node)
        
        # Define enhanced edges
        workflow.set_entry_point("start")
        
        workflow.add_edge("start", "process_query")
        
        # Conditional routing based on processing mode
        workflow.add_conditional_edges(
            "process_query",
            self._decide_execution_mode,
            {
                "parallel": "run_agents_parallel",
                "sequential": "run_agents_sequential",
                "error": "handle_error",
                "complete": "finalize"
            }
        )
        
        workflow.add_edge("run_agents_parallel", "aggregate_results")
        workflow.add_edge("run_agents_sequential", "aggregate_results")
        workflow.add_edge("aggregate_results", "analyze_results")  # New Stage 2 step
        workflow.add_edge("analyze_results", "store_results")
        workflow.add_edge("store_results", "process_query")  # Loop back for next query
        workflow.add_edge("handle_error", "process_query")   # Continue on error
        workflow.add_edge("finalize", END)
        
        # Compile the enhanced graph
        checkpointer = MemorySaver()
        self.graph = workflow.compile(checkpointer=checkpointer)
        
        logger.info("Enhanced LangGraph workflow compiled successfully")
    
    # Enhanced node implementations
    async def _start_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize the enhanced workflow state."""
        logger.info("Starting enhanced brand monitoring workflow (Stage 2)")
        
        workflow_state = dict_to_state(state)
        workflow_state.workflow_id = str(uuid.uuid4())
        workflow_state.start_time = datetime.now()
        
        # Prepare query states with enhanced tracking
        for i, query in enumerate(workflow_state.queries):
            query_state = QueryState(
                query=query,
                query_id=f"{workflow_state.workflow_id}_{i}"
            )
            workflow_state.add_query_state(query, query_state)
        
        workflow_state.total_queries = len(workflow_state.queries)
        
        # Log Stage 2 capabilities
        logger.info(f"Initialized enhanced workflow with {workflow_state.total_queries} queries")
        logger.info(f"Available agents: {list(self.agents.keys())}")
        logger.info(f"Stage 2 features enabled: Ranking={self.config.stage2.enable_ranking_detection}, "
                   f"Cost={self.config.stage2.enable_cost_tracking}, Analytics={self.config.stage2.enable_analytics}")
        
        return state_to_dict(workflow_state)
    
    async def _process_query_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process the current query with enhanced logging."""
        workflow_state = dict_to_state(state)
        
        # Check if we're done
        if workflow_state.current_query_index >= len(workflow_state.queries):
            workflow_state.end_time = datetime.now()
            return state_to_dict(workflow_state)
        
        current_query = workflow_state.queries[workflow_state.current_query_index]
        logger.info(f"Processing query {workflow_state.current_query_index + 1}/{len(workflow_state.queries)}: {current_query}")
        
        # Update current step
        query_state = workflow_state.get_query_state(current_query)
        if query_state:
            query_state.current_step = "processing"
            query_state.status = AgentStatus.RUNNING
        
        return state_to_dict(workflow_state)
    
    async def _decide_execution_mode(self, state: Dict[str, Any]) -> str:
        """Enhanced decision logic for execution mode."""
        workflow_state = dict_to_state(state)
        
        # Check if we're done with all queries
        if workflow_state.current_query_index >= len(workflow_state.queries):
            return "complete"
        
        # Check for errors that should halt processing
        if workflow_state.failed_queries_count > len(workflow_state.queries) * 0.5:
            logger.warning("Too many failed queries, entering error handling")
            return "error"
        
        # Enhanced decision logic based on agent count and configuration
        agent_count = len(self.agents)
        
        if agent_count >= 3 and workflow_state.processing_mode == "parallel":
            logger.debug("Using parallel execution with 3+ agents")
            return "parallel"
        elif workflow_state.processing_mode == "parallel":
            logger.debug("Using parallel execution")
            return "parallel"
        else:
            logger.debug("Using sequential execution")
            return "sequential"
    
    async def _run_agents_parallel_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced parallel execution with better error handling."""
        workflow_state = dict_to_state(state)
        current_query = workflow_state.queries[workflow_state.current_query_index]
        
        logger.info(f"Running {len(self.agents)} agents in parallel for query: {current_query}")
        
        # Create tasks for all agents with enhanced error handling
        tasks = []
        for agent_name, agent in self.agents.items():
            task = asyncio.create_task(
                self._run_single_agent_with_retries(agent_name, agent, current_query),
                name=f"agent_{agent_name}"
            )
            tasks.append(task)
        
        # Wait for all agents to complete with timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=self.config.workflow.timeout_per_agent * len(self.agents)
            )
        except asyncio.TimeoutError:
            logger.error("Parallel execution timed out")
            results = [Exception("Execution timed out") for _ in tasks]
        
        # Process results with enhanced error handling
        query_state = workflow_state.get_query_state(current_query)
        successful_agents = 0
        
        for i, (agent_name, result) in enumerate(zip(self.agents.keys(), results)):
            if isinstance(result, Exception):
                # Create error result
                error_result = AgentResult(
                    agent_name=agent_name,
                    model_name=self.agents[agent_name]._get_model_name(),
                    status=AgentStatus.FAILED,
                    error_message=str(result)
                )
                query_state.agent_results[agent_name] = error_result
                logger.error(f"Agent {agent_name} failed: {str(result)}")
            else:
                query_state.agent_results[agent_name] = result
                successful_agents += 1
                logger.info(f"Agent {agent_name} completed successfully")
        
        logger.info(f"Parallel execution completed: {successful_agents}/{len(self.agents)} agents successful")
        
        return state_to_dict(workflow_state)
    
    async def _run_agents_sequential_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced sequential execution with better error handling."""
        workflow_state = dict_to_state(state)
        current_query = workflow_state.queries[workflow_state.current_query_index]
        
        logger.info(f"Running {len(self.agents)} agents sequentially for query: {current_query}")
        
        query_state = workflow_state.get_query_state(current_query)
        successful_agents = 0
        
        # Run agents one by one
        for agent_name, agent in self.agents.items():
            try:
                logger.debug(f"Running agent {agent_name} sequentially for query: {current_query}")
                
                result = await self._run_single_agent_with_retries(agent_name, agent, current_query)
                query_state.agent_results[agent_name] = result
                successful_agents += 1
                logger.info(f"Agent {agent_name} completed successfully")
                
            except Exception as e:
                # Create error result
                error_result = AgentResult(
                    agent_name=agent_name,
                    model_name=agent._get_model_name(),
                    status=AgentStatus.FAILED,
                    error_message=str(e)
                )
                query_state.agent_results[agent_name] = error_result
                logger.error(f"Agent {agent_name} failed: {str(e)}")
        
        logger.info(f"Sequential execution completed: {successful_agents}/{len(self.agents)} agents successful")
        
        return state_to_dict(workflow_state)
    
    async def _run_single_agent_with_retries(self, agent_name: str, agent: BaseAgent, query: str) -> AgentResult:
        """Run a single agent with enhanced retry logic."""
        max_retries = self.config.workflow.max_retries
        
        for attempt in range(max_retries + 1):
            try:
                logger.debug(f"Running agent {agent_name} for query: {query} (attempt {attempt + 1})")
                
                # Execute with ranking detection enabled for Stage 2
                result = await agent.execute(query)
                
                # Validate result
                if result.status == AgentStatus.COMPLETED:
                    logger.debug(f"Agent {agent_name} successful on attempt {attempt + 1}")
                    return result
                else:
                    raise Exception(f"Agent returned non-completed status: {result.status}")
                
            except Exception as e:
                logger.warning(f"Agent {agent_name} attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < max_retries:
                    delay = self.config.workflow.retry_delay * (2 ** attempt)  # Exponential backoff
                    await asyncio.sleep(delay)
                    continue
                else:
                    # Final failure
                    logger.error(f"Agent {agent_name} failed after {max_retries + 1} attempts")
                    raise
    
    async def _enhanced_aggregate_results_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced result aggregation with Stage 2 features."""
        workflow_state = dict_to_state(state)
        current_query = workflow_state.queries[workflow_state.current_query_index]
        
        logger.debug(f"Aggregating enhanced results for query: {current_query}")
        
        query_state = workflow_state.get_query_state(current_query)
        
        # Calculate overall results with enhanced metrics
        successful_agents = [
            result for result in query_state.agent_results.values()
            if result.status == AgentStatus.COMPLETED and result.brand_detection
        ]
        
        if successful_agents:
            # Basic brand detection
            query_state.overall_found = any(
                result.brand_detection.found for result in successful_agents
            )
            
            # Enhanced confidence calculation (weighted by agent performance)
            confidences = []
            weights = []
            
            for result in successful_agents:
                if result.brand_detection:
                    confidences.append(result.brand_detection.confidence)
                    # Weight by inverse of execution time (faster = more weight)
                    weight = 1.0 / max(result.execution_time or 1.0, 0.1)
                    weights.append(weight)
            
            if confidences:
                weighted_confidence = sum(c * w for c, w in zip(confidences, weights)) / sum(weights)
                query_state.consensus_confidence = weighted_confidence
            
            # Enhanced ranking analysis
            if self.config.stage2.enable_ranking_detection:
                rankings = []
                ranking_sources = []
                
                for result in successful_agents:
                    if (result.brand_detection and 
                        result.brand_detection.ranking_position and
                        result.brand_detection.ranking_position <= self.config.stage2.ranking_detection.max_position):
                        rankings.append(result.brand_detection.ranking_position)
                        ranking_sources.append(result.agent_name)
                
                if rankings:
                    query_state.best_ranking = min(rankings)  # Lower is better
                    query_state.ranking_sources = ranking_sources
                    
                    # Calculate ranking confidence
                    ranking_confidences = [
                        result.brand_detection.confidence for result in successful_agents
                        if result.brand_detection and result.brand_detection.ranking_position
                    ]
                    if ranking_confidences:
                        query_state.ranking_confidence = sum(ranking_confidences) / len(ranking_confidences)
        
        # Mark query as completed
        finalize_query_state(workflow_state, current_query)
        
        logger.info(
            f"Enhanced aggregation completed. Brand found: {query_state.overall_found}, "
            f"Confidence: {query_state.consensus_confidence:.3f}, "
            f"Best ranking: {query_state.best_ranking or 'N/A'}"
        )
        
        return state_to_dict(workflow_state)
    
    async def _analyze_results_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """New Stage 2 node for advanced result analysis."""
        workflow_state = dict_to_state(state)
        current_query = workflow_state.queries[workflow_state.current_query_index]
        
        logger.debug(f"Analyzing results for query: {current_query}")
        
        if not self.analytics_engine:
            logger.warning("Analytics engine not available, skipping analysis")
            return state_to_dict(workflow_state)
        
        try:
            # Perform query-level analysis
            query_state = workflow_state.get_query_state(current_query)
            
            # Calculate additional metrics
            query_analysis = {
                "agent_agreement": self._calculate_agent_agreement(query_state),
                "execution_efficiency": self._calculate_execution_efficiency(query_state),
                "cost_per_query": self._calculate_query_cost(query_state),
                "quality_score": self._calculate_quality_score(query_state)
            }
            
            # Store analysis in query state
            if query_state.analysis is None:
                query_state.analysis = {}
            query_state.analysis.update(query_analysis)
            
            logger.debug(f"Query analysis completed: {query_analysis}")
            
        except Exception as e:
            logger.error(f"Analysis failed for query {current_query}: {str(e)}")
        
        return state_to_dict(workflow_state)
    
    def _calculate_agent_agreement(self, query_state: QueryState) -> float:
        """Calculate agreement between agents on brand detection."""
        results = [
            r.brand_detection.found for r in query_state.agent_results.values()
            if r.brand_detection
        ]
        
        if len(results) <= 1:
            return 1.0
        
        positive_count = sum(results)
        total_count = len(results)
        
        if positive_count == 0 or positive_count == total_count:
            return 1.0
        else:
            return 1.0 - (abs(positive_count - total_count/2) / (total_count/2))
    
    def _calculate_execution_efficiency(self, query_state: QueryState) -> float:
        """Calculate execution efficiency based on time and success rate."""
        execution_times = [
            r.execution_time for r in query_state.agent_results.values()
            if r.execution_time and r.status == AgentStatus.COMPLETED
        ]
        
        if not execution_times:
            return 0.0
        
        avg_time = sum(execution_times) / len(execution_times)
        success_rate = len(execution_times) / len(query_state.agent_results)
        
        # Efficiency = success_rate / normalized_time
        normalized_time = min(avg_time / 30.0, 1.0)  # Normalize to 30 seconds
        efficiency = success_rate / max(normalized_time, 0.1)
        
        return min(efficiency, 1.0)
    
    def _calculate_query_cost(self, query_state: QueryState) -> float:
        """Calculate total cost for the query."""
        total_cost = 0.0
        
        for result in query_state.agent_results.values():
            if result.cost_estimate:
                total_cost += result.cost_estimate
        
        return total_cost
    
    def _calculate_quality_score(self, query_state: QueryState) -> float:
        """Calculate overall quality score for the query results."""
        if not query_state.overall_found:
            return 0.0
        
        factors = {
            "confidence": query_state.consensus_confidence,
            "agreement": self._calculate_agent_agreement(query_state),
            "efficiency": self._calculate_execution_efficiency(query_state),
            "ranking_bonus": 0.1 if query_state.best_ranking else 0.0
        }
        
        # Weighted quality score
        weights = {"confidence": 0.4, "agreement": 0.3, "efficiency": 0.2, "ranking_bonus": 0.1}
        quality_score = sum(factors[key] * weights[key] for key in factors)
        
        return min(quality_score, 1.0)
    
    async def _enhanced_store_results_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced storage with Stage 2 data."""
        workflow_state = dict_to_state(state)
        current_query = workflow_state.queries[workflow_state.current_query_index]
        
        logger.debug(f"Storing enhanced results for query: {current_query}")
        
        try:
            if self.storage_manager:
                # Store enhanced results for current query
                query_state = workflow_state.get_query_state(current_query)
                
                for agent_name, agent_result in query_state.agent_results.items():
                    success = await self.storage_manager.store_single_enhanced_result(
                        current_query, agent_result, query_state
                    )
                    if not success:
                        logger.warning(f"Failed to store enhanced result for agent {agent_name}")
                
                logger.info(f"Enhanced results stored for query: {current_query}")
            else:
                logger.warning("Enhanced storage manager not available")
        
        except Exception as e:
            logger.error(f"Failed to store enhanced results: {str(e)}")
            # Continue execution even if storage fails
        
        # Move to next query
        workflow_state.current_query_index += 1
        
        return state_to_dict(workflow_state)
    
    async def _enhanced_finalize_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced finalization with Stage 2 analytics."""
        workflow_state = dict_to_state(state)
        
        logger.info("Finalizing enhanced workflow execution")
        
        # Update final statistics
        workflow_state.update_summary_stats()
        
        # Generate comprehensive analytics if enabled
        if self.config.stage2.enable_analytics and self.analytics_engine:
            try:
                # Check if the function exists before calling it
                if hasattr(self.analytics_engine, 'generate_comprehensive_report'):
                    analytics_report = await self.analytics_engine.generate_comprehensive_report(workflow_state)
                else:
                    analytics_report = await self.analytics_engine.analyze_workflow_results(workflow_state)
                workflow_state.analytics_report = analytics_report
                logger.info("Comprehensive analytics report generated")
            except Exception as e:
                logger.error(f"Failed to generate analytics report: {str(e)}")
        
        # Log enhanced summary
        summary = workflow_state.get_progress_summary()
        logger.info(f"Enhanced workflow completed. Summary: {summary}")
        
        # Enhanced execution record
        execution_record = {
            'workflow_id': workflow_state.workflow_id,
            'start_time': workflow_state.start_time,
            'end_time': workflow_state.end_time,
            'total_queries': workflow_state.total_queries,
            'successful_queries': workflow_state.successful_queries,
            'brand_mentions': workflow_state.total_brand_mentions,
            'agents_used': list(self.agents.keys()),
            'stage2_features': {
                'ranking_detection': self.config.stage2.enable_ranking_detection,
                'cost_tracking': self.config.stage2.enable_cost_tracking,
                'analytics': self.config.stage2.enable_analytics
            }
        }
        self.execution_history.append(execution_record)
        
        return state_to_dict(workflow_state)
    
    async def _handle_error_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced error handling with recovery strategies."""
        workflow_state = dict_to_state(state)
        
        logger.warning("Entering enhanced error handling mode")
        
        # Log current state with enhanced metrics
        progress = workflow_state.get_progress_summary()
        logger.warning(f"Enhanced workflow progress: {progress}")
        
        # Enhanced recovery strategies
        available_agents = [name for name, agent in self.agents.items() if hasattr(agent, 'health_check')]
        
        if available_agents:
            logger.info(f"Recovery possible with agents: {available_agents}")
            # Could implement agent health checks and selective retry here
        
        return state_to_dict(workflow_state)
    
    # Enhanced public interface methods
    async def execute_enhanced_workflow(
        self, 
        queries: List[str], 
        processing_mode: str = "parallel",
        enable_analytics: bool = None
    ) -> WorkflowState:
        """
        Execute the enhanced workflow for a list of queries with Stage 2 features.
        
        Args:
            queries: List of search queries to process
            processing_mode: "parallel" or "sequential" execution
            enable_analytics: Override analytics setting
            
        Returns:
            Final workflow state with all results and analytics
        """
        if not self.graph:
            raise RuntimeError("Enhanced workflow not initialized. Call initialize() first.")
        
        logger.info(f"Starting enhanced workflow execution with {len(queries)} queries in {processing_mode} mode")
        logger.info(f"Available agents: {list(self.agents.keys())}")
        
        # Override analytics if specified
        if enable_analytics is not None:
            original_analytics = self.config.stage2.enable_analytics
            self.config.stage2.enable_analytics = enable_analytics
        
        try:
            # Create enhanced initial state
            initial_state = WorkflowState(
                queries=queries,
                target_agents=list(self.agents.keys()),
                processing_mode=processing_mode,
                config_snapshot=self.config.model_dump() if hasattr(self.config, 'model_dump') else None,
                workflow_id=str(uuid.uuid4()),
                start_time=datetime.now()
            )
            
            # Execute the enhanced graph
            thread_id = str(uuid.uuid4())
            final_state_dict = await self.graph.ainvoke(
                state_to_dict(initial_state),
                config={"configurable": {"thread_id": thread_id}}
            )
            
            final_state = dict_to_state(final_state_dict)
            
            logger.info("Enhanced workflow execution completed successfully")
            
            # Log Stage 2 metrics
            if self.config.stage2.enable_ranking_detection:
                ranking_count = sum(
                    1 for qs in final_state.query_states.values()
                    if qs.best_ranking
                )
                logger.info(f"🎯 Ranking detection: {ranking_count}/{len(queries)} queries had rankings")
            
            return final_state
            
        except Exception as e:
            logger.error(f"Enhanced workflow execution failed: {str(e)}")
            raise
        
        finally:
            # Restore original analytics setting if it was overridden
            if enable_analytics is not None:
                self.config.stage2.enable_analytics = original_analytics
    
    def get_enhanced_performance_stats(self) -> Dict[str, Any]:
        """Get enhanced performance statistics for all agents."""
        stats = {}
        for agent_name, agent in self.agents.items():
            base_stats = agent.get_performance_stats()
            
            # Add Stage 2 enhanced metrics
            base_stats.update({
                'provider': agent.__class__.__name__.replace('Agent', ''),
                'model_info': agent.get_model_info() if hasattr(agent, 'get_model_info') else {},
                'stage2_capable': True
            })
            
            stats[agent_name] = base_stats
        
        return stats
    
    async def get_comprehensive_analytics(self, workflow_state: WorkflowState) -> Dict[str, Any]:
        """Get comprehensive analytics for a workflow state."""
        if not self.analytics_engine:
            return {"error": "Analytics engine not available"}
        
        return await self.analytics_engine.analyze_workflow_results(workflow_state)
    
    async def cleanup(self):
        """Clean up workflow resources."""
        logger.info("🧹 Cleaning up enhanced workflow resources...")
        
        # Clean up agents
        for agent_name, agent in self.agents.items():
            try:
                if hasattr(agent, 'cleanup'):
                    await agent.cleanup()
            except Exception as e:
                logger.warning(f"Failed to cleanup agent {agent_name}: {str(e)}")
        
        # Clean up storage manager
        if self.storage_manager:
            try:
                await self.storage_manager.cleanup()
            except Exception as e:
                logger.warning(f"Failed to cleanup storage manager: {str(e)}")
        
        logger.info("✅ Enhanced workflow cleanup completed")

# Backward compatibility
BrandMonitoringWorkflow = EnhancedBrandMonitoringWorkflow

# Factory function for easy workflow creation
async def create_enhanced_workflow(config=None) -> EnhancedBrandMonitoringWorkflow:
    """
    Create and initialize an enhanced brand monitoring workflow.
    
    Args:
        config: Optional configuration object
        
    Returns:
        Initialized enhanced workflow ready for execution
    """
    workflow = EnhancedBrandMonitoringWorkflow(config)
    
    if not await workflow.initialize():
        raise RuntimeError("Failed to initialize enhanced workflow")
    
    return workflow