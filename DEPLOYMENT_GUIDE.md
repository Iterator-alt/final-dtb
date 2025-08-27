# 🚀 Streamlit Cloud Deployment Guide

This guide will help you deploy the DataTobiz Brand Monitoring System to Streamlit Cloud.

## 📋 Prerequisites

Before deploying, ensure you have:

1. **GitHub Account**: Your code is already pushed to GitHub
2. **Streamlit Cloud Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)
3. **API Keys**: Collect all required API keys
4. **Google Sheets Setup**: Prepare your Google Sheets spreadsheet

## 🔑 Required API Keys

You'll need the following API keys:

### 1. OpenAI API Key
- Visit [OpenAI Platform](https://platform.openai.com/api-keys)
- Create a new API key
- Copy the key (starts with `sk-`)

### 2. Perplexity API Key
- Visit [Perplexity Settings](https://www.perplexity.ai/settings/api)
- Generate a new API key
- Copy the key

### 3. Google Gemini API Key
- Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
- Create a new API key
- Copy the key

### 4. Google Sheets Setup
- Create a Google Sheets spreadsheet
- Note the spreadsheet ID from the URL
- Set up Google Cloud Service Account:
  1. Go to [Google Cloud Console](https://console.cloud.google.com/)
  2. Create a new project or select existing
  3. Enable Google Sheets API
  4. Create Service Account:
     - Go to IAM & Admin > Service Accounts
     - Click "Create Service Account"
     - Download JSON credentials file
  5. Share your spreadsheet with the service account email

## 🌐 Deploy to Streamlit Cloud

### Step 1: Access Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"

### Step 2: Configure App
1. **Repository**: Select `Iterator-alt/final-dtb`
2. **Branch**: Select `master`
3. **Main file path**: Enter `streamlit_app.py`
4. **App URL**: Choose your preferred URL (optional)

### Step 3: Configure Secrets
Click on "Advanced settings" and add the following secrets:

```toml
OPENAI_API_KEY = "sk-your-openai-api-key-here"
PERPLEXITY_API_KEY = "your-perplexity-api-key-here"
GEMINI_API_KEY = "your-gemini-api-key-here"
GOOGLE_SHEETS_SPREADSHEET_ID = "your-spreadsheet-id-here"
GOOGLE_SERVICE_ACCOUNT_CREDENTIALS = """
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
}
"""
```

### Step 4: Deploy
1. Click "Deploy!"
2. Wait for the deployment to complete
3. Your app will be available at the provided URL

## 🔧 Post-Deployment Configuration

### Step 1: Test the Application
1. Open your deployed Streamlit app
2. Check if all secrets are properly configured
3. Use the "Test Connections" button in the sidebar
4. Verify all agents are online

### Step 2: Configure Google Sheets
1. Ensure your Google Sheets spreadsheet is shared with the service account
2. The app will automatically create the required worksheet
3. Verify data is being stored correctly

### Step 3: Test Brand Monitoring
1. Enter a test query like "DataTobiz software development"
2. Click "Start Brand Monitoring"
3. Verify results are displayed and stored

## 🛠️ Troubleshooting

### Common Issues

#### 1. Missing Secrets Error
**Problem**: App shows "Configuration Required" message
**Solution**: 
- Check all secrets are properly configured in Streamlit Cloud
- Ensure no extra spaces or quotes in secret values
- Verify API keys are valid

#### 2. Google Sheets Access Error
**Problem**: "Failed to access Google Sheets"
**Solution**:
- Verify service account JSON is complete
- Check spreadsheet is shared with service account email
- Ensure Google Sheets API is enabled

#### 3. Agent Connection Failures
**Problem**: Some agents show as offline
**Solution**:
- Verify API keys are correct
- Check API quotas and limits
- Test individual API connections

#### 4. Deployment Failures
**Problem**: App fails to deploy
**Solution**:
- Check requirements.txt is valid
- Verify all dependencies are available
- Check for syntax errors in code

### Debug Steps

1. **Check Logs**: View deployment logs in Streamlit Cloud
2. **Test Locally**: Run `streamlit run streamlit_app.py` locally first
3. **Verify Secrets**: Double-check all secret values
4. **API Testing**: Test API keys individually

## 📊 Monitoring Your Deployment

### Health Checks
- Use the "Test Connections" button regularly
- Monitor agent status in the sidebar
- Check Google Sheets for data consistency

### Performance Monitoring
- Monitor response times
- Check API usage and costs
- Review error logs

### Data Validation
- Verify brand mentions are being detected
- Check data quality in Google Sheets
- Monitor ranking detection accuracy

## 🔒 Security Best Practices

1. **API Key Management**:
   - Use environment-specific API keys
   - Regularly rotate API keys
   - Monitor API usage

2. **Access Control**:
   - Limit Google Sheets access to service account only
   - Use least privilege principle
   - Monitor access logs

3. **Data Privacy**:
   - Ensure no sensitive data in logs
   - Implement data retention policies
   - Follow GDPR compliance if applicable

## 📈 Scaling Considerations

### Performance Optimization
- Monitor memory usage
- Optimize API calls
- Implement caching where appropriate

### Cost Management
- Set API usage limits
- Monitor costs across providers
- Implement usage alerts

### Reliability
- Set up monitoring and alerting
- Implement retry logic
- Plan for disaster recovery

## 🆘 Support

If you encounter issues:

1. **Check Documentation**: Review this guide and README
2. **Streamlit Community**: Visit [discuss.streamlit.io](https://discuss.streamlit.io)
3. **GitHub Issues**: Report bugs in the repository
4. **API Documentation**: Check provider documentation

## 🎯 Next Steps

After successful deployment:

1. **Customize Brand Monitoring**: Adjust brand variations and settings
2. **Set Up Alerts**: Configure notifications for brand mentions
3. **Analytics Dashboard**: Review performance metrics
4. **Scale Up**: Add more queries and monitoring capabilities

---

**🔍 DataTobiz Brand Monitoring System | Successfully Deployed on Streamlit Cloud**
