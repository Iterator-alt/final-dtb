"""
Enhanced Configuration Management for DataTobiz Brand Monitoring System - Stage 2

This module handles all configuration settings, API keys, and environment variables
with proper security practices and validation. Enhanced for Stage 2 with support
for Google Gemini and advanced ranking detection features.
"""

import os
import yaml
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMConfig(BaseModel):
    """Configuration for individual LLM providers."""
    
    name: str
    api_key: str
    model: Optional[str] = None
    max_tokens: int = 1000
    temperature: float = 0.1
    timeout: int = 30

class GoogleSheetsConfig(BaseModel):
    """Configuration for Google Sheets integration."""
    
    credentials_file: str = Field(default="credentials.json")
    spreadsheet_id: str = ""
    worksheet_name: str = "Brand_Monitoring"
    auto_setup_headers: bool = True
    batch_size: int = 100
    enable_validation: bool = True

class BrandConfig(BaseModel):
    """Configuration for brand detection settings."""
    
    target_brand: str = "DataTobiz"
    brand_variations: List[str] = [
        "DataTobiz", "Data Tobiz", "data tobiz", "DATATOBIZ", 
        "DataToBiz", "Data-Tobiz", "datatobiz.com"
    ]
    case_sensitive: bool = False
    partial_match: bool = True
    
    @field_validator('brand_variations')
    @classmethod
    def validate_variations(cls, v, info):
        if info.data.get('target_brand') and info.data['target_brand'] not in v:
            v.append(info.data['target_brand'])
        return v

class WorkflowConfig(BaseModel):
    """Configuration for workflow execution."""
    
    max_retries: int = 3
    retry_delay: float = 1.0
    parallel_execution: bool = True
    timeout_per_agent: int = 60
    log_level: str = "INFO"

class RankingDetectionConfig(BaseModel):
    """Configuration for ranking detection (Stage 2)."""
    
    max_position: int = 20
    min_confidence: float = 0.6
    enable_ordinal_detection: bool = True
    enable_list_detection: bool = True
    enable_keyword_detection: bool = True
    enable_numeric_detection: bool = True

class ContextAnalysisConfig(BaseModel):
    """Configuration for context analysis."""
    
    context_window: int = 200
    enable_sentiment_analysis: bool = False
    positive_keywords: List[str] = [
        "excellent", "outstanding", "innovative", "reliable", "powerful",
        "comprehensive", "award-winning", "recognized", "trusted", "proven"
    ]
    negative_keywords: List[str] = [
        "poor", "disappointing", "limited", "lacking", "outdated", "problematic"
    ]

class StructureDetectionConfig(BaseModel):
    """Configuration for structure detection."""
    
    detect_in_lists: bool = True
    detect_near_headings: bool = True
    detect_comparisons: bool = True

class EnhancedBrandConfig(BaseModel):
    """Enhanced brand detection configuration for Stage 2."""
    
    context_analysis: ContextAnalysisConfig = Field(default_factory=ContextAnalysisConfig)
    structure_detection: StructureDetectionConfig = Field(default_factory=StructureDetectionConfig)

class AgentExecutionConfig(BaseModel):
    """Configuration for agent execution."""
    
    default_mode: str = "parallel"
    enable_health_checks: bool = True
    health_check_timeout: int = 10
    enable_performance_monitoring: bool = True

class RetryStrategiesConfig(BaseModel):
    """Configuration for retry strategies."""
    
    backoff_multiplier: float = 2.0
    max_retry_delay: int = 30
    per_agent_strategies: bool = True

class AgentsConfig(BaseModel):
    """Configuration for agents (Stage 2)."""
    
    execution: AgentExecutionConfig = Field(default_factory=AgentExecutionConfig)
    retry_strategies: RetryStrategiesConfig = Field(default_factory=RetryStrategiesConfig)

class ExportConfig(BaseModel):
    """Configuration for data export."""
    
    enable_auto_export: bool = False
    formats: List[str] = ["json", "csv"]
    frequency: str = "weekly"
    export_path: str = "data/exports/"

class StorageConfig(BaseModel):
    """Enhanced storage configuration."""
    
    google_sheets: GoogleSheetsConfig = Field(default_factory=GoogleSheetsConfig)
    export: ExportConfig = Field(default_factory=ExportConfig)

class NotificationsConfig(BaseModel):
    """Configuration for notifications (Stage 2 preparation)."""
    
    enabled: bool = False
    email_enabled: bool = False
    slack_enabled: bool = False
    webhook_enabled: bool = False

class AnalyticsConfig(BaseModel):
    """Configuration for analytics (Stage 2)."""
    
    enabled: bool = True
    metrics: List[str] = [
        "detection_rate", "ranking_positions", "confidence_scores",
        "execution_times", "cost_tracking", "agent_performance"
    ]
    daily_reports: bool = False
    weekly_summaries: bool = True
    trend_analysis: bool = True
    retention_days: int = 365

class SecurityConfig(BaseModel):
    """Configuration for security."""
    
    validate_api_keys: bool = True
    enable_rate_limiting: bool = True
    rate_limits: Dict[str, int] = {
        "openai": 50,
        "perplexity": 20,
        "gemini": 60
    }
    log_requests: bool = False
    mask_api_keys: bool = True

class Stage2Config(BaseModel):
    """Stage 2 specific configuration."""
    
    enable_ranking_detection: bool = True
    enable_cost_tracking: bool = True
    enable_analytics: bool = True
    ranking_detection: RankingDetectionConfig = Field(default_factory=RankingDetectionConfig)

class Settings(BaseSettings):
    """Main settings class that aggregates all configurations - Enhanced for Stage 2."""
    
    # API Keys - loaded from environment variables
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    perplexity_api_key: str = Field(default="", env="PERPLEXITY_API_KEY")
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")  # New for Stage 2
    
    # Configuration sections
    google_sheets: GoogleSheetsConfig = Field(default_factory=GoogleSheetsConfig)
    brand: BrandConfig = Field(default_factory=BrandConfig)
    workflow: WorkflowConfig = Field(default_factory=WorkflowConfig)
    
    # Stage 2 configurations
    stage2: Stage2Config = Field(default_factory=Stage2Config)
    enhanced_brand: EnhancedBrandConfig = Field(default_factory=EnhancedBrandConfig)
    agents: AgentsConfig = Field(default_factory=AgentsConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    notifications: NotificationsConfig = Field(default_factory=NotificationsConfig)
    analytics: AnalyticsConfig = Field(default_factory=AnalyticsConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    
    # LLM Configurations - now supports all 3 models
    llm_configs: Dict[str, LLMConfig] = Field(default_factory=dict)
    
    # Backward compatibility for Stage 1
    enable_ranking_detection: bool = True
    ranking_keywords: List[str] = [
        "first", "top", "best", "leading", "number one", "#1", "premier", 
        "foremost", "primary", "top-rated", "highest-rated", "industry leader", "market leader"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"
    
    def __init__(self, config_file: str = "config.yaml", **kwargs):
        """Initialize settings from config file and environment variables."""
        
        # Load from YAML config file if it exists
        config_data = {}
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f) or {}
        
        # Process LLM configurations with environment variable overrides
        merged_llm_configs = self._process_llm_configs(config_data)
        
        # Process Google Sheets configuration
        google_sheets_config = self._process_google_sheets_config(config_data)
        
        # Process Stage 2 configurations
        stage2_config = self._process_stage2_config(config_data)
        
        # Merge config data with defaults
        merged_config = {
            **config_data,
            **kwargs,
            "llm_configs": merged_llm_configs,
            "google_sheets": google_sheets_config,
            "stage2": stage2_config,
            "openai_api_key": os.getenv("OPENAI_API_KEY", "") or merged_llm_configs.get("openai", {}).get("api_key", ""),
            "perplexity_api_key": os.getenv("PERPLEXITY_API_KEY", "") or merged_llm_configs.get("perplexity", {}).get("api_key", ""),
            "gemini_api_key": os.getenv("GEMINI_API_KEY", "") or merged_llm_configs.get("gemini", {}).get("api_key", ""),  # New for Stage 2
        }
        
        super().__init__(**merged_config)
    
    def _process_llm_configs(self, config_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Process LLM configurations with environment variable support."""
        merged_llm_configs = dict(config_data.get("llm_configs", {}))
        
        # OpenAI configuration
        openai_key = os.getenv("OPENAI_API_KEY", "")
        if openai_key:
            yaml_openai = merged_llm_configs.get("openai", {}) or {}
            merged_llm_configs["openai"] = {
                "name": "openai",
                "api_key": openai_key,
                "model": yaml_openai.get("model", "gpt-3.5-turbo"),
                "max_tokens": yaml_openai.get("max_tokens", 1000),
                "temperature": yaml_openai.get("temperature", 0.1),
                "timeout": yaml_openai.get("timeout", 30),
            }
        elif "openai" in merged_llm_configs and merged_llm_configs["openai"].get("api_key"):
            yaml_openai = merged_llm_configs["openai"]
            merged_llm_configs["openai"] = {
                "name": "openai",
                "api_key": yaml_openai["api_key"],
                "model": yaml_openai.get("model", "gpt-3.5-turbo"),
                "max_tokens": yaml_openai.get("max_tokens", 1000),
                "temperature": yaml_openai.get("temperature", 0.1),
                "timeout": yaml_openai.get("timeout", 30),
            }
        
        # Perplexity configuration
        perplexity_key = os.getenv("PERPLEXITY_API_KEY", "")
        if perplexity_key:
            yaml_ppx = merged_llm_configs.get("perplexity", {}) or {}
            merged_llm_configs["perplexity"] = {
                "name": "perplexity",
                "api_key": perplexity_key,
                "model": yaml_ppx.get("model", "llama-3.1-sonar-small-128k-online"),
                "max_tokens": yaml_ppx.get("max_tokens", 1000),
                "temperature": yaml_ppx.get("temperature", 0.1),
                "timeout": yaml_ppx.get("timeout", 30),
            }
        elif "perplexity" in merged_llm_configs and merged_llm_configs["perplexity"].get("api_key"):
            yaml_ppx = merged_llm_configs["perplexity"]
            merged_llm_configs["perplexity"] = {
                "name": "perplexity",
                "api_key": yaml_ppx["api_key"],
                "model": yaml_ppx.get("model", "llama-3.1-sonar-small-128k-online"),
                "max_tokens": yaml_ppx.get("max_tokens", 1000),
                "temperature": yaml_ppx.get("temperature", 0.1),
                "timeout": yaml_ppx.get("timeout", 30),
            }
        
        # Gemini configuration (NEW for Stage 2)
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        if gemini_key:
            yaml_gemini = merged_llm_configs.get("gemini", {}) or {}
            merged_llm_configs["gemini"] = {
                "name": "gemini",
                "api_key": gemini_key,
                "model": yaml_gemini.get("model", "gemini-pro"),
                "max_tokens": yaml_gemini.get("max_tokens", 1000),
                "temperature": yaml_gemini.get("temperature", 0.1),
                "timeout": yaml_gemini.get("timeout", 30),
            }
        elif "gemini" in merged_llm_configs and merged_llm_configs["gemini"].get("api_key"):
            yaml_gemini = merged_llm_configs["gemini"]
            merged_llm_configs["gemini"] = {
                "name": "gemini",
                "api_key": yaml_gemini["api_key"],
                "model": yaml_gemini.get("model", "gemini-pro"),
                "max_tokens": yaml_gemini.get("max_tokens", 1000),
                "temperature": yaml_gemini.get("temperature", 0.1),
                "timeout": yaml_gemini.get("timeout", 30),
            }
        
        return merged_llm_configs
    
    def _process_google_sheets_config(self, config_data: Dict[str, Any]) -> GoogleSheetsConfig:
        """Process Google Sheets configuration."""
        yaml_gs = config_data.get("google_sheets", {}) or {}
        spreadsheet_id = os.getenv("GOOGLE_SPREADSHEET_ID") or yaml_gs.get("spreadsheet_id", "")
        
        return GoogleSheetsConfig(
            spreadsheet_id=spreadsheet_id,
            worksheet_name=yaml_gs.get("worksheet_name", "Brand_Monitoring"),
            credentials_file=yaml_gs.get("credentials_file", "credentials.json"),
            auto_setup_headers=yaml_gs.get("auto_setup_headers", True),
            batch_size=yaml_gs.get("batch_size", 100),
            enable_validation=yaml_gs.get("enable_validation", True)
        )
    
    def _process_stage2_config(self, config_data: Dict[str, Any]) -> Stage2Config:
        """Process Stage 2 specific configuration."""
        yaml_stage2 = config_data.get("stage2", {}) or {}
        
        # Handle ranking detection config
        ranking_config_data = yaml_stage2.get("ranking_detection", {})
        ranking_config = RankingDetectionConfig(**ranking_config_data)
        
        return Stage2Config(
            enable_ranking_detection=yaml_stage2.get("enable_ranking_detection", True),
            enable_cost_tracking=yaml_stage2.get("enable_cost_tracking", True),
            enable_analytics=yaml_stage2.get("enable_analytics", True),
            ranking_detection=ranking_config
        )
    
    def validate_configuration(self) -> List[str]:
        """Validate all configuration settings and return any errors."""
        errors = []
        
        # Check API keys - at least one required
        available_keys = [
            self.openai_api_key, 
            self.perplexity_api_key, 
            self.gemini_api_key  # Include Gemini for Stage 2
        ]
        
        if not any(available_keys):
            errors.append("At least one API key (OpenAI, Perplexity, or Gemini) is required")
        
        # Check brand configuration
        if not self.brand.target_brand:
            errors.append("Target brand name is missing")
        
        # Stage 2 validations
        if self.stage2.enable_ranking_detection:
            if self.stage2.ranking_detection.max_position <= 0:
                errors.append("Maximum ranking position must be greater than 0")
            
            if not (0 <= self.stage2.ranking_detection.min_confidence <= 1):
                errors.append("Ranking detection confidence must be between 0 and 1")
        
        return errors
    
    def get_llm_config(self, llm_name: str) -> Optional[LLMConfig]:
        """Get configuration for a specific LLM."""
        config_dict = self.llm_configs.get(llm_name)
        if config_dict:
            return LLMConfig(**config_dict)
        return None
    
    def add_llm_config(self, name: str, config: LLMConfig):
        """Add a new LLM configuration."""
        self.llm_configs[name] = config.model_dump()
    
    def get_available_agents(self) -> List[str]:
        """Get list of available agents based on configured API keys."""
        available = []
        
        if self.openai_api_key and "openai" in self.llm_configs:
            available.append("openai")
        
        if self.perplexity_api_key and "perplexity" in self.llm_configs:
            available.append("perplexity")
        
        if self.gemini_api_key and "gemini" in self.llm_configs:  # New for Stage 2
            available.append("gemini")
        
        return available
    
    def is_stage2_enabled(self) -> bool:
        """Check if Stage 2 features are enabled."""
        return (self.stage2.enable_ranking_detection or 
                self.stage2.enable_cost_tracking or 
                self.stage2.enable_analytics)
    
    def get_stage2_features(self) -> Dict[str, bool]:
        """Get status of Stage 2 features."""
        return {
            "ranking_detection": self.stage2.enable_ranking_detection,
            "cost_tracking": self.stage2.enable_cost_tracking,
            "analytics": self.stage2.enable_analytics,
            "gemini_agent": bool(self.gemini_api_key),
            "enhanced_brand_detection": True,  # Always available in Stage 2
        }

# Global settings instance
settings = None

def get_settings(config_file: str = "config.yaml") -> Settings:
    """Get or create the global settings instance."""
    global settings
    if settings is None:
        settings = Settings(config_file=config_file)
    return settings

def reload_settings(config_file: str = "config.yaml") -> Settings:
    """Reload settings from configuration file."""
    global settings
    settings = Settings(config_file=config_file)
    return settings

def validate_stage2_requirements() -> Dict[str, Any]:
    """Validate that Stage 2 requirements are met."""
    settings = get_settings()
    
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "available_features": []
    }
    
    # Check for at least 2 agents (Stage 1 requirement)
    available_agents = settings.get_available_agents()
    if len(available_agents) < 2:
        validation_result["errors"].append("At least 2 LLM agents required for multi-agent functionality")
        validation_result["valid"] = False
    
    # Check for 3 agents (Stage 2 ideal)
    if len(available_agents) < 3:
        validation_result["warnings"].append("Stage 2 works best with all 3 LLM agents (OpenAI, Perplexity, Gemini)")
    
    # Check Google Sheets configuration
    if not settings.google_sheets.spreadsheet_id:
        validation_result["warnings"].append("Google Sheets not configured - results won't be stored")
    
    # List available features
    validation_result["available_features"] = list(settings.get_stage2_features().keys())
    
    return validation_result