"""
Interview Coach Graph Builder.

This module contains the main graph builder class that orchestrates the
interview coach workflow by connecting nodes and defining transitions.
"""

import logging
from typing import Optional

from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.base import BaseCheckpointSaver

from app.core.graph.state import InterviewCoachState
from app.core.graph.nodes import (
    RequirementGatheringNode,
    AskMoreInfoNode,
    InterviewStrategyNode,
    ContinueInterviewNode,
    InterviewerNode,
    QuestionMakerNode,
    EvaluationNode,
)


logger = logging.getLogger(__name__)


class InterviewCoachGraphBuilder:
    """
    Builds and compiles the Interview Coach workflow graph.

    This class is responsible for:
    1. Creating node instances with their dependencies
    2. Adding nodes to the graph
    3. Defining edges and conditional routing
    4. Compiling the graph with checkpointing

    Attributes:
        state_graph (StateGraph): The underlying LangGraph state graph.
        checkpointer (BaseCheckpointSaver): Checkpointer for conversation persistence.
        nodes (dict): Dictionary of initialized node instances.
    """

    def __init__(
        self,
        req_gathering_agent,
        interview_strategy_agent,
        question_maker_agent,
        interviewer_agent,
        evaluation_agent,
        checkpointer: Optional[BaseCheckpointSaver] = None,
    ):
        """
        Initialize the graph builder.

        Args:
            req_gathering_agent: The agent for requirement gathering.
            checkpointer: Optional checkpointer for state persistence.
                         Defaults to InMemorySaver if not provided.
        """
        self.state_graph = StateGraph(InterviewCoachState)
        self.checkpointer = checkpointer or InMemorySaver()

        # Initialize nodes with their dependencies
        self.nodes = {
            "req_gathering": RequirementGatheringNode(req_gathering_agent),
            "ask_more_info": AskMoreInfoNode(),
            "interview_strategy": InterviewStrategyNode(interview_strategy_agent),
            "question_maker": QuestionMakerNode(question_maker_agent),
            "interviewer": InterviewerNode(interviewer_agent),
            "continue_interview": ContinueInterviewNode(),
            "evaluation": EvaluationNode(evaluation_agent),
        }

        logger.info(
            "InterviewCoachGraphBuilder initialized with nodes: %s",
            list(self.nodes.keys()),
        )

    def _add_nodes(self) -> None:
        """Add all nodes to the state graph."""
        for node_name, node_instance in self.nodes.items():
            self.state_graph.add_node(node_name, node_instance.execute)
            logger.debug(f"Added node: {node_name}")

    def _add_edges(self) -> None:
        """
        Define edges and transitions between nodes.

        """
        # Start with requirement gathering
        self.state_graph.add_edge(START, "req_gathering")

        # Conditional routing based on requirements completion
        self.state_graph.add_conditional_edges(
            "req_gathering",
            self._should_ask_more_info,
            {
                True: "ask_more_info",  # More info needed
                False: "interview_strategy",  # Requirements complete
            },
        )

        # Loop back from ask_more_info to requirement gathering
        self.state_graph.add_edge("ask_more_info", "req_gathering")

        # Add edge from interview_strategy to question_maker
        self.state_graph.add_edge("interview_strategy", "question_maker")

        # Add edge from question_maker to interviewer
        self.state_graph.add_edge("question_maker", "interviewer")

        self.state_graph.add_conditional_edges(
            "interviewer",
            self._should_continue_interview,
            {
                True: "continue_interview",  # More info needed
                False: "evaluation",  # Requirements complete
            },
        )

        self.state_graph.add_edge("continue_interview", "interviewer")

        self.state_graph.add_edge("evaluation", END)

        logger.debug("Graph edges configured")

    def _should_ask_more_info(self, state: InterviewCoachState) -> bool:
        """
        Determine if we need to ask for more information.

        This is a routing function used in conditional edges.

        Args:
            state: Current state of the workflow.

        Returns:
            True if more information is needed, False otherwise.
        """
        needs_more_info = not state.get("requirements_completed", False)
        logger.debug(f"Should ask more info: {needs_more_info}")
        return needs_more_info

    def _should_continue_interview(self, state: InterviewCoachState) -> bool:
        """
        Determine if we need to continue the interview.

        This is a routing function used in conditional edges.

        Args:
            state: Current state of the workflow.

        Returns:
            True if more information is needed, False otherwise.
        """
        needs_more_info = not state.get("is_interview_completed", False)
        logger.debug(f"Should continue interview: {needs_more_info}")
        return needs_more_info

    def build(self) -> StateGraph:
        """
        Build and compile the complete graph.

        This method:
        1. Adds all nodes to the graph
        2. Defines edges and routing logic
        3. Compiles the graph with checkpointing

        Returns:
            The compiled StateGraph ready for execution.
        """
        logger.info("Building Interview Coach graph...")

        self._add_nodes()
        self._add_edges()

        compiled_graph = self.state_graph.compile(checkpointer=self.checkpointer)

        logger.info("Interview Coach graph built successfully")
        return compiled_graph
