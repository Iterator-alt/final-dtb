# 🔍 DataTobiz Brand Monitoring System

A comprehensive brand monitoring system with multi-agent AI orchestration, advanced analytics, and real-time tracking capabilities.

## 🚀 Features

- **Multi-Agent AI**: OpenAI, Perplexity, and Gemini integration
- **Real-time Monitoring**: Live brand mention tracking
- **Advanced Analytics**: Comprehensive reporting and insights
- **Ranking Detection**: Position tracking in search results
- **Google Sheets Integration**: Automatic data storage
- **Cost Tracking**: API usage monitoring
- **Modern UI**: Beautiful Streamlit interface

## 🏗️ Architecture

- **Stage 2 Enhanced**: Advanced multi-agent orchestration
- **LangGraph Workflow**: Sophisticated AI coordination
- **Asynchronous Processing**: High-performance parallel execution
- **Modular Design**: Extensible and maintainable codebase

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, asyncio, LangGraph
- **AI Models**: OpenAI GPT, Perplexity Sonar, Google Gemini
- **Storage**: Google Sheets API
- **Web Interface**: Streamlit
- **Deployment**: Streamlit Cloud

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Iterator-alt/final-dtb.git
   cd final-dtb
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure secrets** (for deployment)
   - `OPENAI_API_KEY`
   - `PERPLEXITY_API_KEY`
   - `GEMINI_API_KEY`
   - `GOOGLE_SHEETS_SPREADSHEET_ID`
   - `GOOGLE_SERVICE_ACCOUNT_CREDENTIALS`

## 🚀 Local Development

Run the application locally:

```bash
streamlit run streamlit_app.py
```

The app will be available at `http://localhost:8501`

## 🌐 Deployment

### Streamlit Cloud Deployment

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial deployment"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Configure secrets in the dashboard
   - Deploy!

### Required Secrets

Configure these secrets in Streamlit Cloud:

```toml
OPENAI_API_KEY = "your-openai-api-key"
PERPLEXITY_API_KEY = "your-perplexity-api-key"
GEMINI_API_KEY = "your-gemini-api-key"
GOOGLE_SHEETS_SPREADSHEET_ID = "your-spreadsheet-id"
GOOGLE_SERVICE_ACCOUNT_CREDENTIALS = "your-service-account-json"
```

## 📊 Usage

1. **Access the Application**: Open the deployed Streamlit app
2. **Configure Secrets**: Ensure all API keys are set
3. **Test Connections**: Use the sidebar to verify system health
4. **Start Monitoring**: Enter search queries and run brand monitoring
5. **View Results**: Analyze mentions, rankings, and analytics
6. **Download Data**: Export results as CSV

## 🎯 Key Capabilities

- **Brand Detection**: Advanced pattern matching and context analysis
- **Multi-Query Processing**: Batch monitoring of multiple search terms
- **Ranking Analysis**: Position tracking in search results
- **Sentiment Analysis**: Positive/negative mention classification
- **Historical Tracking**: Long-term trend analysis
- **Export Functionality**: CSV download capabilities

## 📈 Analytics Features

- Real-time brand mention tracking
- Detection rate analysis
- Ranking position monitoring
- Cost estimation and tracking
- Performance metrics
- Agent health monitoring

## 🔧 Configuration

The system uses a YAML configuration file that's automatically generated from Streamlit secrets:

```yaml
# LLM Configurations
llm_configs:
  openai:
    model: "gpt-3.5-turbo"
  perplexity:
    model: "sonar"
  gemini:
    model: "gemini-pro"

# Brand Configuration
brand:
  target_brand: "DataTobiz"
  brand_variations: ["DataTobiz", "Data Tobiz", ...]

# Stage 2 Features
stage2:
  enable_ranking_detection: true
  enable_cost_tracking: true
  enable_analytics: true
```

## 🤖 AI Agents

### OpenAI Agent
- Model: GPT-3.5-turbo
- Capabilities: Text analysis, brand detection
- Features: Context understanding, sentiment analysis

### Perplexity Agent
- Model: Sonar
- Capabilities: Web search, real-time data
- Features: Current information, search results

### Gemini Agent
- Model: Gemini Pro
- Capabilities: Multi-modal analysis
- Features: Advanced reasoning, pattern recognition

## 📊 Data Storage

- **Google Sheets Integration**: Automatic data storage
- **Real-time Updates**: Live data synchronization
- **Historical Tracking**: Long-term data retention
- **Export Capabilities**: CSV download functionality

## 🔒 Security

- **API Key Management**: Secure secret handling
- **Temporary Files**: Automatic cleanup of sensitive data
- **Access Control**: Streamlit Cloud security features
- **Data Privacy**: No sensitive data logging

## 📝 License

This project is proprietary software developed for DataTobiz.

## 🤝 Support

For support and questions:
- Check the application logs
- Verify API key configurations
- Ensure Google Sheets permissions
- Review Streamlit Cloud documentation

## 🚀 Quick Start

1. **Deploy to Streamlit Cloud**
2. **Configure API secrets**
3. **Test system connections**
4. **Start brand monitoring**
5. **Analyze results**

---

**🔍 DataTobiz Brand Monitoring System | Enhanced Stage 2 | Powered by Multi-Agent AI**