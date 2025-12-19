"""
This module provides thread-safe, singleton-based agent creation and management
with comprehensive error handling, logging, and retry mechanisms.
"""

import logging
import threading
from typing import Any, Callable, Optional, Sequence

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_openai import ChatOpenAI
from langchain.tools import BaseTool
from pydantic import BaseModel

from app.core.llm.openai_llm import get_openai_model
from app.core.llm.genai_llm import get_genai_model
from app.core.llm.openai_resoning_llm import get_openai_reasoning_model
from app.core.agent.model.req_gathring_model import ReqGathringModel
from app.core.agent.prompt.req_gathering import REQ_GATHERING_PROMPT
from app.core.agent.prompt.interview_strategy import INTERVIEW_STRATEGY_PROMPT
from app.core.agent.prompt.interviewer import INTERVIEWER_PROMPT
from app.core.agent.prompt.question_maker import QUESTION_MAKER_PROMPT
from app.core.agent.prompt.evaluation import EVALUATION_PROMPT
from app.core.agent.model.interviewer_model import InterviewerModel
from app.core.agent.model.interview_strategy_model import InterviewStrategy
from app.core.agent.model.question_maker_model import QuestionSet
from app.core.agent.model.evalutaion_model import InterviewEvaluation
from app.core.agent.tools import web_search_tool
from app.exceptions.agents_exceptions import (
    AgentInitializationError,
    AgentConfigurationError,
)


# Configure logger for tenacity
logger = logging.getLogger(__name__)


class Agent:
    """
    Agent wrapper class for creating LangChain agents with structured output.

    This class provides a consistent interface for creating agents with
    validation, error handling, and logging.
    """

    def __init__(
        self,
        model: Optional[ChatOpenAI] = None,
        name: Optional[str] = None,
        tools: Optional[Sequence[BaseTool | Callable | dict[str, Any]]] = None,
        prompt: Optional[str] = None,
        response_format: Optional[BaseModel] = None,
    ):
        """
        Initialize an Agent.

        Args:
            model: The language model to use
            name: Agent name for identification
            tools: List of tools available to the agent
            prompt: System prompt for the agent
            response_format: Pydantic model for structured output

        Raises:
            AgentConfigurationError: If required parameters are missing
        """
        self._validate_config(model, name, prompt, response_format)

        self.name = name
        self.response_format = response_format
        self.model = model
        self.tools = tools or []
        self.prompt = prompt

        logger.info(f"Agent '{self.name}' initialized with {len(self.tools)} tools")

    def _validate_config(
        self,
        model: Optional[ChatOpenAI],
        name: Optional[str],
        prompt: Optional[str],
        response_format: Optional[BaseModel],
    ) -> None:
        """Validate agent configuration."""
        if not model:
            raise AgentConfigurationError("Model is required")
        if not name:
            raise AgentConfigurationError("Agent name is required")
        if not prompt:
            raise AgentConfigurationError("System prompt is required")
        if not response_format:
            raise AgentConfigurationError("Response format is required")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    def create_agent(self):
        """
        Create a LangChain agent with the configured settings.

        Returns:
            Configured LangChain agent

        Raises:
            AgentInitializationError: If agent creation fails
        """
        try:
            logger.info(f"Creating agent '{self.name}'")
            agent = create_agent(
                model=self.model,
                tools=self.tools,
                response_format=ToolStrategy(self.response_format),
                system_prompt=self.prompt,
                name=self.name,
            )
            logger.info(f"Agent '{self.name}' created successfully")
            return agent
        except Exception as e:
            logger.error(f"Failed to create agent '{self.name}': {str(e)}")
            raise AgentInitializationError(
                f"Failed to create agent '{self.name}': {str(e)}"
            ) from e


# Thread-safe singleton implementation
class AgentManager:
    """
    Thread-safe singleton manager for agents.

    This class ensures that agents are created only once and shared across
    the application, with proper thread safety.
    """

    _instance = None
    _lock = threading.RLock()  # Use RLock for reentrant locking to prevent deadlocks

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        with self._lock:
            if not self._initialized:
                self._req_gathering_agent = None
                self._interview_strategist_agent = None
                self._interviewer_agent = None
                self._question_maker_agent = None
                self._evaluation_agent = None
                self._openai_model = None
                self._genai_model = None
                self._openai_reasoning_model = None
                self._initialized = True
                logger.info("AgentManager initialized")

    def _get_openai_model(self) -> ChatOpenAI:
        """Lazy-load OpenAI model with error handling."""
        if self._openai_model is None:
            with self._lock:
                if self._openai_model is None:
                    try:
                        logger.info("Initializing OpenAI model")
                        self._openai_model = get_openai_model()
                        logger.info("OpenAI model initialized successfully")
                    except Exception as e:
                        logger.error(f"Failed to initialize OpenAI model: {str(e)}")
                        raise AgentInitializationError(
                            f"Failed to initialize OpenAI model: {str(e)}"
                        ) from e
        return self._openai_model

    def _get_genai_model(self) -> ChatOpenAI:
        """Lazy-load GenAI model with error handling."""
        if self._genai_model is None:
            with self._lock:
                if self._genai_model is None:
                    try:
                        logger.info("Initializing GenAI model")
                        self._genai_model = get_genai_model()
                        logger.info("GenAI model initialized successfully")
                    except Exception as e:
                        logger.error(f"Failed to initialize GenAI model: {str(e)}")
                        raise AgentInitializationError(
                            f"Failed to initialize GenAI model: {str(e)}"
                        ) from e
        return self._genai_model

    def _get_openai_reasoning_model(self) -> ChatOpenAI:
        """Lazy-load OpenAI reasoning model with error handling."""
        if self._openai_reasoning_model is None:
            with self._lock:
                if self._openai_reasoning_model is None:
                    try:
                        logger.info("Initializing OpenAI reasoning model")
                        self._openai_reasoning_model = get_openai_reasoning_model()
                        logger.info("OpenAI reasoning model initialized successfully")
                    except Exception as e:
                        logger.error(
                            f"Failed to initialize OpenAI reasoning model: {str(e)}"
                        )
                        raise AgentInitializationError(
                            f"Failed to initialize OpenAI reasoning model: {str(e)}"
                        ) from e
        return self._openai_reasoning_model

    def get_req_gathering_agent(self):
        """
        Get or create the requirement gathering agent (singleton).

        Returns:
            Configured requirement gathering agent

        Raises:
            AgentInitializationError: If agent creation fails
        """
        if self._req_gathering_agent is None:
            with self._lock:
                if self._req_gathering_agent is None:
                    try:
                        logger.info("Creating requirement gathering agent")
                        self._req_gathering_agent = Agent(
                            model=self._get_openai_model(),
                            name="requirement_gathering_agent",
                            tools=[],
                            prompt=REQ_GATHERING_PROMPT,
                            response_format=ReqGathringModel,
                        ).create_agent()
                        logger.info("Requirement gathering agent created successfully")
                    except Exception as e:
                        logger.error(
                            f"Failed to create requirement gathering agent: {str(e)}"
                        )
                        raise
        return self._req_gathering_agent

    def get_interview_strategist_agent(self):
        """
        Get or create the interview strategist agent (singleton).

        Returns:
            Configured interview strategist agent

        Raises:
            AgentInitializationError: If agent creation fails
        """
        if self._interview_strategist_agent is None:
            with self._lock:
                if self._interview_strategist_agent is None:
                    try:
                        logger.info("Creating interview strategist agent")
                        self._interview_strategist_agent = Agent(
                            model=self._get_genai_model(),
                            name="interview_strategist_agent",
                            tools=[],
                            prompt=INTERVIEW_STRATEGY_PROMPT,
                            response_format=InterviewStrategy,
                        ).create_agent()
                        logger.info("Interview strategist agent created successfully")
                    except Exception as e:
                        logger.error(
                            f"Failed to create interview strategist agent: {str(e)}"
                        )
                        raise
        return self._interview_strategist_agent

    def get_question_maker_agent(self):
        """
        Get or create the question maker agent (singleton).

        Returns:
            Configured question maker agent

        Raises:
            AgentInitializationError: If agent creation fails
        """
        if self._question_maker_agent is None:
            with self._lock:
                if self._question_maker_agent is None:
                    try:
                        logger.info("Creating question maker agent")
                        self._question_maker_agent = Agent(
                            model=self._get_genai_model(),
                            name="question_maker_agent",
                            tools=[web_search_tool],
                            prompt=QUESTION_MAKER_PROMPT,
                            response_format=QuestionSet,
                        ).create_agent()
                        logger.info("Question maker agent created successfully")
                    except Exception as e:
                        logger.error(f"Failed to create question maker agent: {str(e)}")
                        raise
        return self._question_maker_agent

    def get_interviewer_agent(self):
        """
        Get or create the interviewer agent (singleton).

        Returns:
            Configured interviewer agent

        Raises:
            AgentInitializationError: If agent creation fails
        """
        if self._interviewer_agent is None:
            with self._lock:
                if self._interviewer_agent is None:
                    try:
                        logger.info("Creating interviewer agent")
                        self._interviewer_agent = Agent(
                            model=self._get_openai_model(),
                            name="interviewer_agent",
                            tools=[],
                            prompt=INTERVIEWER_PROMPT,
                            response_format=InterviewerModel,
                        ).create_agent()
                        logger.info("Interviewer agent created successfully")
                    except Exception as e:
                        logger.error(f"Failed to create interviewer agent: {str(e)}")
                        raise
        return self._interviewer_agent

    def get_evaluation_agent(self):
        """
        Get or create the evaluation agent (singleton).

        Returns:
            Configured evaluation agent

        Raises:
            AgentInitializationError: If agent creation fails
        """
        if self._evaluation_agent is None:
            with self._lock:
                if self._evaluation_agent is None:
                    try:
                        logger.info("Creating evaluation agent")
                        self._evaluation_agent = Agent(
                            model=self._get_openai_reasoning_model(),
                            name="evaluation_agent",
                            tools=[],
                            prompt=EVALUATION_PROMPT,
                            response_format=InterviewEvaluation,
                        ).create_agent()
                        logger.info("Evaluation agent created successfully")
                    except Exception as e:
                        logger.error(f"Failed to create evaluation agent: {str(e)}")
                        raise
        return self._evaluation_agent

    def reset(self) -> None:
        """
        Reset all agents (useful for testing or reinitialization).

        This will force recreation of all agents on next access.
        """
        with self._lock:
            logger.warning("Resetting all agents")
            self._req_gathering_agent = None
            self._interview_strategist_agent = None
            self._interviewer_agent = None
            self._evaluation_agent = None
            self._question_maker_agent = None
            self._openai_model = None
            self._genai_model = None
            logger.info("All agents reset successfully")


# Global manager instance
_manager = AgentManager()


# Public API functions (backward compatible)
def get_req_gathering_agent():
    """
    Get the requirement gathering agent singleton.

    Returns:
        Configured requirement gathering agent
    """
    return _manager.get_req_gathering_agent()


def get_interview_strategist_agent():
    """
    Get the interview strategist agent singleton.

    Returns:
        Configured interview strategist agent
    """
    return _manager.get_interview_strategist_agent()


def get_question_maker_agent():
    """
    Get the question maker agent singleton.

    Returns:
        Configured question maker agent
    """
    return _manager.get_question_maker_agent()


def get_interviewer_agent():
    """
    Get the interviewer agent singleton.

    Returns:
        Configured interviewer agent
    """
    return _manager.get_interviewer_agent()


def get_evaluation_agent():
    """
    Get the evaluation agent singleton.

    Returns:
        Configured evaluation agent
    """
    return _manager.get_evaluation_agent()


def reset_agents() -> None:
    """
    Reset all agents. Useful for testing or forcing reinitialization.
    """
    _manager.reset()
