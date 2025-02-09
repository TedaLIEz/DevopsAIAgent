from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate 
import os
from dotenv import load_dotenv
from log_reader import read_log_file
from typing import List  
from pydantic import BaseModel, Field 
from langchain_core.utils.function_calling import convert_pydantic_to_openai_function
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser  

load_dotenv()

endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
api_key = os.getenv('AZURE_OPENAI_API_KEY')
api_version = os.getenv('AZURE_OPENAI_VERSION')
deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT')


class Tagging(BaseModel):
    """Tagging text with a label."""
    status: str = Field(description="The status of the tagging log. Select from 'success', 'failure', 'pending', 'timeout'.")
    error_info: str = Field(description="The error information if the status is 'failure'.")

class Agent:
    def __init__(self):
        self.__tagging = convert_pydantic_to_openai_function(Tagging)
        self.__binding_functions = [self.__tagging]
        self.__model = AzureChatOpenAI(temperature=0.0, api_key=api_key,  \
                                       max_tokens=100,
                                       deployment_name=deployment_name, api_version=api_version,  \
                                    azure_endpoint=endpoint).bind(functions=self.__binding_functions, function_call={"name": "Tagging"})

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
        tagging_chain = prompt | self.__model | JsonOutputFunctionsParser()
        return tagging_chain.invoke({"input": content})

