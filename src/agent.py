import argparse
import os
from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from langchain_core.runnables import RunnablePassthrough
from langchain_deepseek import ChatDeepSeek
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import AzureOpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv


load_dotenv()

endpoint = os.getenv('ENDPOINT')
api_key = os.getenv('API_KEY')
model = os.getenv('MODEL')


class Tagging(BaseModel):
    """Tagging text with a label."""
    status: str = Field(
        description="The status of the tagging log. Select from 'success', 'error', 'pending', 'timeout', or 'unknown' if user input is not a log.")
    error_info: str = Field(
        description="The error information if the status is 'error'. Please provide the error message in English.")


class Agent:
    def __init__(self):
        self.__binding_functions = [Tagging]
        self.__model = ChatDeepSeek(temperature=0.0, api_key=api_key,
                                    api_base=endpoint,
                                    model=model).bind_tools(self.__binding_functions)
        key = os.getenv('AZURE_OPENAI_API_KEY')
        deployment_name = os.getenv('AZURE_OPENAI_EMBEDDING_MODEL')
        self.__embeddings = AzureOpenAIEmbeddings(
            openai_api_key=key, deployment=deployment_name, chunk_size=2048)

    def __format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def check_logs(self, file_folder):
        loader = DirectoryLoader(
            file_folder, glob="*.txt", show_progress=True, loader_cls=TextLoader)
        data = loader.load()
        # Split
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=0)
        all_splits = text_splitter.split_documents(data)
        # Store splits
        vectorstore = FAISS.from_documents(
            documents=all_splits, embedding=self.__embeddings)
        prompt = ChatPromptTemplate.from_messages([
            ("human", """You are an assistant for log analysis. Use the following pieces of retrieved context to analysis the log. 
                Use one sentences maximum and keep the answer concise.
                    Question: {question} 
                    Context: {context} 
             """)
        ])
        question = "Extract any error information from the log. If there is no error, please provide the status of the log."
        tagging_chain = {
            "context": vectorstore.as_retriever() | self.__format_docs,
            "question": RunnablePassthrough()
        } | prompt | self.__model | PydanticToolsParser(
            tools=self.__binding_functions)
        return tagging_chain.invoke(question)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Log analysis tool")
    parser.add_argument("log_file", type=str, help="Path to the log file")
    args = parser.parse_args()
    agent = Agent()
    try:
        response = agent.check_logs(args.log_file)
        print(response)
    except Exception as e:
        print(f"Error: {e}")
