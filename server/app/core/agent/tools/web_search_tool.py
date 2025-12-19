from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import tool
import logging

logger = logging.getLogger(__name__)

SEARCH_DISCRIPTION = """
Use this tool to search the web via DuckDuckGo for high-quality, commonly asked interview questions.

This tool should be used ONLY when you need to:
- Discover realistic, industry-standard interview questions
- Validate commonly expected interview topics for a given role, experience level, or technology stack
- Gather inspiration for question phrasing (not verbatim copying)

Dynamic Search Guidance:
- Adapt the search query based on:
  - job role
  - experience level
  - specific programming language or framework
- Combine role + stack + seniority in the query
  (e.g., "junior spring boot interview questions", "senior backend system design interview")

Usage Rules:
- Do NOT copy questions directly from search results.
- Extract concepts or themes, then rephrase questions in your own words.
- Prefer conceptual and scenario-based questions over trivia.
- Avoid blog-style or opinion-based content.

Result Selection Criteria:
- Prefer results that mention:
  - real interview experiences
  - common interview questions
  - hiring manager expectations
- Ignore results that are:
  - exam dumps
  - outdated (pre-2018 unless fundamentals)
  - low-quality forums without context

Post-Processing Requirements:
- Rewrite every question to match the user's:
  - experience level
  - role
  - technology stack
- Ensure questions align with the interview strategy and difficulty.
- Use search results as inspiration only, not as final output.

Example Valid Queries:
- "junior java spring boot interview questions"
- "backend developer REST API interview questions"
- "behavioral interview questions software engineer"

Example Invalid Queries:
- "java spring boot answers"
- "exact interview questions google"
- "leetcode solutions"

Do NOT mention the search tool or sources in the final output.

"""


@tool(name_or_callable="web_search_tool")
def web_search_tool(query: str) -> DuckDuckGoSearchRun:
    """Use this tool to search the web via DuckDuckGo for high-quality, commonly asked interview questions."""
    logger.info(f"Web search tool called with query: {query}")
    web_search = DuckDuckGoSearchRun(
        name="web_search",
        description=SEARCH_DISCRIPTION,
    )
    return web_search
