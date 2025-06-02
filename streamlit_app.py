import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
import glob
from PyPDF2 import PdfReader
from docx import Document

# Load environment variables
load_dotenv()

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file."""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF {file_path}: {str(e)}")
        return ""

def extract_text_from_docx(file_path):
    """Extract text from a DOCX file."""
    try:
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading DOCX {file_path}: {str(e)}")
        return ""

def load_knowledge_base():
    """Load all files from the knowledge base directory."""
    knowledge_base = {}
    
    # Process all files in the knowledge base directory
    for file_path in glob.glob("knowledge_base/*.*"):
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext == '.md':
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
            elif file_ext == '.pdf':
                content = extract_text_from_pdf(file_path)
            elif file_ext == '.docx':
                content = extract_text_from_docx(file_path)
            else:
                st.warning(f"Unsupported file type: {file_ext} for {file_name}")
                continue
                
            if content.strip():  # Only add non-empty content
                knowledge_base[file_name] = content
                
        except Exception as e:
            st.error(f"Error processing {file_name}: {str(e)}")
            continue
            
    return knowledge_base

def get_relevant_context(query, knowledge_base):
    """Get relevant context from knowledge base based on the query."""
    # For now, we'll return all context, but this could be improved with semantic search
    context = "\n\n".join(knowledge_base.values())
    return context

# Load knowledge base
KNOWLEDGE_BASE = load_knowledge_base()

# Set page config
st.set_page_config(
    page_title="Beta Alpha Psi: Nu Sigma Chapter Q&A Bot",
    page_icon="🎓",
    layout="wide"
)

# Show title and description
st.title("InformaNu")
st.write(
    "Welcome to InformaNu: Beta Alpha Psi - Nu Sigma Chapter Q&A Bot! "
    "Ask me anything about our chapter, events, requirements, or history."
)

# Get API key from environment variables or secrets.toml
openai_api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

if not openai_api_key:
    st.error("OpenAI API key not found. Please check your environment variables or secrets.toml file.")
    st.stop()

# Create an OpenAI client
client = OpenAI(api_key=openai_api_key)

# System prompt for the assistant
SYSTEM_PROMPT = """You are a helpful assistant for Beta Alpha Psi: Nu Sigma Chapter. 
Your role is to provide accurate information about the chapter, including:
- Chapter history and achievements
- Membership requirements and benefits
- Event information and schedules
- Professional development opportunities
- Chapter leadership and structure
- Academic requirements and standards

Always be professional, friendly, and accurate in your responses. If you're unsure about something, 
acknowledge the limitation and suggest where the user might find more information.

Use the provided context from the knowledge base to answer questions accurately. If the information
is not in the context, acknowledge that you don't have that specific information."""

# Create a session state variable to store the chat messages
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# Display the existing chat messages
for message in st.session_state.messages:
    if message["role"] != "system":  # Don't display system messages
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Create a chat input field
if prompt := st.chat_input("Ask me anything about Beta Alpha Psi: Nu Sigma Chapter..."):
    # Store and display the current prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get relevant context from knowledge base
    context = get_relevant_context(prompt, KNOWLEDGE_BASE)
    
    # Add context to the messages
    messages_with_context = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Context from knowledge base:\n{context}\n\nUser question: {prompt}"}
    ]

    # Generate a response using the OpenAI API
    try:
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages_with_context,
            stream=True,
        )

        # Stream the response to the chat
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.stop()
