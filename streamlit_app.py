#!/usr/bin/env python3
"""
DataTobiz Brand Monitoring System - Streamlit Web Application

A comprehensive web interface for brand monitoring with multi-agent orchestration,
ranking detection, and advanced analytics. Optimized for Streamlit Cloud deployment.
"""

import streamlit as st
import asyncio
import sys
import os
import tempfile
import json
from pathlib import Path
import pandas as pd
from datetime import datetime
import time

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from main import EnhancedBrandMonitoringAPI
from src.utils.logger import setup_logging

# Setup logging
setup_logging(log_level="INFO")

# Page configuration
st.set_page_config(
    page_title="DataTobiz Brand Monitoring System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
    }
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        border-left: 5px solid #1f77b4;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
    }
    .agent-status {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 2rem;
        font-size: 0.875rem;
        font-weight: bold;
        margin: 0.25rem;
    }
    .agent-online {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        border: 2px solid #28a745;
    }
    .agent-offline {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        color: #721c24;
        border: 2px solid #dc3545;
    }
    .secret-status {
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        font-weight: bold;
    }
    .secret-ok {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        border: 2px solid #28a745;
    }
    .secret-missing {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        color: #721c24;
        border: 2px solid #dc3545;
    }
    .stButton > button {
        background: linear-gradient(135deg, #1f77b4 0%, #ff7f0e 100%);
        color: white;
        border: none;
        border-radius: 2rem;
        padding: 0.75rem 2rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(31, 119, 180, 0.3);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'api' not in st.session_state:
    st.session_state.api = None
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
if 'last_results' not in st.session_state:
    st.session_state.last_results = None

def check_streamlit_secrets():
    """Check if all required Streamlit secrets are configured."""
    required_secrets = [
        "OPENAI_API_KEY",
        "PERPLEXITY_API_KEY", 
        "GEMINI_API_KEY",
        "GOOGLE_SHEETS_SPREADSHEET_ID",
        "GOOGLE_SERVICE_ACCOUNT_CREDENTIALS"
    ]
    
    missing_secrets = []
    configured_secrets = []
    
    for secret in required_secrets:
        if secret in st.secrets and st.secrets[secret]:
            configured_secrets.append(secret)
        else:
            missing_secrets.append(secret)
    
    return {
        "all_configured": len(missing_secrets) == 0,
        "missing_secrets": missing_secrets,
        "configured_secrets": configured_secrets
    }

def debug_secrets():
    """Debug function to check what secrets are available."""
    debug_info = {
        "available_secrets": list(st.secrets.keys()),
        "secret_lengths": {}
    }
    
    for secret_name in ["OPENAI_API_KEY", "PERPLEXITY_API_KEY", "GEMINI_API_KEY", "GOOGLE_SHEETS_SPREADSHEET_ID", "GOOGLE_SERVICE_ACCOUNT_CREDENTIALS"]:
        if secret_name in st.secrets:
            secret_value = st.secrets[secret_name]
            if isinstance(secret_value, str):
                debug_info["secret_lengths"][secret_name] = len(secret_value)
            else:
                debug_info["secret_lengths"][secret_name] = f"Type: {type(secret_value)}"
        else:
            debug_info["secret_lengths"][secret_name] = "Not found"
    
    return debug_info

def create_credentials_file():
    """Create credentials.json file from Streamlit secrets."""
    try:
        credentials_json = st.secrets.get("GOOGLE_SERVICE_ACCOUNT_CREDENTIALS", "")
        if credentials_json:
            # Create credentials file in current directory
            credentials_path = "credentials.json"
            with open(credentials_path, 'w') as f:
                f.write(credentials_json)
            return credentials_path
        return None
    except Exception as e:
        st.error(f"Error creating credentials file: {str(e)}")
        return None

def create_config_from_secrets():
    """Create config.yaml content from Streamlit secrets."""
    
    # Validate API keys
    openai_key = st.secrets.get('OPENAI_API_KEY', '')
    perplexity_key = st.secrets.get('PERPLEXITY_API_KEY', '')
    gemini_key = st.secrets.get('GEMINI_API_KEY', '')
    spreadsheet_id = st.secrets.get('GOOGLE_SHEETS_SPREADSHEET_ID', '')
    credentials_json = st.secrets.get('GOOGLE_SERVICE_ACCOUNT_CREDENTIALS', '')
    
    # Check if keys are properly formatted
    if not openai_key.startswith('sk-'):
        st.warning("⚠️ OpenAI API key format may be incorrect (should start with 'sk-')")
    
    if not perplexity_key.startswith('pplx-'):
        st.warning("⚠️ Perplexity API key format may be incorrect (should start with 'pplx-')")
    
    # Check if Perplexity key is valid length
    if perplexity_key and len(perplexity_key) < 20:
        st.warning("⚠️ Perplexity API key appears to be too short")
    
    # Check Google Sheets configuration
    if not spreadsheet_id:
        st.warning("⚠️ Google Sheets Spreadsheet ID is missing")
        st.info("💡 The spreadsheet ID is the long string in your Google Sheets URL (e.g., 1u6xIltHLEO-cfrFwCNVFL2726nRwaAMD90aqAbZKjgQ)")
    else:
        st.success(f"✅ Google Sheets Spreadsheet ID: {spreadsheet_id}")
    
    if not credentials_json:
        st.warning("⚠️ Google Service Account credentials are missing")
    else:
        try:
            import json
            creds_data = json.loads(credentials_json)
            if 'client_email' not in creds_data:
                st.warning("⚠️ Google Service Account credentials appear to be invalid (missing client_email)")
            else:
                st.success(f"✅ Google Service Account configured for: {creds_data['client_email']}")
        except json.JSONDecodeError:
            st.warning("⚠️ Google Service Account credentials are not valid JSON")
    
    config_content = f"""# Enhanced DataTobiz Brand Monitoring Configuration (Stage 2)
# Generated from Streamlit secrets

# LLM Configurations
llm_configs:
  openai:
    name: "openai"
    api_key: "{openai_key}"
    model: "gpt-3.5-turbo"
    max_tokens: 1000
    temperature: 0.1
    timeout: 30

  perplexity:
    name: "perplexity"
    api_key: "{perplexity_key}"
    model: "sonar"
    max_tokens: 1000
    temperature: 0.1
    timeout: 30

  gemini:
    name: "gemini"
    api_key: "{gemini_key}"
    model: "gemini-pro"
    max_tokens: 1000
    temperature: 0.1
    timeout: 30

# Google Sheets Configuration
google_sheets:
  spreadsheet_id: "{spreadsheet_id}"
  worksheet_name: "Brand_Monitoring_New"
  credentials_file: "credentials.json"
  auto_setup_headers: true
  batch_size: 100
  enable_validation: true

# Brand Configuration
brand:
  target_brand: "DataTobiz"
  brand_variations:
    - "DataTobiz"
    - "Data Tobiz"
    - "data tobiz"
    - "DATATOBIZ"
    - "DataToBiz"
    - "Data-Tobiz"
    - "datatobiz.com"
  case_sensitive: false
  partial_match: true

# Workflow Configuration
workflow:
  max_retries: 3
  retry_delay: 1.0
  parallel_execution: true
  timeout_per_agent: 60
  log_level: "INFO"

# Stage 2 Configuration
stage2:
  enable_ranking_detection: true
  enable_cost_tracking: true
  enable_analytics: true
  
  ranking_detection:
    max_position: 20
    min_confidence: 0.6
    enable_ordinal_detection: true
    enable_list_detection: true
    enable_keyword_detection: true
    enable_numeric_detection: true

# Enhanced Brand Configuration
enhanced_brand:
  context_analysis:
    context_window: 200
    enable_sentiment_analysis: false
    positive_keywords:
      - "excellent"
      - "outstanding"
      - "innovative"
      - "reliable"
      - "powerful"
      - "comprehensive"
      - "award-winning"
      - "recognized"
      - "trusted"
      - "proven"
    negative_keywords:
      - "poor"
      - "bad"
      - "disappointing"
      - "limited"
      - "lacking"
      - "outdated"
      - "problematic"
      - "difficult"
      - "complex"
      - "unreliable"
"""
    return config_content

@st.cache_resource
def create_api():
    """Create the brand monitoring API instance."""
    try:
        # Check secrets first
        secrets_status = check_streamlit_secrets()
        if not secrets_status["all_configured"]:
            st.error("❌ Missing required secrets. Please configure all secrets in Streamlit Cloud.")
            return None
        
        # Create temporary config file
        config_content = create_config_from_secrets()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            config_path = f.name
        
        # Create credentials file
        credentials_path = create_credentials_file()
        if not credentials_path:
            st.error("❌ Failed to create credentials file from secrets.")
            return None
        
        # Create API with temporary config
        api = EnhancedBrandMonitoringAPI(config_path)
        
        # Store the config path for later cleanup
        api._temp_config_path = config_path
        
        # Force reload Google Sheets config from environment variables
        if api.settings:
            api.settings.reload_google_sheets_config()
        
        return api
    except Exception as e:
        st.error(f"Failed to create API instance: {str(e)}")
        return None

async def initialize_api_async(api):
    """Initialize the API asynchronously."""
    try:
        result = await api.initialize()
        
        # Clean up temporary config file after initialization
        if hasattr(api, '_temp_config_path'):
            try:
                os.unlink(api._temp_config_path)
                delattr(api, '_temp_config_path')
            except:
                pass
        
        return result
    except Exception as e:
        st.error(f"Failed to initialize API: {str(e)}")
        return False

def main():
    """Main application function."""
    st.markdown('<h1 class="main-header">🔍 DataTobiz Brand Monitoring System</h1>', unsafe_allow_html=True)
    
    # Check secrets status
    secrets_status = check_streamlit_secrets()
    
    if not secrets_status["all_configured"]:
        st.error("❌ **Configuration Required**")
        st.markdown("""
        ### Missing Streamlit Secrets
        Please configure the following secrets in your Streamlit Cloud deployment:
        
        **Required Secrets:**
        - `OPENAI_API_KEY` - Your OpenAI API key
        - `PERPLEXITY_API_KEY` - Your Perplexity API key  
        - `GEMINI_API_KEY` - Your Google Gemini API key
        - `GOOGLE_SHEETS_SPREADSHEET_ID` - Your Google Sheets spreadsheet ID
        - `GOOGLE_SERVICE_ACCOUNT_CREDENTIALS` - Your Google service account JSON credentials
        
        **How to configure:**
        1. Go to your Streamlit Cloud dashboard
        2. Navigate to your app settings
        3. Add the secrets in the "Secrets" section
        4. Redeploy your app
        """)
        
        st.markdown("### Current Secret Status:")
        for secret in secrets_status["configured_secrets"]:
            st.markdown(f'<div class="secret-status secret-ok">✅ {secret}</div>', unsafe_allow_html=True)
        for secret in secrets_status["missing_secrets"]:
            st.markdown(f'<div class="secret-status secret-missing">❌ {secret}</div>', unsafe_allow_html=True)
        
        return
    
    # Create API instance
    if st.session_state.api is None:
        st.session_state.api = create_api()
    
    if st.session_state.api is None:
        st.error("Failed to create the system. Please check your configuration.")
        return
    
    # Initialize API if not already initialized
    if not st.session_state.initialized:
        with st.spinner("🚀 Initializing Brand Monitoring System..."):
            import asyncio
            st.session_state.initialized = asyncio.run(initialize_api_async(st.session_state.api))
    
    if not st.session_state.initialized:
        st.error("Failed to initialize the system. Please check your configuration.")
        return
    
    # Sidebar for controls
    st.sidebar.title("🎛️ Control Panel")
    
    # System Status
    st.sidebar.markdown("### 📊 System Status")
    
    # Initialize button
    if not st.session_state.initialized:
        if st.sidebar.button("🚀 Initialize System", type="primary"):
            with st.spinner("Initializing system..."):
                import asyncio
                st.session_state.initialized = asyncio.run(initialize_api_async(st.session_state.api))
                if st.session_state.initialized:
                    st.sidebar.success("✅ System initialized!")
                    st.rerun()
                else:
                    st.sidebar.error("❌ Initialization failed!")
    
    # System health status
    if st.session_state.initialized:
        st.sidebar.markdown('<span class="agent-status agent-online">✅ System Online</span>', unsafe_allow_html=True)
        
        # Test connections
        if st.sidebar.button("🔍 Test Connections"):
            with st.spinner("Testing system connections..."):
                try:
                    # Test API connections (async)
                    import asyncio
                    status = asyncio.run(st.session_state.api.test_connections())
                    
                    if status.get('success', False):
                        st.sidebar.success("✅ All connections successful!")
                        
                        # Display agent status
                        st.sidebar.markdown("### 🤖 Agent Status")
                        for agent_name, agent_info in status.get('agents', {}).items():
                            if agent_info.get('healthy', False):
                                st.sidebar.markdown(f'<span class="agent-status agent-online">✅ {agent_name}</span>', unsafe_allow_html=True)
                            else:
                                st.sidebar.markdown(f'<span class="agent-status agent-offline">❌ {agent_name}</span>', unsafe_allow_html=True)
                        
                        # Display storage status
                        st.sidebar.markdown("### 💾 Storage Status")
                        storage_info = status.get('storage', {}).get('google_sheets', {})
                        if storage_info.get('available', False):
                            st.sidebar.markdown('<span class="agent-status agent-online">✅ Google Sheets</span>', unsafe_allow_html=True)
                        else:
                            st.sidebar.markdown('<span class="agent-status agent-offline">❌ Google Sheets</span>', unsafe_allow_html=True)
                        
                        # Display analytics status
                        st.sidebar.markdown("### 📊 Analytics Status")
                        analytics_info = status.get('analytics', {}).get('engine', {})
                        if analytics_info.get('available', False):
                            st.sidebar.markdown('<span class="agent-status agent-online">✅ Analytics Engine</span>', unsafe_allow_html=True)
                        else:
                            st.sidebar.markdown('<span class="agent-status agent-offline">❌ Analytics Engine</span>', unsafe_allow_html=True)
                            
                    else:
                        st.sidebar.error(f"❌ Connection test failed: {status.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    st.sidebar.error(f"❌ Connection test failed: {str(e)}")
    else:
        st.sidebar.markdown('<span class="agent-status agent-offline">❌ System Offline</span>', unsafe_allow_html=True)
    
    # Main content area with tabs
    tab1, tab2, tab3 = st.tabs(["🎯 Brand Monitoring", "📊 System Health", "📈 Analytics"])
    
    with tab1:
        st.markdown("### 🎯 Brand Monitoring")
        
        if not st.session_state.initialized:
            st.warning("⚠️ Please initialize the system first using the sidebar button.")
        else:
            # Input for search query
            search_query = st.text_input(
                "Enter search query for brand monitoring:",
                placeholder="e.g., 'DataTobiz software development services'",
                help="Enter a search query to monitor for DataTobiz mentions"
            )
            
            # Search options
            col1_1, col1_2 = st.columns(2)
            with col1_1:
                max_results = st.slider("Max Results", 5, 50, 10)
            with col1_2:
                search_depth = st.selectbox("Search Depth", ["Basic", "Comprehensive", "Deep Analysis"])
            
            # Run monitoring
            if st.button("🚀 Start Brand Monitoring", type="primary"):
                if search_query:
                    with st.spinner("🔍 Running brand monitoring analysis..."):
                        try:
                            # Run the monitoring (async)
                            import asyncio
                            results = asyncio.run(st.session_state.api.monitor_queries(
                                queries=[search_query],
                                mode="parallel",
                                enable_ranking=True,
                                enable_analytics=True
                            ))
                            
                            st.session_state.last_results = results
                            st.success("✅ Brand monitoring completed successfully!")
                            
                            # Display results
                            if results and results.get('success', False):
                                st.markdown("### 📈 Results")
                                
                                # Display summary
                                if 'summary' in results:
                                    summary = results['summary']
                                    col1, col2, col3, col4 = st.columns(4)
                                    with col1:
                                        st.metric("Total Queries", summary.get('total_queries', 0))
                                    with col2:
                                        st.metric("Brand Mentions", summary.get('brand_mentions_found', 0))
                                    with col3:
                                        detection_rate = summary.get('brand_detection_rate', 0)
                                        st.metric("Detection Rate", f"{detection_rate:.1%}")
                                    with col4:
                                        execution_time = summary.get('execution_time', 0)
                                        st.metric("Execution Time", f"{execution_time:.2f}s")
                                
                                # Display detailed results
                                if 'results' in results:
                                    st.markdown("### 📊 Detailed Results")
                                    for query, query_result in results['results'].items():
                                        with st.expander(f"Query: {query}"):
                                            found = "✅ Found" if query_result.get('found') else "❌ Not Found"
                                            confidence = f"{query_result.get('confidence', 0):.1%}"
                                            st.write(f"**Status:** {found}")
                                            st.write(f"**Confidence:** {confidence}")
                                            
                                            if 'ranking' in query_result and query_result['ranking']:
                                                st.write(f"**Ranking:** {query_result['ranking']}")
                                            
                                            # Agent breakdown
                                            if 'agents' in query_result:
                                                st.write("**Agent Results:**")
                                                for agent, agent_result in query_result['agents'].items():
                                                    status = "✅" if agent_result.get('status') == 'completed' else "❌"
                                                    st.write(f"{status} {agent}: {agent_result.get('found', False)}")
                                
                                # Download results
                                if results:
                                    import json
                                    json_data = json.dumps(results, indent=2)
                                    st.download_button(
                                        label="📥 Download Results (JSON)",
                                        data=json_data,
                                        file_name=f"brand_monitoring_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                        mime="application/json"
                                    )
                            else:
                                st.error(f"❌ Monitoring failed: {results.get('error', 'Unknown error')}")
                            
                        except Exception as e:
                            st.error(f"❌ Monitoring failed: {str(e)}")
                else:
                    st.warning("Please enter a search query.")
    
    with tab2:
        st.markdown("### 📊 System Health")
        
        if not st.session_state.initialized:
            st.warning("⚠️ Please initialize the system first using the sidebar button.")
        else:
            # System health overview
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🔧 System Status")
                st.markdown('<span class="agent-status agent-online">✅ System Online</span>', unsafe_allow_html=True)
                
                # Agent status
                st.markdown("#### 🤖 Agent Status")
                if st.session_state.api.workflow and st.session_state.api.workflow.agents:
                    for agent_name in st.session_state.api.workflow.agents.keys():
                        st.markdown(f'<span class="agent-status agent-online">✅ {agent_name}</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="agent-status agent-offline">❌ No agents available</span>', unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### 💾 Storage Status")
                if st.session_state.api.workflow and st.session_state.api.workflow.storage_manager:
                    st.markdown('<span class="agent-status agent-online">✅ Google Sheets Connected</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="agent-status agent-offline">❌ Storage not configured</span>', unsafe_allow_html=True)
                
                st.markdown("#### 📊 Analytics Status")
                if st.session_state.api.workflow and st.session_state.api.workflow.analytics_engine:
                    st.markdown('<span class="agent-status agent-online">✅ Analytics Engine Ready</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="agent-status agent-offline">❌ Analytics not available</span>', unsafe_allow_html=True)
            
            # Detailed health check
            if st.button("🔍 Run Detailed Health Check"):
                with st.spinner("Running comprehensive health check..."):
                    try:
                        import asyncio
                        status = asyncio.run(st.session_state.api.test_connections())
                        
                        if status.get('success', False):
                            st.success("✅ All systems operational!")
                            
                            # Display detailed status
                            st.markdown("#### 📋 Detailed Status Report")
                            
                            # Agents
                            st.markdown("**🤖 Agents:**")
                            for agent_name, agent_info in status.get('agents', {}).items():
                                if agent_info.get('healthy', False):
                                    st.markdown(f"- ✅ {agent_name}: {agent_info.get('model', 'Unknown')}")
                                else:
                                    st.markdown(f"- ❌ {agent_name}: {agent_info.get('error', 'Failed')}")
                            
                            # Storage
                            st.markdown("**💾 Storage:**")
                            storage_info = status.get('storage', {}).get('google_sheets', {})
                            if storage_info.get('available', False):
                                st.markdown(f"- ✅ Google Sheets: {storage_info.get('records_found', 'Unknown')} records")
                            else:
                                st.markdown(f"- ❌ Google Sheets: {storage_info.get('error', 'Not available')}")
                            
                            # Analytics
                            st.markdown("**📊 Analytics:**")
                            analytics_info = status.get('analytics', {}).get('engine', {})
                            if analytics_info.get('available', False):
                                st.markdown("- ✅ Analytics Engine: Ready")
                            else:
                                st.markdown(f"- ❌ Analytics Engine: {analytics_info.get('reason', 'Not available')}")
                            
                            # Stage 2 features
                            st.markdown("**🎯 Stage 2 Features:**")
                            stage2_features = status.get('stage2_features', {})
                            for feature, enabled in stage2_features.items():
                                status_icon = "✅" if enabled else "❌"
                                st.markdown(f"- {status_icon} {feature}")
                        else:
                            st.error(f"❌ Health check failed: {status.get('error', 'Unknown error')}")
                            
                    except Exception as e:
                        st.error(f"❌ Health check failed: {str(e)}")
            
            # Debug section
            with st.expander("🔧 Debug Information"):
                st.markdown("#### 🔍 Secrets Debug")
                debug_info = debug_secrets()
                
                st.markdown("**Available Secrets:**")
                for secret in debug_info["available_secrets"]:
                    st.write(f"- {secret}")
                
                st.markdown("**Secret Status:**")
                for secret_name, length_info in debug_info["secret_lengths"].items():
                    if length_info == "Not found":
                        st.markdown(f"- ❌ {secret_name}: Not configured")
                    else:
                        st.markdown(f"- ✅ {secret_name}: {length_info}")
                
                # Configuration debug
                st.markdown("#### ⚙️ Configuration Debug")
                if st.session_state.api and st.session_state.api.settings:
                    st.write("**Settings loaded:** ✅")
                    st.write(f"**Target brand:** {st.session_state.api.settings.brand.target_brand}")
                    st.write(f"**Spreadsheet ID:** {st.session_state.api.settings.google_sheets.spreadsheet_id}")
                    
                    # Debug environment variables
                    st.markdown("**Environment Variables:**")
                    import os
                    st.write(f"GOOGLE_SHEETS_SPREADSHEET_ID: {os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID', 'Not found')}")
                    st.write(f"GOOGLE_SPREADSHEET_ID: {os.getenv('GOOGLE_SPREADSHEET_ID', 'Not found')}")
                    
                    # Debug Google Sheets config
                    st.markdown("**Google Sheets Config:**")
                    gs_config = st.session_state.api.settings.google_sheets
                    st.write(f"Spreadsheet ID: '{gs_config.spreadsheet_id}'")
                    st.write(f"Credentials File: '{gs_config.credentials_file}'")
                    st.write(f"Worksheet Name: '{gs_config.worksheet_name}'")
                    st.write(f"Auto Setup Headers: {gs_config.auto_setup_headers}")
                    st.write(f"Batch Size: {gs_config.batch_size}")
                    st.write(f"Enable Validation: {gs_config.enable_validation}")
                else:
                    st.write("**Settings loaded:** ❌")
                
                # Workflow debug
                st.markdown("#### 🔄 Workflow Debug")
                if st.session_state.api and st.session_state.api.workflow:
                    st.write("**Workflow initialized:** ✅")
                    if st.session_state.api.workflow.agents:
                        st.write(f"**Available agents:** {list(st.session_state.api.workflow.agents.keys())}")
                    else:
                        st.write("**Available agents:** None")
                    
                    if st.session_state.api.workflow.storage_manager:
                        st.write("**Storage manager:** ✅")
                    else:
                        st.write("**Storage manager:** ❌")
                else:
                    st.write("**Workflow initialized:** ❌")
    
    with tab3:
        st.markdown("### 📈 Analytics Dashboard")
        
        if not st.session_state.initialized:
            st.warning("⚠️ Please initialize the system first using the sidebar button.")
        else:
            st.info("📊 Analytics dashboard will show historical data and trends.")
            
            # Display last results if available
            if st.session_state.last_results:
                st.markdown("#### 📊 Last Monitoring Results")
                results = st.session_state.last_results
                
                if results.get('success', False) and 'summary' in results:
                    summary = results['summary']
                    
                    # Metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Queries", summary.get('total_queries', 0))
                    with col2:
                        st.metric("Brand Mentions", summary.get('brand_mentions_found', 0))
                    with col3:
                        detection_rate = summary.get('brand_detection_rate', 0)
                        st.metric("Detection Rate", f"{detection_rate:.1%}")
                    with col4:
                        execution_time = summary.get('execution_time', 0)
                        st.metric("Execution Time", f"{execution_time:.2f}s")
    

    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>🔍 DataTobiz Brand Monitoring System | Enhanced Stage 2 | Powered by Multi-Agent AI</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
