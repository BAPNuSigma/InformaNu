# InformaNu Q&A Bot

A Streamlit-powered Q&A bot for BAP-NuSigma, leveraging OpenAI and document-based answers.

## Features
- **Chatbot UI**: Friendly, policy-aware assistant for your chapter
- **Document Knowledge Base**: Extracts and indexes information from PDFs, Word documents, and Markdown files
- **OpenAI GPT Integration**: Uses GPT-3.5 for conversational answers
- **Secure Credentials**: Uses environment variables or Streamlit secrets
- **Comprehensive Knowledge**: Includes national policies, membership requirements, officer roles, and chapter schedules

## Knowledge Base Contents
The bot is trained on the following documents:
- BAP National Policies
- Candidate Requirements
- Member Requirements
- Membership Types and Requirements
- Officer Roles
- Social Media Policy
- Spring 2025 Schedule

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
4. **Deploy!**

The app will automatically use environment variables in production and `secrets.toml` locally.

---

## Usage
- Ask questions about your chapter or national policies
- The bot will answer using only the information in the indexed documents
- If the answer is not found, the bot will say so
- The bot maintains context of the conversation for more natural interactions

---

## Troubleshooting
- **No secrets file found**: Make sure you have `.streamlit/secrets.toml` locally, or environment variables set on Render
- **No documents found**: Check if the knowledge_base directory contains the required documents
- **API Key Issues**: Verify your OpenAI API key is correctly set in secrets or environment variables

---

## License
MIT

