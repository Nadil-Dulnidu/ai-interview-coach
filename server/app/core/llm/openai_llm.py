"""
Thread-safe OpenAI model management with comprehensive error handling and validation.

This module provides production-ready LLM model initialization with proper
singleton pattern, validation, error handling, and logging.
"""

import logging
import threading
from typing import Optional
from functools import lru_cache

from langchain_openai import ChatOpenAI

from app.config.env_config import get_settings
from app.exceptions.llm_excaptions import LLMConfigurationError, LLMInitializationError


# Configure module logger
logger = logging.getLogger(__name__)


class OpenAIModelManager:
    """
    Thread-safe singleton manager for OpenAI models.

    This class manages OpenAI model instances with proper thread safety,
    validation, and error handling. Supports multiple models with different
    temperatures through a cache.
    """

    _instance = None
    _lock = threading.RLock()

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
                self._models = {}  # Cache for models with different temperatures
                self._settings = None
                self._initialized = True
                logger.info("OpenAIModelManager initialized")

    def _get_settings(self):
        """Lazy-load settings with validation."""
        if self._settings is None:
            with self._lock:
                if self._settings is None:
                    try:
                        logger.info("Loading OpenAI settings")
                        self._settings = get_settings()
                        self._validate_settings()
                        logger.info("OpenAI settings loaded and validated")
                    except Exception as e:
                        logger.error(f"Failed to load settings: {str(e)}")
                        raise LLMConfigurationError(
                            f"Failed to load settings: {str(e)}"
                        ) from e
        return self._settings

    def _validate_settings(self) -> None:
        """
        Validate OpenAI configuration settings.

        Raises:
            LLMConfigurationError: If required settings are missing or invalid
        """
        if not self._settings.OPENAI_API_KEY:
            raise LLMConfigurationError("OPENAI_API_KEY is not set")

        if not self._settings.OPENAI_MODEL_NAME:
            raise LLMConfigurationError("OPENAI_MODEL_NAME is not set")

        # Validate API key format (basic check)
        if not self._settings.OPENAI_API_KEY.startswith("sk-"):
            logger.warning("OPENAI_API_KEY does not start with 'sk-' - may be invalid")

        logger.debug(f"Using OpenAI model: {self._settings.OPENAI_MODEL_NAME}")

    def get_model(
        self,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        streaming: bool = False,
    ) -> ChatOpenAI:
        """
        Get or create an OpenAI model instance.

        Models are cached by their configuration (temperature, max_tokens, streaming).
        This ensures consistent behavior and avoids creating duplicate instances.

        Args:
            temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
            max_tokens: Maximum tokens in response (None = model default)
            streaming: Whether to enable streaming responses

        Returns:
            Configured ChatOpenAI instance

        Raises:
            LLMConfigurationError: If configuration is invalid
            LLMInitializationError: If model creation fails
        """
        # Validate temperature
        if not 0.0 <= temperature <= 2.0:
            raise LLMConfigurationError(
                f"Temperature must be between 0.0 and 2.0, got {temperature}"
            )

        # Create cache key based on configuration
        cache_key = (temperature, max_tokens, streaming)

        if cache_key not in self._models:
            with self._lock:
                if cache_key not in self._models:
                    try:
                        settings = self._get_settings()
                        logger.info(
                            f"Creating OpenAI model (temp={temperature}, "
                            f"max_tokens={max_tokens}, streaming={streaming})"
                        )

                        model_kwargs = {
                            "model": settings.OPENAI_MODEL_NAME,
                            "api_key": settings.OPENAI_API_KEY,
                            "temperature": temperature,
                            "streaming": streaming,
                        }

                        if max_tokens is not None:
                            model_kwargs["max_tokens"] = max_tokens

                        self._models[cache_key] = ChatOpenAI(**model_kwargs)
                        logger.info(
                            f"OpenAI model created successfully: {settings.OPENAI_MODEL_NAME}"
                        )
                    except Exception as e:
                        logger.error(f"Failed to create OpenAI model: {str(e)}")
                        raise LLMInitializationError(
                            f"Failed to create OpenAI model: {str(e)}"
                        ) from e

        return self._models[cache_key]

    def reset(self) -> None:
        """
        Reset all cached models. Useful for testing or configuration changes.
        """
        with self._lock:
            logger.warning("Resetting all OpenAI models")
            self._models.clear()
            self._settings = None
            logger.info("All OpenAI models reset successfully")

    def get_model_info(self) -> dict:
        """
        Get information about cached models.

        Returns:
            Dictionary with model statistics
        """
        with self._lock:
            return {
                "cached_models": len(self._models),
                "configurations": [
                    {
                        "temperature": temp,
                        "max_tokens": max_tok,
                        "streaming": stream,
                    }
                    for temp, max_tok, stream in self._models.keys()
                ],
                "model_name": (
                    self._settings.OPENAI_MODEL_NAME if self._settings else None
                ),
            }


# Global manager instance
_manager = OpenAIModelManager()


# Public API - Backward compatible
def get_openai_model(
    temperature: float = 0.0,
    max_tokens: Optional[int] = None,
    streaming: bool = False,
) -> ChatOpenAI:
    """
    Get an OpenAI model instance (singleton per configuration).

    This is the main public API for getting OpenAI models. Models are cached
    based on their configuration to ensure consistent behavior.

    Args:
        temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
        max_tokens: Maximum tokens in response (None = model default)
        streaming: Whether to enable streaming responses

    Returns:
        Configured ChatOpenAI instance

    Raises:
        LLMConfigurationError: If configuration is invalid
        LLMInitializationError: If model creation fails

    Example:
        >>> model = get_openai_model(temperature=0.7)
        >>> response = model.invoke("Hello, how are you?")
    """
    return _manager.get_model(
        temperature=temperature, max_tokens=max_tokens, streaming=streaming
    )


def reset_openai_models() -> None:
    """
    Reset all cached OpenAI models.

    Useful for testing or when configuration has changed.
    """
    _manager.reset()


def get_openai_model_info() -> dict:
    """
    Get information about cached OpenAI models.

    Returns:
        Dictionary containing model statistics and configuration info
    """
    return _manager.get_model_info()


# Convenience function for generating responses
def generate_openai_response(
    prompt: str,
    temperature: float = 0.0,
    max_tokens: Optional[int] = None,
) -> str:
    """
    Generate a response using OpenAI model.

    This is a convenience function that handles model retrieval and invocation.

    Args:
        prompt: The input prompt
        temperature: Controls randomness
        max_tokens: Maximum tokens in response

    Returns:
        Generated response text

    Raises:
        LLMConfigurationError: If configuration is invalid
        LLMInitializationError: If model creation fails
    """
    try:
        model = get_openai_model(temperature=temperature, max_tokens=max_tokens)
        logger.debug(f"Generating response for prompt: {prompt[:50]}...")
        response = model.invoke(prompt)
        logger.debug("Response generated successfully")
        return response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        logger.error(f"Failed to generate response: {str(e)}")
        raise


if __name__ == "__main__":
    # Example usage with error handling
    try:
        # Get model with default temperature
        model = get_openai_model(temperature=0.0)
        print(f"Model created: {model}")

        # Generate a response
        response = generate_openai_response("Hello, how are you?", temperature=0.7)
        print(f"Response: {response}")

        # Check model info
        info = get_openai_model_info()
        print(f"Model info: {info}")

    except LLMConfigurationError as e:
        logger.error(f"Configuration error: {e}")
    except LLMInitializationError as e:
        logger.error(f"Initialization error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
