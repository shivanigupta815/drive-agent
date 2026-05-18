# 📁 Google Drive AI Assistant

A conversational chatbot that helps you search and discover files in your Google Drive using natural language queries. Powered by OpenAI or Groq and LangChain for intelligent file searching.

## ✨ Features

- 🔍 **Natural Language Search** - Ask questions like "Show me all PDFs" or "Find spreadsheets about budget"
- ⚡ **Fast Results** - Optimized agent with reduced processing time
- 🎨 **User-Friendly UI** - Clean Streamlit interface
- 🔒 **Secure** - API keys and credentials never exposed
- 📊 **File Type Recognition** - Automatically identifies and formats different file types
- 🚀 **API Backend** - FastAPI backend for flexible deployment

## 🛠️ Setup Instructions

### 1. Prerequisites

- Python 3.8+
- Google Drive account
- OpenAI or Groq API key
- Google Service Account (for API access)

### 2. Create Google Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Drive API
4. Create Service Account:
   - Go to "Service Accounts"
   - Click "Create Service Account"
   - Download the JSON key file
5. Share your Google Drive folder with the service account email

### 3. Clone & Install

```bash
# Clone the repository
git clone <your-repo>
cd drive-agent

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file in the project root:

```bash
# Copy from example
cp .env.example .env
```

Then edit `.env` with your actual values:

```
# Google Drive Configuration
FOLDER_ID=your_google_drive_folder_id_here
SERVICE_ACCOUNT_FILE=service_account.json

# OpenAI or Groq API Key
OPENAI_API_KEY=your_openai_api_key_here
GROQ_API_KEY=your_groq_api_key_here
MODEL_NAME=openai:gpt-4o-mini

# Backend URL (for frontend)
BACKEND_URL=http://127.0.0.1:8000
```

**How to get FOLDER_ID:**
- Open your Google Drive folder in browser
- The folder ID is in the URL: `https://drive.google.com/drive/folders/YOUR_FOLDER_ID_HERE`

### 5. Place Service Account JSON

Copy your downloaded `service_account.json` to the project root directory.

```bash
# Example structure:
drive-agent/
├── .env
├── .env.example
├── .gitignore
├── service_account.json
├── requirements.txt
├── app.py
├── agent.py
├── drive_tool.py
└── ...
```

## 🚀 Running the Application

### Option 1: Streamlit UI (Recommended for beginners)

```bash
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

### Option 2: FastAPI Backend + Streamlit Frontend

Terminal 1 - Start backend API:
```bash
python main.py
# or
uvicorn main:app --reload
```

Terminal 2 - Start frontend:
```bash
streamlit run frontend.py
```

## � Deploy to Streamlit Cloud

The app works seamlessly on both **localhost** and **Streamlit Cloud**!

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Add Drive Agent chatbot"
git push origin main
```

### Step 2: Add to Streamlit Cloud

1. Go to [Streamlit Cloud](https://share.streamlit.io)
2. Click "New app"
3. Select your GitHub repository
4. Choose `app.py` as the main file

### Step 3: Configure Secrets on Streamlit Cloud

1. Click on your app settings (⚙️ in the top right)
2. Go to **Secrets**
3. Add your credentials as TOML format:

```toml
# Google Cloud Service Account credentials
[gcp_service_account]
type = "service_account"
project_id = "your_project_id"
private_key_id = "your_private_key_id"
private_key = "-----BEGIN PRIVATE KEY-----\nYour_key_here\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."

# Your Google Drive folder ID
FOLDER_ID = "1qkx58doSeYrcLjHPDysJyVJ36PsSqqlt"

# OpenAI or Groq API Key
OPENAI_API_KEY = "your_openai_api_key_here"
# Optional Groq key example
GROQ_API_KEY = "your_groq_api_key_here"
```

**How to get service account JSON for secrets:**
- Open your `service_account.json` file
- Copy the entire JSON content
- Paste into the `[gcp_service_account]` section above
- Escape line breaks in `private_key` with `\n`

### Step 4: Done! 🎉

Your app will be live on Streamlit Cloud once deployment completes.

**The app automatically:**
- ✅ Detects Streamlit Cloud and uses secrets
- ✅ Falls back to local `.env` on localhost
- ✅ Works without any code changes

## �💬 Usage Examples

Ask the chatbot questions like:

- "Show me all files"
- "Find all PDF files"
- "Show me spreadsheets"
- "Find documents with 'budget' in the name"
- "Show me files modified recently"
- "Find images"

## 🔒 Security Best Practices

✅ **What we've done:**
- API keys stored in `.env` files (not in code)
- `service_account.json` excluded from Git (in `.gitignore`)
- Removed all debug print statements that exposed sensitive data
- Added error handling to prevent info leakage
- Support for Streamlit secrets management

✅ **Before pushing to GitHub:**
1. Ensure `.gitignore` includes `.env`, `service_account.json`, and sensitive files
2. Never commit `.env` files
3. Use `.env.example` to show required variables
4. For production, use environment variables or secrets management

## ⚙️ Performance Improvements Made

1. **Faster Processing** - Reduced agent iterations from multiple loops to single execution
2. **Token Limit** - Set max_tokens=1024 to reduce processing overhead
3. **Query Optimization** - Intelligent query building for specific file types
4. **Increased Page Size** - Changed from 50 to 100 for better results
5. **Sorting** - Results sorted by modification date (newest first)

## 📝 Project Structure

```
drive-agent/
├── app.py              # Streamlit UI (primary interface)
├── frontend.py         # Alternative Streamlit frontend
├── main.py            # FastAPI backend
├── agent.py           # LangGraph agent with LLM logic
├── drive_tool.py      # Google Drive API integration
├── requirements.txt   # Python dependencies
├── .env               # Environment variables (create locally)
├── .env.example       # Template for environment variables
├── .gitignore        # Git ignore rules (secure)
├── service_account.json  # Google Service Account (DON'T commit)
└── README.md          # This file
```

## 🐛 Troubleshooting

### "FOLDER_ID environment variable not set"
- Make sure `.env` file exists in the project root
- Verify `FOLDER_ID` is set in `.env`
- Restart the application after changing `.env`

### "Service account file not found"
- Ensure `service_account.json` is in the project root
- Check the `SERVICE_ACCOUNT_FILE` path in `.env`

### "API Key not configured"
- Get API key from https://console.groq.com
- Add it to `.env` file: `GROQ_API_KEY=your_key`

### Search taking too long
- Check internet connection
- Ensure Google Drive folder isn't too large
- Try searching for specific file types

### No files found
- Verify service account has access to the folder
- Share the folder with the service account email
- Check folder permissions

## 📚 API Reference

### POST /chat

Search files via API endpoint.

**Request:**
```json
{
  "message": "show me all PDFs",
  "history": []
}
```

**Response:**
```json
{
  "response": "Found 5 file(s):\n1. 📕 **Report.pdf**\n...",
  "success": true
}
```

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is open source and available under the MIT License.

## 📞 Support

For issues and questions:
1. Check the Troubleshooting section
2. Review Google Cloud Console for permission issues
3. Verify all environment variables are set correctly

---

**Made with ❤️ for easier Google Drive management**
