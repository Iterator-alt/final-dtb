"""
Enhanced Google Sheets Integration - Stage 2

This module provides comprehensive Google Sheets integration for storing
brand monitoring results with ranking detection, cost tracking, and enhanced analytics.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
import gspread
from gspread.exceptions import APIError, SpreadsheetNotFound, WorksheetNotFound
from google.oauth2.service_account import Credentials

from src.workflow.state import WorkflowState, QueryState, AgentResult
from src.config.settings import GoogleSheetsConfig, get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

class EnhancedGoogleSheetsManager:
    """
    Enhanced manager class for Google Sheets operations with Stage 2 features.
    
    Handles authentication, sheet operations, and data formatting for brand monitoring results
    with ranking detection, cost tracking, and advanced analytics.
    """
    
    def __init__(self, config: GoogleSheetsConfig = None):
        """Initialize the enhanced Google Sheets manager."""
        self.config = config or get_settings().google_sheets
        self.settings = get_settings()
        self._client = None
        self._spreadsheet = None
        self._worksheet = None
        
        # Enhanced column definitions for Stage 2
        self.base_columns = [
            "Query",
            "Model_Name", 
            "Found_Y/N",
            "Timestamp",
            "Confidence",
            "Execution_Time",
            "Error_Message"
        ]
        
        # Stage 2 columns - ranking and analytics
        self.ranking_columns = [
            "Ranking_Position",
            "Ranking_Context",
            "Ranking_Confidence"
        ]
        
        # Stage 2 columns - cost and performance
        self.analytics_columns = [
            "Token_Usage_Input",
            "Token_Usage_Output", 
            "Token_Usage_Total",
            "Cost_Estimate",
            "Retry_Count",
            "Response_Length"
        ]
        
        # Stage 2 columns - context and quality
        self.context_columns = [
            "Brand_Matches",
            "Context_Quality",
            "Agent_Agreement",
            "Query_Category"
        ]
        
        # Stage 2 columns - competitive analysis
        self.competitive_columns = [
            "Competitors_Mentioned",
            "Market_Position",
            "Sentiment_Score"
        ]
    
    async def initialize(self) -> bool:
        """
        Initialize the Google Sheets connection and setup with Stage 2 enhancements.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Setup authentication
            if not await self._authenticate():
                return False
            
            # Open spreadsheet
            if not await self._open_spreadsheet():
                return False
            
            # Setup worksheet with Stage 2 columns
            if not await self._setup_enhanced_worksheet():
                return False
            
            logger.info("Enhanced Google Sheets manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize enhanced Google Sheets manager: {str(e)}")
            return False
    
    async def _authenticate(self) -> bool:
        """Authenticate with Google Sheets API."""
        try:
            # Use the simpler gspread service account method
            loop = asyncio.get_event_loop()
            self._client = await loop.run_in_executor(
                None, 
                gspread.service_account, 
                self.config.credentials_file
            )
            
            logger.debug("Google Sheets authentication successful")
            return True
            
        except FileNotFoundError:
            logger.error(f"Credentials file not found: {self.config.credentials_file}")
            return False
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return False
    
    async def _open_spreadsheet(self) -> bool:
        """Open the target spreadsheet."""
        try:
            loop = asyncio.get_event_loop()
            self._spreadsheet = await loop.run_in_executor(
                None,
                self._client.open_by_key,
                self.config.spreadsheet_id
            )
            
            logger.debug(f"Opened spreadsheet: {self._spreadsheet.title}")
            return True
            
        except SpreadsheetNotFound:
            logger.error(f"Spreadsheet not found: {self.config.spreadsheet_id}")
            return False
        except Exception as e:
            logger.error(f"Failed to open spreadsheet: {str(e)}")
            return False
    
    async def _setup_enhanced_worksheet(self) -> bool:
        """Setup or create the target worksheet with Stage 2 columns."""
        try:
            loop = asyncio.get_event_loop()
            
            logger.info(f"Setting up enhanced worksheet: {self.config.worksheet_name}")
            
            # Try to open existing worksheet
            try:
                logger.info("Attempting to open existing worksheet...")
                self._worksheet = await loop.run_in_executor(
                    None,
                    self._spreadsheet.worksheet,
                    self.config.worksheet_name
                )
                logger.info(f"Successfully opened existing worksheet: {self.config.worksheet_name}")
                
            except WorksheetNotFound:
                # Create new worksheet with appropriate column count
                logger.info("Worksheet not found, creating new worksheet...")
                total_columns = len(self._get_all_columns())
                
                self._worksheet = await loop.run_in_executor(
                    None,
                    self._spreadsheet.add_worksheet,
                    self.config.worksheet_name,
                    1000,  # rows
                    total_columns  # columns
                )
                logger.info(f"Successfully created new worksheet: {self.config.worksheet_name}")
            
            # Setup enhanced headers
            logger.info("Setting up enhanced headers...")
            await self._setup_enhanced_headers()
            logger.info("Enhanced headers setup completed")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup enhanced worksheet: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return False
    
    def _get_all_columns(self) -> List[str]:
        """Get all column headers based on enabled Stage 2 features."""
        columns = self.base_columns.copy()
        
        # Add Stage 2 columns based on configuration
        if self.settings.stage2.enable_ranking_detection:
            columns.extend(self.ranking_columns)
        
        if self.settings.stage2.enable_cost_tracking:
            columns.extend(self.analytics_columns)
        
        if self.settings.stage2.enable_analytics:
            columns.extend(self.context_columns)
            columns.extend(self.competitive_columns)
        
        return columns
    
    async def _setup_enhanced_headers(self):
        """Setup enhanced column headers in the worksheet."""
        try:
            loop = asyncio.get_event_loop()
            
            # Check if headers already exist
            existing_headers = await loop.run_in_executor(
                None,
                lambda: self._worksheet.row_values(1)
            )
            
            current_columns = self._get_all_columns()
            
            if not existing_headers or existing_headers != current_columns:
                # Update headers
                await loop.run_in_executor(
                    None,
                    lambda: self._worksheet.update('A1', [current_columns])
                )
                
                # Format headers (bold)
                header_range = f'A1:{chr(65 + len(current_columns) - 1)}1'
                await loop.run_in_executor(
                    None,
                    lambda: self._worksheet.format(header_range, {'textFormat': {'bold': True}})
                )
                
                logger.debug(f"Enhanced headers setup completed with {len(current_columns)} columns")
            
        except Exception as e:
            logger.error(f"Failed to setup enhanced headers: {str(e)}")
            raise
    
    async def store_enhanced_results(self, workflow_state: WorkflowState) -> bool:
        """
        Store enhanced workflow results to Google Sheets with Stage 2 data.
        
        Args:
            workflow_state: Complete workflow state with results
            
        Returns:
            True if storage successful, False otherwise
        """
        try:
            if not self._worksheet:
                logger.error("Worksheet not initialized")
                return False
            
            # Prepare enhanced data rows
            rows_to_add = []
            
            for query, query_state in workflow_state.query_states.items():
                for agent_name, agent_result in query_state.agent_results.items():
                    row = self._format_enhanced_result_row(query, agent_result, query_state)
                    rows_to_add.append(row)
            
            if not rows_to_add:
                logger.warning("No results to store")
                return True
            
            # Add rows to sheet with batch processing
            await self._append_enhanced_rows(rows_to_add)
            
            logger.info(f"Stored {len(rows_to_add)} enhanced result rows to Google Sheets")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store enhanced results: {str(e)}")
            return False
    
    def _format_enhanced_result_row(
        self, 
        query: str, 
        agent_result: AgentResult,
        query_state: QueryState
    ) -> List[str]:
        """Format a single result into an enhanced spreadsheet row with Stage 2 data."""
        # Base columns (Stage 1)
        row = [
            query,
            agent_result.model_name,
            "Y" if agent_result.brand_detection and agent_result.brand_detection.found else "N",
            agent_result.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            f"{agent_result.brand_detection.confidence:.3f}" if agent_result.brand_detection else "0.000",
            f"{agent_result.execution_time:.3f}" if agent_result.execution_time else "",
            agent_result.error_message or ""
        ]
        
        # Stage 2 ranking columns
        if self.settings.stage2.enable_ranking_detection:
            ranking_pos = ""
            ranking_context = ""
            ranking_confidence = ""
            
            if agent_result.brand_detection:
                ranking_pos = str(agent_result.brand_detection.ranking_position or "")
                ranking_context = (agent_result.brand_detection.ranking_context or "")[:500]  # Limit length
                
                # Calculate ranking confidence (if position found)
                if agent_result.brand_detection.ranking_position:
                    ranking_confidence = f"{min(agent_result.brand_detection.confidence * 1.2, 1.0):.3f}"
            
            row.extend([ranking_pos, ranking_context, ranking_confidence])
        
        # Stage 2 analytics columns
        if self.settings.stage2.enable_cost_tracking:
            token_input = ""
            token_output = ""
            token_total = ""
            cost_estimate = ""
            
            if agent_result.token_usage:
                token_input = str(agent_result.token_usage.get('prompt_tokens', ''))
                token_output = str(agent_result.token_usage.get('completion_tokens', ''))
                token_total = str(agent_result.token_usage.get('total_tokens', ''))
            
            if agent_result.cost_estimate:
                cost_estimate = f"{agent_result.cost_estimate:.6f}"
            
            response_length = str(len(agent_result.raw_response)) if agent_result.raw_response else ""
            
            row.extend([
                token_input,
                token_output,
                token_total,
                cost_estimate,
                str(agent_result.retry_count),
                response_length
            ])
        
        # Stage 2 context and quality columns
        if self.settings.stage2.enable_analytics:
            brand_matches = ""
            context_quality = ""
            agent_agreement = ""
            query_category = ""
            
            if agent_result.brand_detection:
                brand_matches = ", ".join(agent_result.brand_detection.matches[:3])  # First 3 matches
                context_quality = f"{agent_result.brand_detection.confidence:.2f}"
            
            # Calculate agent agreement for this query
            agent_agreement = f"{self._calculate_agent_agreement(query_state):.2f}"
            
            # Categorize query
            query_category = self._categorize_query(query)
            
            row.extend([brand_matches, context_quality, agent_agreement, query_category])
            
            # Competitive analysis columns
            competitors_mentioned = self._extract_competitors_from_response(agent_result.raw_response or "")
            market_position = self._determine_market_position(agent_result, query_state)
            sentiment_score = self._calculate_sentiment_score(agent_result.brand_detection)
            
            row.extend([
                ", ".join(competitors_mentioned[:5]),  # Top 5 competitors
                market_position,
                f"{sentiment_score:.2f}"
            ])
        
        return row
    
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
        
        # Perfect agreement = 1.0, complete disagreement = 0.0
        if positive_count == 0 or positive_count == total_count:
            return 1.0
        else:
            return 1.0 - (abs(positive_count - total_count/2) / (total_count/2))
    
    def _categorize_query(self, query: str) -> str:
        """Categorize the query based on content."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["comparison", "vs", "versus", "compare"]):
            return "Comparison"
        elif any(word in query_lower for word in ["best", "top", "leading", "ranking"]):
            return "Ranking"
        elif any(word in query_lower for word in ["tools", "software", "platform"]):
            return "Tools/Software"
        elif any(word in query_lower for word in ["company", "companies", "vendor"]):
            return "Companies"
        elif any(word in query_lower for word in ["analytics", "business intelligence", "bi"]):
            return "Analytics/BI"
        else:
            return "General"
    
    def _extract_competitors_from_response(self, response: str) -> List[str]:
        """Extract competitor mentions from agent response."""
        if not response:
            return []
        
        common_competitors = [
            "tableau", "power bi", "qlik", "looker", "sisense", "domo", 
            "alteryx", "snowflake", "databricks", "palantir", "sas",
            "microsoft", "google", "amazon", "oracle", "ibm", "salesforce"
        ]
        
        response_lower = response.lower()
        found_competitors = []
        
        for competitor in common_competitors:
            if competitor in response_lower:
                found_competitors.append(competitor.title())
        
        return found_competitors
    
    def _determine_market_position(self, agent_result: AgentResult, query_state: QueryState) -> str:
        """Determine market position based on ranking and context."""
        if not agent_result.brand_detection or not agent_result.brand_detection.found:
            return "Not Mentioned"
        
        ranking = agent_result.brand_detection.ranking_position
        if not ranking:
            ranking = query_state.best_ranking
        
        if not ranking:
            return "Mentioned"
        elif ranking == 1:
            return "Leader"
        elif ranking <= 3:
            return "Top Player"
        elif ranking <= 5:
            return "Contender"
        elif ranking <= 10:
            return "Recognized"
        else:
            return "Niche"
    
    def _calculate_sentiment_score(self, brand_detection) -> float:
        """Calculate sentiment score based on context."""
        if not brand_detection or not brand_detection.context:
            return 0.5  # Neutral
        
        context_lower = brand_detection.context.lower()
        
        positive_words = [
            "excellent", "outstanding", "best", "top", "leading", "innovative",
            "powerful", "comprehensive", "reliable", "trusted", "proven"
        ]
        
        negative_words = [
            "poor", "bad", "disappointing", "limited", "lacking", "outdated",
            "problematic", "difficult", "complex", "expensive"
        ]
        
        positive_count = sum(1 for word in positive_words if word in context_lower)
        negative_count = sum(1 for word in negative_words if word in context_lower)
        
        # Base sentiment is neutral (0.5)
        # Positive words increase sentiment, negative words decrease it
        sentiment = 0.5 + (positive_count * 0.1) - (negative_count * 0.1)
        
        return max(0.0, min(1.0, sentiment))  # Clamp between 0 and 1
    
    async def _append_enhanced_rows(self, rows: List[List[str]], batch_size: int = 50):
        """
        Append multiple enhanced rows to the worksheet with optimized batching.
        
        Args:
            rows: List of rows to append
            batch_size: Number of rows to process per batch
        """
        loop = asyncio.get_event_loop()
        
        # Process in smaller batches for Stage 2 (more columns = larger payload)
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            
            try:
                await loop.run_in_executor(
                    None,
                    lambda: self._worksheet.append_rows(batch)
                )
                
                logger.debug(f"Appended enhanced batch of {len(batch)} rows")
                
                # Slightly longer delay for Stage 2 to respect API limits
                await asyncio.sleep(0.2)
                
            except APIError as e:
                if "quota" in str(e).lower():
                    logger.warning("Google Sheets API quota exceeded, waiting...")
                    await asyncio.sleep(60)  # Wait 1 minute
                    # Retry the batch
                    await loop.run_in_executor(
                        None,
                        lambda: self._worksheet.append_rows(batch)
                    )
                else:
                    raise
    
    async def store_single_enhanced_result(
        self, 
        query: str, 
        agent_result: AgentResult,
        query_state: QueryState = None
    ) -> bool:
        """
        Store a single enhanced agent result.
        
        Args:
            query: The search query
            agent_result: Result from an agent
            query_state: Optional query state for additional context
            
        Returns:
            True if storage successful, False otherwise
        """
        try:
            if not self._worksheet:
                logger.error("Worksheet not initialized")
                return False
            
            logger.info(f"Attempting to store enhanced result for query: {query}")
            
            # Create a minimal query state if not provided
            if query_state is None:
                query_state = QueryState(query=query)
                query_state.agent_results[agent_result.agent_name] = agent_result
            
            row = self._format_enhanced_result_row(query, agent_result, query_state)
            logger.debug(f"Formatted enhanced row with {len(row)} columns")
            
            loop = asyncio.get_event_loop()
            
            # Try to append the row
            logger.info("Appending enhanced row to Google Sheets...")
            await loop.run_in_executor(
                None,
                lambda: self._worksheet.append_row(row)
            )
            
            logger.info(f"Successfully stored enhanced result for query: {query}, agent: {agent_result.agent_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store enhanced single result: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return False
    
    async def get_enhanced_historical_data(
        self, 
        days_back: int = 30,
        query_filter: Optional[str] = None,
        include_ranking_data: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieve enhanced historical data from the sheet.
        
        Args:
            days_back: Number of days to look back
            query_filter: Optional filter for specific queries
            include_ranking_data: Whether to include ranking analysis
            
        Returns:
            List of enhanced historical records
        """
        try:
            if not self._worksheet:
                logger.error("Worksheet not initialized")
                return []
            
            loop = asyncio.get_event_loop()
            
            # Get all records
            records = await loop.run_in_executor(
                None,
                self._worksheet.get_all_records
            )
            
            # Filter by date if specified
            if days_back > 0:
                cutoff_date = datetime.now() - timedelta(days=days_back)
                
                filtered_records = []
                for record in records:
                    try:
                        record_date = datetime.strptime(record.get('Timestamp', ''), "%Y-%m-%d %H:%M:%S")
                        if record_date >= cutoff_date:
                            filtered_records.append(record)
                    except ValueError:
                        continue  # Skip records with invalid timestamps
                
                records = filtered_records
            
            # Filter by query if specified
            if query_filter:
                records = [r for r in records if query_filter.lower() in r.get('Query', '').lower()]
            
            # Enhance records with calculated fields if ranking data is included
            if include_ranking_data:
                records = self._enhance_historical_records(records)
            
            logger.debug(f"Retrieved {len(records)} enhanced historical records")
            return records
            
        except Exception as e:
            logger.error(f"Failed to retrieve enhanced historical data: {str(e)}")
            return []
    
    def _enhance_historical_records(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance historical records with calculated metrics."""
        for record in records:
            # Add calculated fields
            record['has_ranking'] = bool(record.get('Ranking_Position', '').strip())
            record['is_top_10'] = False
            record['is_top_5'] = False
            record['is_top_3'] = False
            
            if record['has_ranking']:
                try:
                    position = int(record['Ranking_Position'])
                    record['is_top_10'] = position <= 10
                    record['is_top_5'] = position <= 5
                    record['is_top_3'] = position <= 3
                except (ValueError, TypeError):
                    pass
            
            # Enhance confidence categories
            try:
                confidence = float(record.get('Confidence', 0))
                if confidence >= 0.8:
                    record['confidence_category'] = 'High'
                elif confidence >= 0.6:
                    record['confidence_category'] = 'Medium'
                elif confidence >= 0.4:
                    record['confidence_category'] = 'Low'
                else:
                    record['confidence_category'] = 'Very Low'
            except (ValueError, TypeError):
                record['confidence_category'] = 'Unknown'
        
        return records
    
    async def get_enhanced_summary_stats(self) -> Dict[str, Any]:
        """Get enhanced summary statistics from stored data."""
        try:
            records = await self.get_enhanced_historical_data(days_back=0)  # All data
            
            if not records:
                return {}
            
            total_queries = len(set(r.get('Query', '') for r in records))
            total_results = len(records)
            brand_mentions = len([r for r in records if r.get('Found_Y/N') == 'Y'])
            
            # Stage 2 enhanced statistics
            ranking_mentions = len([r for r in records if r.get('Ranking_Position', '').strip()])
            top_10_mentions = len([r for r in records if r.get('is_top_10', False)])
            top_5_mentions = len([r for r in records if r.get('is_top_5', False)])
            top_3_mentions = len([r for r in records if r.get('is_top_3', False)])
            
            models = list(set(r.get('Model_Name', '') for r in records))
            
            # Cost analysis
            total_cost = 0
            cost_records = [r for r in records if r.get('Cost_Estimate', '').strip()]
            for record in cost_records:
                try:
                    total_cost += float(record['Cost_Estimate'])
                except (ValueError, TypeError):
                    pass
            
            # Performance analysis
            execution_times = []
            for record in records:
                try:
                    exec_time = float(record.get('Execution_Time', ''))
                    execution_times.append(exec_time)
                except (ValueError, TypeError):
                    pass
            
            avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
            
            return {
                'total_unique_queries': total_queries,
                'total_results': total_results,
                'brand_mentions_found': brand_mentions,
                'detection_rate': brand_mentions / total_results if total_results > 0 else 0,
                'ranking_mentions_found': ranking_mentions,
                'ranking_detection_rate': ranking_mentions / brand_mentions if brand_mentions > 0 else 0,
                'top_10_rate': top_10_mentions / brand_mentions if brand_mentions > 0 else 0,
                'top_5_rate': top_5_mentions / brand_mentions if brand_mentions > 0 else 0,
                'top_3_rate': top_3_mentions / brand_mentions if brand_mentions > 0 else 0,
                'models_used': models,
                'total_cost_estimate': total_cost,
                'average_execution_time': avg_execution_time,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get enhanced summary stats: {str(e)}")
            return {}
    
    async def cleanup(self):
        """Cleanup resources."""
        # Google Sheets client doesn't require explicit cleanup
        self._client = None
        self._spreadsheet = None
        self._worksheet = None
        logger.debug("Enhanced Google Sheets manager cleaned up")

# Backward compatibility - replace the original class
GoogleSheetsManager = EnhancedGoogleSheetsManager

# Utility functions
async def create_enhanced_sheets_manager(config: GoogleSheetsConfig = None) -> EnhancedGoogleSheetsManager:
    """Create and initialize an enhanced Google Sheets manager."""
    manager = EnhancedGoogleSheetsManager(config)
    success = await manager.initialize()
    
    if not success:
        raise Exception("Failed to initialize enhanced Google Sheets manager")
    
    return manager

async def store_enhanced_workflow_results(workflow_state: WorkflowState, config: GoogleSheetsConfig = None) -> bool:
    """Utility function to store enhanced workflow results."""
    manager = EnhancedGoogleSheetsManager(config)
    
    try:
        if not await manager.initialize():
            return False
        
        return await manager.store_enhanced_results(workflow_state)
        
    finally:
        await manager.cleanup()