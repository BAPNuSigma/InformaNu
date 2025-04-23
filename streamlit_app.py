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

    # Process common queries directly
    response = None
    query = prompt.lower()
    
    if 'next meeting' in query or ('when' in query and 'meeting' in query):
        response = kb_handler.get_next_meeting()
    elif 'candidate' in query and 'requirement' in query:
        requirements = kb_handler.knowledge_base.get('membership_types_and_requirements', {}).get('markdown', '')
        candidate_section = None
        lines = requirements.split('\n')
        in_section = False
        section_content = []
        
        for line in lines:
            if '## Candidate Eligibility' in line or '## Candidacy Requirements' in line:
                in_section = True
            elif in_section and line.startswith('##'):
                in_section = False
            elif in_section and line.strip():
                section_content.append(line)
        
        if section_content:
            response = '\n'.join(section_content)
    elif 'gpa' in query and ('requirement' in query or 'need' in query or 'join' in query):
        response = kb_handler.get_gpa_requirement()
    elif 'attendance' in query and 'requirement' in query:
        response = kb_handler.get_attendance_requirements()
    elif 'checklist' in query:
        response = kb_handler.get_membership_checklist()
    elif 'reflection' in query and 'paper' in query:
        response = kb_handler.get_reflection_papers_policy()
    elif 'tutoring' in query and 'schedule' in query:
        response = kb_handler.get_tutoring_schedule()
    
    if not response:
        # Search the knowledge base for relevant information
        matches = kb_handler.search_knowledge_base(query)
        if matches:
            response = matches[0]['content']
    
    if response:
        # Clean up the response
        response = response.replace('  - ', '- ').strip()
        # Display the response
        with st.chat_message("assistant"):
            st.markdown(response)
        # Store the response
        st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        # If no direct match found, use OpenAI to generate a response
        client = OpenAI()
        messages = [
            {"role": "system", "content": "You are a helpful assistant for Beta Alpha Psi: Nu Sigma Chapter. If you don't know the specific answer from the knowledge base, politely say so and suggest contacting chapter leadership for the most accurate information."}
        ]
        messages.extend([{"role": m["role"], "content": m["content"]} for m in st.session_state.messages])
        
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stream=True,
        )
        
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
