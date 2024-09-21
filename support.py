import os
import pandas as pd
import numpy as np
import langchain
from langchain_openai import OpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chains.qa_with_sources.loading import load_qa_with_sources_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders.pdf import PyPDFLoader
from dotenv import load_dotenv

load_dotenv()

# Specify the path to your PDF file
pdf_path = r"C:\Users\ARTHUR\nlp\End_to_End_NLP_Project\BankVista_ChatBot\bankvista.pdf"

# Initialize the PDF loader
loader = PyPDFLoader(pdf_path)

# Load the document into a list of text chunks (each representing a page or section)
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap = 200
)
# As all_docs is of type documents we can directly use split_documents over split_text in order to get the chunks.
docs = text_splitter.split_documents(documents)
length = len(docs)

llm = OpenAI(temperature=0.6, max_tokens=500)

embeddings = OpenAIEmbeddings()

vectorindex_openai = FAISS.from_documents(docs, embeddings)

llm = OpenAI()

chain = RetrievalQAWithSourcesChain.from_llm(llm=llm, retriever=vectorindex_openai.as_retriever())
