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
    status: str = Field(description="The status of the tagging log. Select from 'success', 'failure', 'pending', 'timeout'.")
    error_info: str = Field(description="The error information if the status is 'failure'. Please provide the error message in English.")

class Agent:
    def __init__(self):
        self.__binding_functions = [Tagging]
        self.__model = ChatDeepSeek(temperature=0.0, api_key=api_key,  \
                              api_base=endpoint, \
                              model=model).bind_tools(self.__binding_functions)

    def respond(self, message):
        from langchain_core.messages import HumanMessage, SystemMessage
        messages = [
            SystemMessage("You are helpful but sassy assistant."),
            HumanMessage(message),
        ]

        return self.__model.invoke(messages)

    def check_log(self, file_path):
        content = read_log_file(file_path)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a log analysis assistant. Please tag the log file."),
            ("user", "{input}")
        ])
        tagging_chain = prompt | self.__model | PydanticToolsParser(tools=self.__binding_functions)
        return tagging_chain.invoke({"input": content})


if __name__ == "__main__":
    agent = Agent()
    file_path = os.path.join(os.getcwd(), "data", "logs", "0_hello-world-job.txt")
    agent.check_log(file_path)
