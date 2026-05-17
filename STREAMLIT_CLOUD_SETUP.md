# 🚀 Deploy to Streamlit Cloud - Quick Guide

Your app is now ready to work on both **localhost** and **Streamlit Cloud**!

## Quick Deployment Steps

### 1. Push to GitHub

Make sure your repo has these files:
```
drive-agent/
├── app.py
├── agent.py
├── drive_tool.py
├── requirements.txt
├── .gitignore (includes service_account.json)
├── .env.example
├── .streamlit/secrets.toml.example
└── README.md
```

**Never commit:**
- `.env`
- `service_account.json`
- `.streamlit/secrets.toml`

### 2. Go to Streamlit Cloud

1. Visit https://share.streamlit.io
2. Click "New app"
3. Connect your GitHub account
4. Select your repository
5. Choose branch: `main`
6. Set main file path: `app.py`

### 3. Add Secrets on Streamlit Cloud

After app is created:

1. Click ⚙️ (Settings) in top right
2. Go to **Secrets**
3. Paste your secrets in TOML format:

```toml
# From your service_account.json file
[gcp_service_account]
type = "service_account"
project_id = "your_project_id"
private_key_id = "key_id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "service-account@project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."

# Your Google Drive folder ID
FOLDER_ID = "1qkx58doSeYrcLjHPDysJyVJ36PsSqqlt"

# Your Groq API key
GROQ_API_KEY = "your_groq_api_key_here"
```

### 4. Done! 🎉

App URL: `https://drive-agent-uebufjudnecjscf4wyuzyy.streamlit.app`

## How It Works

The `drive_tool.py` automatically:
- ✅ Detects if running on Streamlit Cloud
- ✅ Uses `st.secrets` on cloud (secrets.toml)
- ✅ Uses local `.env` on localhost
- ✅ No code changes needed!

## Troubleshooting

**"FOLDER_ID not found"**
- Add `FOLDER_ID = "your_id"` to Streamlit secrets

**"Service account credentials not found"**
- Add `[gcp_service_account]` section to Streamlit secrets
- Make sure `private_key` has `\n` line breaks

**"API Key not found"**
- Add `GROQ_API_KEY = "your_key"` to Streamlit secrets

## File Locations

| Env | Credentials | Folder ID |
|-----|-------------|-----------|
| Localhost | `.env` or `service_account.json` | `.env` |
| Streamlit Cloud | `st.secrets['gcp_service_account']` | `st.secrets['FOLDER_ID']` |
