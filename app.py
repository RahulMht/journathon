import chainlit as cl
from dotenv import load_dotenv
load_dotenv()
import warnings
import google.generativeai as genai
import os
from pathlib import Path as p
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
warnings.filterwarnings("ignore")

# restart python kernal if issues with langchain import.

genai.configure(api_key=os.environ.get("google_api_key"))
"""### In Context Information Retreival
"""
model = ChatGoogleGenerativeAI(model="gemini-pro", temperature = 0.2, safety_settings= None)

prompt_template = """Your are a helpful NEWS checker specializing in NEWS checking. User will provide NEWS. If the NEWS provided is meaningful and is true based on the given facts, answer "Yes!" and return the piece of fact, "No!" if false also give the appropriate reason to support your answer based on the provided fact. The NEWS maynot always be in fact, In that case answer "inconclusive". \n\n
                    facts: \n {context}?\n
                    NEWS: \n {information} \n
                    Answer:
                  """

prompt = PromptTemplate(
    template=prompt_template, input_variables=["context", "information"]
)

stuff_chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

"""### Extract text from the PDF"""

# pdf_loader = PyPDFLoader(r'C:\Users\DELL\Desktop\Newspaper.pdf')
# pages = pdf_loader.load_and_split()
# context = "\n\n".join(str(p.page_content) for p in pages)

'''Extract text from folder of pdfs and combine them into a single string.'''
folder_path = p(r"D:\Journathon\data")
context = ""
for filename in os.listdir(folder_path):
    if filename.endswith(".pdf"):
        file_path = os.path.join(folder_path, filename)
        try:
            pdf_loader = PyPDFLoader(file_path)
            pages = pdf_loader.load_and_split()
            context = "\n\n".join(str(p.page_content) for p in pages)
        except :
            print(f"Error reading PDF '{filename}")

text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
texts = text_splitter.split_text(context)

# texts

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

vector_index = Chroma.from_texts(texts, embeddings).as_retriever()


@cl.on_message
async def main(message: cl.Message):
    docs = vector_index.get_relevant_documents(message.content)

    stuff_answer = stuff_chain(
        {"input_documents": docs, "information": message.content}, return_only_outputs=True
    )

    # Access the text content from the dictionary
    text = stuff_answer['output_text']
    await cl.Message(
        content=text,
    ).send()
    sources = ""
    for doc in docs[:6]:
        sources += doc.page_content + "\n\n"
    
    await cl.Message(
        content= f"Source:{sources}",
    ).send()


