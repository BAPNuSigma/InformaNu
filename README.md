# InformaNu Q&A Bot

A Streamlit-powered Q&A bot for BAP-NuSigma, leveraging OpenAI and Google Sheets for dynamic, document-based answers.

## Features
- **Chatbot UI**: Friendly, policy-aware assistant for your chapter
- **PDF Knowledge Base**: Extracts and indexes information from PDFs
- **Google Sheets Integration**: Automatically generates PDFs from a Google Sheet
- **OpenAI GPT Integration**: Uses GPT-3.5/4 for conversational answers
- **Secure Credentials**: Uses environment variables or Streamlit secrets

---

## Local Development

### 1. Clone the Repository
```bash
git clone https://github.com/BAPNuSigma/InformaNu.git
cd InformaNu
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Secrets
Create a file at `.streamlit/secrets.toml` with the following structure:
```toml
[openai]
api_key = "your-openai-api-key"

[google_credentials]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "your-private-key"
client_email = "your-client-email"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
```

### 4. Run the App
```bash
streamlit run streamlit_app.py
```

---

## Deployment on Render

1. **Push your code to GitHub**
2. **Create a new Web Service on [Render](https://render.com/)**
3. **Set Environment Variables** in the Render dashboard:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `GOOGLE_CREDENTIALS`: The full JSON string of your Google service account credentials
4. **Deploy!**

The app will automatically use environment variables in production and `secrets.toml` locally.

---

## Usage
- Ask questions about your chapter or national policies
- The bot will answer using only the information in the indexed PDFs and Google Sheet
- If the answer is not found, the bot will say so

---

## Troubleshooting
- **No secrets file found**: Make sure you have `.streamlit/secrets.toml` locally, or environment variables set on Render
- **Google credentials not found**: Double-check your `GOOGLE_CREDENTIALS` value and format
- **No PDFs found**: The app generates PDFs from Google Sheets on first run; check logs if this fails

---

## License
MIT

