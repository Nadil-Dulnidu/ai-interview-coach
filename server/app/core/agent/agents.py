from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from app.core.llm.llm import get_openai_model
from app.core.agent.model.req_gathring_model import ReqGathringModel
from app.core.agent.prompt.req_gathering import REQ_GATHERING_PROMPT
from langchain.tools import BaseTool
from typing import Callable, Any, Sequence

open_ai_model = get_openai_model()


class Agent:
    def __init__(
        self,
        model: ChatOpenAI | None = None,
        name: str | None = None,
        tools: Sequence[BaseTool | Callable | dict[str, Any]] | None = None,
        prompt: str | None = None,
        response_format: BaseModel | None = None,
    ):
        self.name = name
        self.response_format = response_format
        self.model = model
        self.tools = tools
        self.prompt = prompt

    def create_agent(self):
        return create_agent(
            model=self.model,
            tools=self.tools,
            response_format=ToolStrategy(self.response_format),
            system_prompt=self.prompt,
            name=self.name,
        )


def get_req_gathring_agent():
    return Agent(
        model=open_ai_model,
        name="requirement gathring agent",
        tools=[],
        prompt=REQ_GATHERING_PROMPT,
        response_format=ReqGathringModel,
    ).create_agent()


# if __name__ == "__main__":
#     agent = get_req_gathring_agent()
#     response = agent.invoke(
#         {
#             "messages": [
#                 {
#                     "role": "user",
#                     "content": "I want to apply for a job as a software engineer",
#                 }
#             ]
#         }
#     )

#     print(response["messages"])
