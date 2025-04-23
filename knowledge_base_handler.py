import os
import markdown
from pathlib import Path

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
    
    def search_knowledge_base(self, query):
        """Simple search implementation - can be enhanced with better matching"""
        query = query.lower()
        matches = []
        
        for topic, content in self.knowledge_base.items():
            text = content['text'].lower()
            # Check if query terms appear in the content
            if query in text:
                # Find the relevant section
                paragraphs = text.split('\n\n')
                for para in paragraphs:
                    if query in para.lower():
                        matches.append({
                            'topic': topic,
                            'content': para,
                            'relevance': len(query) / len(para)  # Simple relevance score
                        })
        
        # Sort by relevance
        matches.sort(key=lambda x: x['relevance'], reverse=True)
        return matches

    def get_topic_content(self, topic):
        """Get the full content for a specific topic"""
        return self.knowledge_base.get(topic, {}).get('markdown', '') 