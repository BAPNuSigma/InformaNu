# Beta Alpha Psi: Nu Sigma Chapter Q&A Bot

A specialized Q&A chatbot for Beta Alpha Psi: Nu Sigma Chapter that provides information about the chapter, events, requirements, and more.

## Setup Instructions

### Local Development

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
4. Run the Streamlit app:
   ```bash
   streamlit run streamlit_app.py
   ```

### Deployment on Streamlit Cloud

1. Fork this repository
2. Create a new app on Streamlit Cloud
3. Add your OpenAI API key to the app's secrets:
   - Go to your app's settings
   - Add a new secret with key `OPENAI_API_KEY` and your API key as the value

### Deployment on Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Add your OpenAI API key as an environment variable:
   - Key: `OPENAI_API_KEY`
   - Value: your API key

## Knowledge Base

The `knowledge_base` directory contains information about the chapter. To update the knowledge base:

1. Add new markdown files to the `knowledge_base` directory
2. Each file should focus on a specific topic (e.g., membership requirements, events, history)
3. Use clear headings and structured content

## Features

- Specialized Q&A for Beta Alpha Psi: Nu Sigma Chapter
- Secure API key management
- Persistent chat history
- Professional and accurate responses

## Contributing

To contribute to the knowledge base or improve the bot:

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
