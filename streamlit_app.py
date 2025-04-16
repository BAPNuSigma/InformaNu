import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
acknowledge the limitation and suggest where the user might find more information."""

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

    # Generate a response using the OpenAI API
    try:
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        # Stream the response to the chat
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.stop()
