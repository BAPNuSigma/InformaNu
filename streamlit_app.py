import streamlit as st
from openai import OpenAI
from knowledge_base_handler import KnowledgeBaseHandler
from datetime import datetime, timedelta
import re
import pandas as pd

# Initialize knowledge base handler
kb_handler = KnowledgeBaseHandler()

# Debug: Print loaded knowledge base files and their headers
print("Loaded knowledge base files:")
for kb_name, kb_content in kb_handler.knowledge_base.items():
    print(f"- {kb_name}: {len(kb_content['markdown'].splitlines())} lines")
    # Print first few lines for preview
    print("  Preview:", '\n'.join(kb_content['markdown'].splitlines()[:5]))

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

def extract_section(content, header):
    # Try both Markdown and plain text headers
    header_plain = header.lstrip('#').strip()
    lines = content.split('\n')
    section = []
    in_section = False
    header_level = header.count('#') if header.startswith('#') else 2  # Default to 2 if not markdown
    for line in lines:
        # Match either markdown or plain text header
        if line.strip().startswith(header) or line.strip().lower() == header_plain.lower():
            in_section = True
            continue
        if in_section:
            # Stop at the next header of the same or higher level (markdown) or next all-caps line (DOCX)
            if (line.strip().startswith('#' * header_level) and not line.strip().startswith(header)) or \
               (line.strip().isupper() and len(line.strip().split()) < 6):
                break
            section.append(line)
    extracted = '\n'.join(section).strip() if section else None
    if header in ['## Member Requirements', 'Member Requirements']:
        print(f"[DEBUG] FINAL Extracted section for '{header}':\n{extracted}")
    return extracted

def extract_excel_section(content, section_name):
    # content is a string with rows like 'Section | Content'
    lines = content.split('\n')
    results = []
    for line in lines:
        if '|' in line:
            section, detail = [x.strip() for x in line.split('|', 1)]
            if section.lower() == section_name.lower():
                results.append(detail)
    return '\n'.join(results) if results else None

def extract_meetings_by_month(content, month):
    # month: int (1=Jan, 2=Feb, ...)
    lines = content.split('\n')
    meetings = []
    i = 0
    while i < len(lines):
        line = lines[i]
        date_match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{2,4})', line)
        if date_match:
            m = int(date_match.group(1))
            if m == month:
                meeting_block = [line]
                j = i + 1
                while j < len(lines) and (lines[j].strip().startswith('-') or lines[j].strip().startswith('  ')):
                    meeting_block.append(lines[j])
                    j += 1
                meetings.append('\n'.join(meeting_block))
        i += 1
    return '\n\n'.join(meetings) if meetings else None

def get_available_model(client, preferred="gpt-4", fallback="gpt-3.5-turbo"):
    """Check if the preferred model is available, otherwise use fallback"""
    try:
        # Try a simple call to check access
        client.chat.completions.create(
            model=preferred,
            messages=[{"role": "system", "content": "ping"}],
            max_tokens=1,
        )
        return preferred
    except Exception as e:
        print(f"Warning: {preferred} not available, falling back to {fallback}. Error: {e}")
        return fallback

# Create a chat input field
if prompt := st.chat_input("Ask me anything about Beta Alpha Psi: Nu Sigma Chapter"):
    # Store and display the current prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process common queries directly
    response = None
    query = prompt.lower()
    print(f"\n[DEBUG] User query: {query}")
    
    if 'next meeting' in query or ('when' in query and 'meeting' in query):
        schedule = kb_handler.knowledge_base.get('spring_2025_schedule', {}).get('markdown', '')
        if schedule:
            response = find_meeting_details(schedule, datetime.now(), look_for_next=True)
            if response:
                response = "The next meeting is:\n" + response
            else:
                response = "I couldn't find any upcoming meetings in the schedule."
        print(f"[DEBUG] Next meeting response: {response}")
    
    elif any(phrase in query for phrase in ["today's meeting", "this week's meeting", "current meeting"]):
        schedule = kb_handler.knowledge_base.get('spring_2025_schedule', {}).get('markdown', '')
        if schedule:
            response = find_meeting_details(schedule, datetime.now(), look_for_next=False)
            if response:
                response = "This week's meeting is:\n" + response
            else:
                response = "I couldn't find a meeting scheduled for this week. The schedule might need to be updated, or there might not be a meeting this week. Please check the official chapter communication channels for the most up-to-date information."
        print(f"[DEBUG] This week's meeting response: {response}")

    strict_kb_answered = False
    response = None

    # Strict KB: Member Requirements
    if 'member' in query.lower() and 'requirement' in query.lower():
        for kb_name, kb_content in kb_handler.knowledge_base.items():
            # Try markdown/docx
            section = extract_section(kb_content['markdown'], '## Member Requirements')
            print(f"[DEBUG] Extracted section for '## Member Requirements' from {kb_name}:\n{section}")
            if section:
                response = section
                break
            # Try Excel
            excel_section = extract_excel_section(kb_content['markdown'], 'Member Requirements')
            print(f"[DEBUG] Extracted Excel section for 'Member Requirements' from {kb_name}:\n{excel_section}")
            if excel_section:
                response = '## Member Requirements\n' + excel_section
                break
        if not response:
            response = "I couldn't find the member requirements in our knowledge base. Please contact chapter leadership."
        strict_kb_answered = True

    # Strict KB: Candidate Requirements
    elif 'candidate' in query.lower() and 'requirement' in query.lower():
        for kb_name, kb_content in kb_handler.knowledge_base.items():
            eligibility = extract_section(kb_content['markdown'], '## Candidate Eligibility')
            candidacy = extract_section(kb_content['markdown'], '## Candidacy Requirements')
            excel_elig = extract_excel_section(kb_content['markdown'], 'Candidate Eligibility')
            excel_cand = extract_excel_section(kb_content['markdown'], 'Candidacy Requirements')
            print(f"[DEBUG] Extracted eligibility: {eligibility}\nCandidacy: {candidacy}\nExcel eligibility: {excel_elig}\nExcel candidacy: {excel_cand}")
            if eligibility or candidacy or excel_elig or excel_cand:
                response = ''
                if eligibility:
                    response += eligibility + '\n\n'
                if candidacy:
                    response += candidacy + '\n\n'
                if excel_elig:
                    response += '## Candidate Eligibility\n' + excel_elig + '\n\n'
                if excel_cand:
                    response += '## Candidacy Requirements\n' + excel_cand
                break
        if not response or not response.strip():
            response = "I couldn't find the candidacy requirements in our knowledge base. Please contact chapter leadership."
        strict_kb_answered = True

    # Strict KB: Meeting Schedule
    elif 'meeting schedule' in query.lower() or 'schedule for this semester' in query.lower():
        for kb_name, kb_content in kb_handler.knowledge_base.items():
            section = extract_section(kb_content['markdown'], '# Spring 2025 Meeting Schedule')
            print(f"[DEBUG] Extracted section for '# Spring 2025 Meeting Schedule' from {kb_name}:\n{section}")
            if section:
                response = section
                break
        if not response:
            response = "I couldn't find the meeting schedule in our knowledge base. Please contact chapter leadership."
        strict_kb_answered = True

    # Strict KB: Month-based meetings
    else:
        month_map = {'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6, 'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12}
        for month_name, month_num in month_map.items():
            if month_name in query.lower():
                for kb_name, kb_content in kb_handler.knowledge_base.items():
                    meetings = extract_meetings_by_month(kb_content['markdown'], month_num)
                    print(f"[DEBUG] Extracted meetings for {month_name} from {kb_name}:\n{meetings}")
                    if meetings:
                        response = meetings
                        break
                if not response:
                    response = f"I couldn't find any meetings for {month_name.capitalize()} in our knowledge base. Please contact chapter leadership."
                strict_kb_answered = True
                break

    # Display strict KB answer if found
    if strict_kb_answered:
        with st.chat_message("assistant"):
            st.markdown(response.strip())
        st.session_state.messages.append({"role": "assistant", "content": response.strip()})
    else:
        # Fallback: LLM for other questions
        if not response:
            matches = kb_handler.search_knowledge_base(query)
            relevant_context = ""
            if matches:
                relevant_context = "\n\n".join([match['content'] for match in matches[:3]])
            print(f"[DEBUG] Relevant context for LLM:\n{relevant_context}")
            if relevant_context or len(st.session_state.messages) > 0:
                system_prompt = """You are InformaNu, the official Q&A assistant for Beta Alpha Psi: Nu Sigma Chapter. 
Your primary role is to provide accurate information about chapter requirements, events, and policies.

IMPORTANT RULES:
1. ONLY use information from the provided knowledge base
2. If the information is not in the knowledge base, say \"I don't have that information in my knowledge base. Please contact chapter leadership.\"
3. DO NOT make assumptions or provide information not explicitly stated in the knowledge base
4. For requirements and schedule questions, ONLY use the exact content from the knowledge base
5. Be clear and specific about requirements and deadlines
6. Maintain a professional but friendly tone
7. For time-sensitive information, remind users to verify through official channels

Here is the relevant information from our knowledge base:

{relevant_context}
"""
                client = OpenAI()
                last_msgs = []
                if len(st.session_state.messages) >= 2:
                    last_msgs = st.session_state.messages[-2:]
                else:
                    last_msgs = st.session_state.messages[-1:]
                messages = [
                    {"role": "system", "content": system_prompt.format(relevant_context=relevant_context)}
                ]
                messages.extend([{"role": m["role"], "content": m["content"]} for m in last_msgs])
                
                # Get available model
                model = get_available_model(client)
                print(f"[DEBUG] Using model: {model}")
                print(f"[DEBUG] Messages sent to LLM:\n{messages}")
                
                stream = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.3,  # Lowered temperature for more deterministic responses
                    stream=True,
                )
                with st.chat_message("assistant"):
                    response = st.write_stream(stream)
                st.session_state.messages.append({"role": "assistant", "content": response})
            else:
                with st.chat_message("assistant"):
                    response = ("I apologize, but I couldn't find specific information about that in my knowledge base. "
                              "For the most accurate and up-to-date information, please contact chapter leadership directly.")
                    st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

# After loading the knowledge base, print the loaded keys
print("Loaded knowledge base keys:", list(kb_handler.knowledge_base.keys()))
