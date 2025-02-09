from langchain_openai import AzureChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
api_key = os.getenv('AZURE_OPENAI_API_KEY')
api_version = os.getenv('AZURE_OPENAI_VERSION')
deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT')


class Agent:
    def __init__(self):
        self.__chat = AzureChatOpenAI(temperature=0.0, api_key=api_key,  \
                                    api_version=api_version, \
                                    azure_deployment=deployment_name, \
                                    azure_endpoint=endpoint)

    def respond(self, message):
        from langchain_core.messages import HumanMessage, SystemMessage
        messages = [
            SystemMessage("You are helpful but sassy assistant."),
            HumanMessage(message),
        ]

        return self.__chat.invoke(messages)


if __name__ == '__main__':
    agent = Agent()
    print(agent.respond('Hello, how are you?'))