import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template
import gspread
from google.oauth2.service_account import Credentials
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to get OpenAI API key
def get_openai_api_key():
    try:
        # First try to get from Streamlit secrets
        if "openai" in st.secrets and "api_key" in st.secrets["openai"]:
            return st.secrets["openai"]["api_key"]
        # Then try environment variable
        return os.getenv("OPENAI_API_KEY")
    except Exception as e:
        logger.error(f"Error getting OpenAI API key: {e}")
        return None

# Function to convert dictionary to string
def dict_to_string(d):
    try:
        items = [f'{k}: {v}' for k, v in d.items()]
        return '{ ' + ', '.join(items) + ' }'
    except Exception as e:
        logger.error(f"Error converting dictionary to string: {e}")
        return str(d)

# Function to generate PDF
def generate_pdf(data, filename):
    try:
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter

        # Define a title
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, height - 40, "Updated Schedule")

        # Add data to PDF
        y = height - 70
        c.setFont("Helvetica", 10)
        for entry in data:
            entry_str = dict_to_string(entry)
            c.drawString(30, y, entry_str)
            y -= 15  # Move to next line
            if y < 40:  # Check if the current page is full
                c.showPage()
                c.setFont("Helvetica", 10)
                y = height - 40

        c.save()
        logger.info(f"PDF generated successfully: {filename}")
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        st.error(f"Error generating PDF: {e}")

# Function to extract text from PDFs
def get_pdf_text(pdf_paths):
    text = ""
    for pdf_path in pdf_paths:
        try:
            pdf_reader = PdfReader(pdf_path)
            for page in pdf_reader.pages:
                text += page.extract_text()
        except Exception as e:
            logger.error(f"Error reading PDF {pdf_path}: {e}")
            st.error(f"Error reading PDF {pdf_path}: {e}")
    return text

# Function to split text into chunks
def get_text_chunks(text):
    try:
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        return chunks
    except Exception as e:
        logger.error(f"Error splitting text: {e}")
        st.error(f"Error splitting text: {e}")
        return []

# Function to create vector store from text chunks
def get_vectorstore(text_chunks):
    try:
        openai_api_key = get_openai_api_key()
        if not openai_api_key:
            st.error("OpenAI API key not found. Please check your configuration.")
            return None
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
        return vectorstore
    except Exception as e:
        logger.error(f"Error creating vector store: {e}")
        st.error(f"Error creating vector store: {e}")
        return None

# Function to create conversation chain
def get_conversation_chain(vectorstore):
    try:
        openai_api_key = get_openai_api_key()
        if not openai_api_key:
            st.error("OpenAI API key not found. Please check your configuration.")
            return None
        llm = ChatOpenAI(
            api_key=openai_api_key,
            temperature=0.7,
            model_name="gpt-3.5-turbo"
        )

        memory = ConversationBufferMemory(
            memory_key='chat_history',
            return_messages=True,
            output_key='answer'
        )
        
        # Add a personality to the bot by setting an initial system message
        initial_message = {
            "role": "system",
            "content": "You are BAP-GPT, an expert on national and chapter-specific policies with a friendly and helpful personality. Always provide clear, concise, and accurate information using only the information in the provided texts to answer questions. If the text does not provide answers to my questions then state -Apologies, I'm not trained on that information just yet-. Never make up any information and never give information on anything harmful or not business appropriate."
        }
        memory.chat_memory.add_user_message(initial_message["content"])
        
        conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            ),
            memory=memory,
            return_source_documents=True
        )
        return conversation_chain
    except Exception as e:
        logger.error(f"Error creating conversation chain: {e}")
        st.error(f"Error creating conversation chain: {e}")
        return None

# Function to handle user input
def handle_userinput(user_question):
    try:
        if st.session_state.conversation is None:
            st.error("Please wait while the system initializes...")
            return

        response = st.session_state.conversation({'question': user_question})
        st.session_state.chat_history = response['chat_history']

        # Skip the first message (system message)
        skip_first_message = True

        for i, message in enumerate(st.session_state.chat_history):
            if skip_first_message:
                skip_first_message = False
                continue
            if i % 2 == 0:
                st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
            else:
                st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"Error handling user input: {e}")
        st.error(f"Error handling user input: {e}")

# Function to process PDFs
def process_pdfs(pdf_paths):
    try:
        # get pdf text
        raw_text = get_pdf_text(pdf_paths)
        if not raw_text:
            st.error("No text could be extracted from the PDFs")
            return

        # get the text chunks
        text_chunks = get_text_chunks(raw_text)
        if not text_chunks:
            st.error("No text chunks could be created")
            return

        # create vector store
        vectorstore = get_vectorstore(text_chunks)
        if vectorstore is None:
            st.error("Could not create vector store")
            return

        # create conversation chain
        st.session_state.conversation = get_conversation_chain(vectorstore)
        if st.session_state.conversation is None:
            st.error("Could not create conversation chain")
            return

        st.success("PDFs processed successfully!")
    except Exception as e:
        logger.error(f"Error processing PDFs: {e}")
        st.error(f"Error processing PDFs: {e}")

def main():
    try:
        load_dotenv()
        st.set_page_config(page_title="BAP-GPT", page_icon=":mag:")
        st.write(css, unsafe_allow_html=True)

        if "conversation" not in st.session_state:
            st.session_state.conversation = None
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = None

        # Create documents directory if it doesn't exist
        documents_folder = 'documents'
        if not os.path.exists(documents_folder):
            os.makedirs(documents_folder)
            st.info(f"Created {documents_folder} directory")

        # Generate PDF from Google Sheets data
        try:
            credentials = st.secrets["google_credentials"]
            scopes = ["https://www.googleapis.com/auth/spreadsheets"]
            creds = Credentials.from_service_account_info(credentials, scopes=scopes)
            client = gspread.authorize(creds)

            # Enter Sheet ID here!!!
            sheet_id = "1hQgAn1Wg4Cz9qcNg04gJdQqrjuMZEjjJrXwK3dIi_Og"
            sheet = client.open_by_key(sheet_id)
            worksheetSchedule = sheet.get_worksheet(0)
            schedulelist = worksheetSchedule.get_all_records()

            # Generate PDF in the 'documents' folder, overwriting any existing file
            output_path = os.path.join(documents_folder, "schedule_list_report.pdf")
            generate_pdf(schedulelist, output_path)

            st.write(f"PDF generated and saved to {output_path}")
        except Exception as e:
            logger.error(f"Error with Google Sheets integration: {e}")
            st.error(f"Error with Google Sheets integration: {e}")

        # Automatically process PDFs in 'documents' folder on page load
        pdf_paths = [os.path.join(documents_folder, filename) for filename in os.listdir(documents_folder) if filename.endswith('.pdf')]
        
        if pdf_paths and st.session_state.conversation is None:
            with st.spinner("Processing PDFs..."):
                process_pdfs(pdf_paths)
        elif not pdf_paths:
            st.warning("No PDF files found in the documents directory. Please ensure PDFs are present.")

        st.header("Chat with BAP-GPT :mag:")
        user_question = st.text_input("Ask a question about national or chapter specific policies")
        if user_question:
            handle_userinput(user_question)

    except Exception as e:
        logger.error(f"Error in main function: {e}")
        st.error(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()
