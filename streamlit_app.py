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
        if not response or "couldn't find" in response.lower():
            # Fallback to searching in the schedule
            schedule = kb_handler.knowledge_base.get('spring_2025_schedule', {}).get('markdown', '')
            if schedule:
                from datetime import datetime
                current_date = datetime.now()
                next_meeting = None
                next_meeting_date = None
                
                for line in schedule.split('\n'):
                    if '**' in line and '/' in line:  # Look for date entries
                        try:
                            date_str = line.split('**')[1].split('-')[0].strip()
                            if '/' in date_str:
                                date_parts = date_str.split('/')
                                if len(date_parts) == 3:
                                    meeting_date = datetime.strptime(date_str, '%m/%d/%y')
                                    if meeting_date > current_date:
                                        next_meeting = line
                                        next_meeting_date = meeting_date
                                        break
                        except Exception:
                            continue
                
                if next_meeting:
                    response = f"The next meeting is:\n{next_meeting}"
                    # Get additional details
                    lines = schedule.split('\n')
                    for i, line in enumerate(lines):
                        if next_meeting in line:
                            j = i + 1
                            while j < len(lines) and (lines[j].strip().startswith('-') or lines[j].strip().startswith('  ')):
                                response += f"\n{lines[j].strip()}"
                                j += 1
                            break

    elif 'candidate' in query and 'requirement' in query:
        # Get both eligibility and requirements sections
        content = kb_handler.knowledge_base.get('membership_types_and_requirements', {}).get('markdown', '')
        if content:
            sections = []
            current_section = []
            in_section = False
            
            for line in content.split('\n'):
                if '## Candidate Eligibility' in line or '## Candidacy Requirements' in line:
                    if current_section:
                        sections.append('\n'.join(current_section))
                    current_section = [line]
                    in_section = True
                elif in_section and line.startswith('##'):
                    sections.append('\n'.join(current_section))
                    current_section = []
                    in_section = False
                elif in_section:
                    current_section.append(line)
            
            if current_section:
                sections.append('\n'.join(current_section))
            
            response = '\n\n'.join(sections)

    elif 'gpa' in query and ('requirement' in query or 'need' in query or 'join' in query):
        response = kb_handler.get_gpa_requirement()
        if not response or "couldn't find" in response.lower():
            # Fallback to searching in the requirements
            content = kb_handler.knowledge_base.get('membership_types_and_requirements', {}).get('markdown', '')
            if content:
                lines = content.split('\n')
                gpa_section = []
                in_gpa = False
                for line in lines:
                    if 'GPA Requirements:' in line:
                        in_gpa = True
                        gpa_section.append(line)
                    elif in_gpa and line.strip() and not line.startswith('#'):
                        gpa_section.append(line)
                    elif in_gpa and line.startswith('#'):
                        break
                if gpa_section:
                    response = '\n'.join(gpa_section)

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
        response = response.strip()
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
