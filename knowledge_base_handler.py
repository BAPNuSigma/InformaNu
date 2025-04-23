import os
import markdown
from pathlib import Path
from datetime import datetime
import re

class KnowledgeBaseHandler:
    def __init__(self, knowledge_base_dir="knowledge_base"):
        self.knowledge_base_dir = knowledge_base_dir
        self.knowledge_base = {}
        self.load_knowledge_base()
    
    def load_knowledge_base(self):
        """Load all markdown files from the knowledge base directory"""
        if not os.path.exists(self.knowledge_base_dir):
            raise FileNotFoundError(f"Knowledge base directory {self.knowledge_base_dir} not found")
        
        for file_path in Path(self.knowledge_base_dir).glob("*.md"):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Store both markdown and plain text versions
                self.knowledge_base[file_path.stem] = {
                    'markdown': content,
                    'text': markdown.markdown(content)
                }
    
    def get_next_meeting(self):
        """Find the next meeting from the schedule based on current date"""
        schedule = self.knowledge_base.get('spring_2025_schedule', {}).get('markdown', '')
        if not schedule:
            return "I couldn't find the meeting schedule."
        
        current_date = datetime.now()
        next_meeting = None
        next_meeting_date = None

        # Parse the schedule looking for meeting dates
        for line in schedule.split('\n'):
            # Look for date patterns like "1/22/25" or similar
            date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{2,4})', line)
            time_match = re.search(r'(\d{1,2}:\d{2}(?:\s*[AaPp][Mm])?)', line)
            
            if date_match and time_match:
                date_str = date_match.group(1)
                time_str = time_match.group(1)
                
                # Convert to datetime object
                try:
                    # Ensure 4-digit year
                    if len(date_str.split('/')[-1]) == 2:
                        date_str = date_str[:-2] + '20' + date_str[-2:]
                    
                    # Standardize time format
                    if 'PM' in time_str.upper() and not time_str.startswith('12'):
                        hour = int(time_str.split(':')[0]) + 12
                        time_str = f"{hour}:{time_str.split(':')[1]}"
                    time_str = time_str.replace('AM', '').replace('PM', '').strip()
                    
                    meeting_datetime = datetime.strptime(f"{date_str} {time_str}", '%m/%d/%Y %H:%M')
                    
                    # If this meeting is in the future and either we haven't found a next meeting yet
                    # or this one is sooner than our current next meeting
                    if meeting_datetime > current_date and (next_meeting_date is None or meeting_datetime < next_meeting_date):
                        next_meeting = line.strip()
                        next_meeting_date = meeting_datetime
                except ValueError:
                    continue

        if next_meeting:
            # Clean up the meeting information
            next_meeting = re.sub(r'[*-]', '', next_meeting).strip()
            return f"Our next meeting is {next_meeting}"
        else:
            return "I couldn't find any upcoming meetings in the schedule."

    def get_gpa_requirement(self):
        """Get the specific GPA requirement for our chapter"""
        requirements = self.knowledge_base.get('membership_types_and_requirements', {}).get('markdown', '')
        if not requirements:
            return "I couldn't find the GPA requirements."
        
        # Look for GPA requirements section
        gpa_section = None
        for line in requirements.split('\n'):
            if 'GPA Requirements:' in line:
                gpa_section = line
                # Get the next lines that are part of the GPA requirements
                lines = []
                for next_line in requirements.split('\n')[requirements.split('\n').index(line)+1:]:
                    if next_line.strip() and next_line.startswith('  -'):
                        lines.append(next_line.strip())
                    elif not next_line.startswith('  ') and next_line.strip():
                        break
                if lines:
                    return "\n".join(lines).replace('  - ', '')
        
        return "I couldn't find the specific GPA requirements."
    
    def search_knowledge_base(self, query):
        """Enhanced search implementation"""
        query = query.lower()
        
        # Special handling for common queries
        if 'next meeting' in query or 'when' in query and 'meeting' in query:
            return [{'content': self.get_next_meeting(), 'relevance': 1.0}]
        elif 'gpa' in query and ('requirement' in query or 'need' in query or 'join' in query):
            return [{'content': self.get_gpa_requirement(), 'relevance': 1.0}]
        
        # Default search behavior
        matches = []
        for topic, content in self.knowledge_base.items():
            text = content['text'].lower()
            if query in text:
                paragraphs = text.split('\n\n')
                for para in paragraphs:
                    if query in para.lower():
                        matches.append({
                            'topic': topic,
                            'content': para,
                            'relevance': len(query) / len(para)
                        })
        
        matches.sort(key=lambda x: x['relevance'], reverse=True)
        return matches

    def get_topic_content(self, topic):
        """Get the full content for a specific topic"""
        return self.knowledge_base.get(topic, {}).get('markdown', '') 