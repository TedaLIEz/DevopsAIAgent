import argparse
from langchain.prompts import ChatPromptTemplate 
from langchain_deepseek import ChatDeepSeek
import os
from dotenv import load_dotenv
from log_reader import read_log_file
from pydantic import BaseModel, Field 
from langchain_core.output_parsers.openai_tools import PydanticToolsParser

load_dotenv()

endpoint = os.getenv('ENDPOINT')
api_key = os.getenv('API_KEY')
model = os.getenv('MODEL')


class Tagging(BaseModel):
    """Tagging text with a label."""
    status: str = Field(description="The status of the tagging log. Select from 'success', 'failure', 'pending', 'timeout', or 'unknown' if user input is not a log.")
    error_info: str = Field(description="The error information if the status is 'failure'. Please provide the error message in English.")

class Agent:
    def __init__(self):
        self.__binding_functions = [Tagging]
        self.__model = ChatDeepSeek(temperature=0.0, api_key=api_key,  \
                              api_base=endpoint, \
                              model=model).bind_tools(self.__binding_functions)

    def analysis(self, message):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a log analysis assistant. Please analysis the log."),
            ("user", "{input}")
        ])
        tagging_chain = prompt | self.__model | PydanticToolsParser(tools=self.__binding_functions)
        return tagging_chain.invoke({"input": message})

    def check_log(self, file_path):
        content = read_log_file(file_path)
        return self.analysis(content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Log analysis tool")
    parser.add_argument("log_file", type=str, help="Path to the log file")
    args = parser.parse_args()
    agent = Agent()
    try:
        result = agent.check_log(args.log_file)
        print(result)
    except Exception as e:
        print(f"Error: {e}")
