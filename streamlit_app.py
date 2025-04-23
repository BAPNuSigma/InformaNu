import streamlit as st
from openai import OpenAI
from knowledge_base_handler import KnowledgeBaseHandler

# Initialize knowledge base handler
kb_handler = KnowledgeBaseHandler()

# Show title and description
st.title("InformaNu")
st.write(
    "Welcome to InformaNu: Beta Alpha Psi - Nu Sigma Chapter Q&A Bot! "
    "Ask me anything about our chapter, events, requirements, or history."
)

# Create a session state variable to store the chat messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display the existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Create a chat input field
if prompt := st.chat_input("Ask me anything about Beta Alpha Psi: Nu Sigma Chapter"):
    # Store and display the current prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Search the knowledge base for relevant information
    matches = kb_handler.search_knowledge_base(prompt.lower())
    
    if matches:
        # Format the response using the most relevant match
        response = matches[0]['content']
        
        # Display the response
        with st.chat_message("assistant"):
            st.markdown(response)
            
        # Store the response
        st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        # If no direct match found, use OpenAI to generate a response
        client = OpenAI()
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
