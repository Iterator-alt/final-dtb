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
    for secret in required_secrets:
        if secret not in st.secrets or not st.secrets[secret]:
            missing_secrets.append(secret)
    
    return {
        "all_configured": len(missing_secrets) == 0,
        "missing_secrets": missing_secrets,
        "configured_secrets": [s for s in required_secrets if s not in missing_secrets]
    }

def create_credentials_file():
    """Create credentials.json file from Streamlit secrets."""
    try:
        credentials_json = st.secrets.get("GOOGLE_SERVICE_ACCOUNT_CREDENTIALS", "")
        if credentials_json:
            # Create temporary credentials file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                f.write(credentials_json)
                return f.name
        return None
    except Exception as e:
        st.error(f"Error creating credentials file: {str(e)}")
        return None

def create_config_from_secrets():
    """Create config.yaml content from Streamlit secrets."""
    config_content = f"""# Enhanced DataTobiz Brand Monitoring Configuration (Stage 2)
# Generated from Streamlit secrets

# LLM Configurations
llm_configs:
  openai:
    name: "openai"
    api_key: "{st.secrets.get('OPENAI_API_KEY', '')}"
    model: "gpt-3.5-turbo"
    max_tokens: 1000
    temperature: 0.1
    timeout: 30

  perplexity:
    name: "perplexity"
    api_key: "{st.secrets.get('PERPLEXITY_API_KEY', '')}"
    model: "sonar"
    max_tokens: 1000
    temperature: 0.1
    timeout: 30

  gemini:
    name: "gemini"
    api_key: "{st.secrets.get('GEMINI_API_KEY', '')}"
    model: "gemini-pro"
    max_tokens: 1000
    temperature: 0.1
    timeout: 30

# Google Sheets Configuration
google_sheets:
  spreadsheet_id: "{st.secrets.get('GOOGLE_SHEETS_SPREADSHEET_ID', '')}"
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
def initialize_api():
    """Initialize the brand monitoring API."""
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
        
        # Initialize API with temporary config
        api = EnhancedBrandMonitoringAPI(config_path)
        
        # Clean up temporary files
        try:
            os.unlink(config_path)
        except:
            pass
        
        return api
    except Exception as e:
        st.error(f"Failed to create API instance: {str(e)}")
        return None

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
    
    # Initialize API
    if st.session_state.api is None:
        with st.spinner("🚀 Initializing Brand Monitoring System..."):
            st.session_state.api = initialize_api()
    
    if st.session_state.api is None:
        st.error("Failed to initialize the system. Please check your configuration.")
        return
    
    # Sidebar for controls
    st.sidebar.title("🎛️ Control Panel")
    
    # System Status
    st.sidebar.markdown("### 📊 System Status")
    
    # Test connections
    if st.sidebar.button("🔍 Test Connections"):
        with st.spinner("Testing system connections..."):
            try:
                # Test API connections
                status = st.session_state.api.test_connections()
                st.sidebar.success("✅ All connections successful!")
                
                # Display agent status
                st.sidebar.markdown("### 🤖 Agent Status")
                for agent, is_healthy in status.items():
                    if is_healthy:
                        st.sidebar.markdown(f'<span class="agent-status agent-online">✅ {agent}</span>', unsafe_allow_html=True)
                    else:
                        st.sidebar.markdown(f'<span class="agent-status agent-offline">❌ {agent}</span>', unsafe_allow_html=True)
                        
            except Exception as e:
                st.sidebar.error(f"❌ Connection test failed: {str(e)}")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🎯 Brand Monitoring")
        
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
                        # Run the monitoring
                        results = st.session_state.api.monitor_brand(
                            query=search_query,
                            max_results=max_results,
                            search_depth=search_depth
                        )
                        
                        st.session_state.last_results = results
                        st.success("✅ Brand monitoring completed successfully!")
                        
                        # Display results
                        if results and 'data' in results:
                            st.markdown("### 📈 Results")
                            
                            # Convert to DataFrame for display
                            df = pd.DataFrame(results['data'])
                            st.dataframe(df, use_container_width=True)
                            
                            # Download button
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Results (CSV)",
                                data=csv,
                                file_name=f"brand_monitoring_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                        
                    except Exception as e:
                        st.error(f"❌ Monitoring failed: {str(e)}")
            else:
                st.warning("Please enter a search query.")
    
    with col2:
        st.markdown("### 📊 Quick Stats")
        
        if st.session_state.last_results:
            results = st.session_state.last_results
            
            # Display metrics
            if 'metrics' in results:
                metrics = results['metrics']
                
                st.markdown(f"""
                <div class="metric-card">
                    <strong>Total Mentions:</strong> {metrics.get('total_mentions', 0)}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="metric-card">
                    <strong>Positive Mentions:</strong> {metrics.get('positive_mentions', 0)}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="metric-card">
                    <strong>Negative Mentions:</strong> {metrics.get('negative_mentions', 0)}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="metric-card">
                    <strong>Neutral Mentions:</strong> {metrics.get('neutral_mentions', 0)}
                </div>
                """, unsafe_allow_html=True)
        
        # System info
        st.markdown("### ℹ️ System Info")
        st.markdown(f"""
        - **Version:** Stage 2 Enhanced
        - **Agents:** OpenAI, Perplexity, Gemini
        - **Storage:** Google Sheets
        - **Analytics:** Enabled
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>🔍 DataTobiz Brand Monitoring System | Enhanced Stage 2 | Powered by Multi-Agent AI</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
