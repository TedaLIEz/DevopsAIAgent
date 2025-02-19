"""
This module provides an Agent class for log analysis using the LlamaIndex library.
"""

import argparse
import os
from pydantic import BaseModel, Field
from llama_index.llms.siliconflow import SiliconFlow
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.siliconflow import SiliconFlowEmbedding
from llama_index.core import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('API_KEY')
model = os.getenv('LLM_MODEL')
embedding_model = os.getenv('EMBEDDING_MODEL')


class Tagging(BaseModel):
    """Tagging text with a label."""
    status: str = Field(
        description="The status of the tagging log. \
            Select from 'success', 'error', 'pending', 'timeout', \
            or 'unknown' if user input is not a log.")
    error_info: str = Field(
        description="The error information if the status is 'error'. \
            Please provide the error message in English.")


class Agent:
    """
    Agent class for log analysis using the LlamaIndex library.
    """

    def __init__(self):
        self.__llm = SiliconFlow(
            api_key=api_key, model=model, temperature=0.0).as_structured_llm(Tagging)
        Settings.llm = self.__llm
        # FIXME: AzureOpenAIEmbedding is working better than SiliconFlowEmbedding
        Settings.embed_model = SiliconFlowEmbedding(
            api_key=api_key, model=embedding_model)

    def check_logs(self, file_folder):
        """Check logs in the specified folder."""
        documents = SimpleDirectoryReader(file_folder).load_data()
        index = VectorStoreIndex.from_documents(documents)
        query_engine = index.as_query_engine()
        prompt_tmpl = (
            "Context information is below.\n"
            "---------------------\n"
            "{context_str}\n"
            "---------------------\n"
            "You are an assistant for log analysis. \
                Use the above pieces of retrieved context to analyze the log. \
                Use one sentence maximum and keep the answer concise."
            "Query: {query_str}\n"
            "Answer: "
        )
        new_summary_tmpl = PromptTemplate(prompt_tmpl)
        query_engine.update_prompts(
            {"response_synthesizer:summary_template": new_summary_tmpl}
        )
        question = "Extract any error information from the log. \
            If there is no error, please provide the status of the log."
        rst = query_engine.query(question)
        return rst


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Log analysis tool")
    parser.add_argument("log_folder_path", type=str, help="Log folder path")
    args = parser.parse_args()
    agent = Agent()
    try:
        response = agent.check_logs(args.log_folder_path)
        print(response)
    except Exception as e:
        print(f"Error: {e}")
