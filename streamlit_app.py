import streamlit as st
from openai import OpenAI
from knowledge_base_handler import KnowledgeBaseHandler
from datetime import datetime, timedelta

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

def find_meeting_details(schedule, target_date, look_for_next=True):
    """Find meeting details for a specific date or next/current meeting"""
    meetings = []
    current_meeting = None
    lines = schedule.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if '**' in line and '/' in line:  # Look for date entries
            try:
                date_str = line.split('**')[1].split('-')[0].strip()
                if '/' in date_str:
                    date_parts = date_str.split('/')
                    if len(date_parts) == 3:
                        meeting_date = datetime.strptime(date_str, '%m/%d/%y')
                        meeting_details = [line]
                        # Get additional details
                        j = i + 1
                        while j < len(lines) and (lines[j].strip().startswith('-') or lines[j].strip().startswith('  ')):
                            meeting_details.append(lines[j].strip())
                            j += 1
                        meetings.append((meeting_date, meeting_details))
            except Exception:
                pass
        i += 1
    
    if not meetings:
        return None
        
    if look_for_next:
        # Find the next meeting after target_date
        future_meetings = [(date, details) for date, details in meetings if date > target_date]
        if future_meetings:
            return '\n'.join(future_meetings[0][1])
    else:
        # Find the meeting closest to target_date
        closest_meeting = min(meetings, key=lambda x: abs((x[0] - target_date).days))
        # Only return if it's within 3 days of target_date
        if abs((closest_meeting[0] - target_date).days) <= 3:
            return '\n'.join(closest_meeting[1])
    
    return None

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
        schedule = kb_handler.knowledge_base.get('spring_2025_schedule', {}).get('markdown', '')
        if schedule:
            response = find_meeting_details(schedule, datetime.now(), look_for_next=True)
            if response:
                response = "The next meeting is:\n" + response
            else:
                response = "I couldn't find any upcoming meetings in the schedule."
    
    elif any(phrase in query for phrase in ["today's meeting", "this week's meeting", "current meeting"]):
        schedule = kb_handler.knowledge_base.get('spring_2025_schedule', {}).get('markdown', '')
        if schedule:
            response = find_meeting_details(schedule, datetime.now(), look_for_next=False)
            if response:
                response = "This week's meeting is:\n" + response
            else:
                response = "I couldn't find a meeting scheduled for this week. The schedule might need to be updated, or there might not be a meeting this week. Please check the official chapter communication channels for the most up-to-date information."

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
        relevant_context = ""
        
        # Combine multiple relevant matches if available
        if matches:
            relevant_context = "\n\n".join([match['content'] for match in matches[:3]])
        
        # If we have matches or this is a follow-up question, use the LLM
        if relevant_context or len(st.session_state.messages) > 0:
            # Create a comprehensive system prompt
            system_prompt = """You are InformaNu, the official Q&A assistant for Beta Alpha Psi: Nu Sigma Chapter. 
            Your primary role is to provide accurate information about chapter requirements, events, and policies.
            
            When responding:
            1. Always prioritize information from the provided knowledge base
            2. Be clear and specific about requirements and deadlines
            3. If you're unsure about specific details, acknowledge this and suggest contacting chapter leadership
            4. Maintain a professional but friendly tone
            5. For time-sensitive information (like meeting times or deadlines), remind users to verify through official channels
            
            Here is the relevant information from our knowledge base:
            
            {relevant_context}
            """
            
            client = OpenAI()
            messages = [
                {"role": "system", "content": system_prompt.format(relevant_context=relevant_context)}
            ]
            # Add previous conversation context
            messages.extend([{"role": m["role"], "content": m["content"]} for m in st.session_state.messages])
            
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                stream=True,
            )
            
            with st.chat_message("assistant"):
                response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            # No relevant information found
            with st.chat_message("assistant"):
                response = ("I apologize, but I couldn't find specific information about that in my knowledge base. "
                          "For the most accurate and up-to-date information, please contact chapter leadership directly.")
            st.session_state.messages.append({"role": "assistant", "content": response})
