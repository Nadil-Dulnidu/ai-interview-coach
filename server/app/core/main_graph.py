from langgraph.graph import StateGraph, END, START
from app.core.agent.agents import get_req_gathring_agent
from app.core.state import InterviewCoachState
from langgraph.types import interrupt
from langgraph.checkpoint.memory import InMemorySaver
from langchain.messages import HumanMessage
import logging

req_gathring_agent = get_req_gathring_agent()


class MainGraph:
    """
    Orchestrates the stateful workflow of the Interview Coach application using LangGraph.

    This class is responsible for defining and managing the execution logic of the
    interview coaching process. It facilitates transitions between various nodes—such
    as requirement gathering, mock interviewing, and feedback generation—while
    maintaining global state consistency across interactions and handling
    asynchronous interrupts for human-in-the-loop validation.

    Attributes:
        graph (StateGraph): The LangGraph StateGraph instance defining the workflow structure.
        state (InterviewCoachState): The current state object tracking conversation
            history, session metadata, and candidate requirements.

    """

    def __init__(
        self,
        graph=StateGraph(InterviewCoachState),
        checkpointer=InMemorySaver(),
    ):
        self.graph = graph
        self.checkpointer = checkpointer

    def req_gathering_node(self, state: InterviewCoachState) -> InterviewCoachState:
        """
        This node is responsible for gathering the requirements from the user.

        Returns:
            InterviewCoachState: The state after gathering the requirements.
        """

        logging.info("[REQ GATHRING NODE] Gathering requirements NODE started")
        messages = state["messages"]
        print(messages)
        response = req_gathring_agent.invoke({"messages": messages})

        req_gathring_structured_response = response["structured_response"]

        print(req_gathring_structured_response)

        if req_gathring_structured_response.missing_info.question != "":

            result = {
                "messages": state["messages"],
                "requirements": None,
                "requirements_completed": False,
                "intruption_question": req_gathring_structured_response.missing_info.question,
            }
            logging.info(
                "[REQ GATHRING NODE] Gathering requirements NODE ended with missing info"
            )
            return result

        result = {
            "messages": state["messages"],
            "requirements": req_gathring_structured_response.model_dump(),
            "requirements_completed": True,
            "intruption_question": "",
        }

        logging.info("[REQ GATHRING NODE] Gathering requirements NODE ended")

        return result

    def should_ask_more_info_node(self, state: InterviewCoachState) -> bool:
        """
        This node is responsible for checking if the user has provided enough information.

        Returns:
            bool: True if the user has provided enough information, False otherwise.
        """

        logging.info("[SHOULD ASK MORE INFO NODE] Should ask more info NODE started")
        result = not state["requirements_completed"]

        logging.info(
            f"[SHOULD ASK MORE INFO NODE] Should ask more info NODE ended with result: {result}"
        )

        return result

    def ask_more_info_node(self, state: InterviewCoachState) -> InterviewCoachState:
        """
        This node is responsible for asking the user for more information.

        Returns:
            InterviewCoachState: The state after asking the user for more information.
        """
        logging.info("[ASK MORE INFO NODE] Ask more info NODE started")
        if state["intruption_question"] != "":
            logging.info(
                "[ASK MORE INFO NODE] Ask more info NODE ended with intruption question"
            )
            question = state["intruption_question"]
            interrupt(question)

        return state

    def build_graph(self) -> StateGraph:
        """
        This method is responsible for building the graph.
        """
        self.graph.add_node("req_gathring", self.req_gathering_node)
        self.graph.add_node("ask_more_info", self.ask_more_info_node)

        self.graph.add_edge(START, "req_gathring")
        self.graph.add_conditional_edges(
            "req_gathring",
            lambda state: self.should_ask_more_info_node(state),
            {True: "ask_more_info", False: END},
        )

        self.graph.add_edge("ask_more_info", "req_gathring")

        return self.graph.compile(checkpointer=self.checkpointer)


graph = MainGraph()

compiled_graph = graph.build_graph()


if __name__ == "__main__":

    config = {"configurable": {"thread_id": "thread-1"}}
    initial_state = InterviewCoachState(
        messages=[
            HumanMessage(content="I want to apply for a job as a software engineer")
        ],
        requirements=None,
        requirements_completed=False,
        intruption_question="",
    )
    response = compiled_graph.invoke(initial_state, config=config)

    print(response)
