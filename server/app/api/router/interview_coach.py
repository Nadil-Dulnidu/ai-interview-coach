from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.api.model.interview_coach_models import VercelChatRequest
from app.api.service.streaming_service import stream_interview_coach_chat
from app.core.agent.model.dynamic_prompt_model import Context
from app.util.vercel_adapter.http_headers import patch_vercel_headers
from app.util.vercel_adapter.message_transformer import extract_user_message

router = APIRouter()


@router.post("/chat")
async def interview_coach_chat_streaming(request: VercelChatRequest):
    """
    Streaming chat endpoint using the pluggable LangGraph-to-Vercel adapter.

    This endpoint uses clean separation of concerns:
    - Core agentic logic (LangGraph) is unchanged
    - Adapter layer handles streaming protocol transformation
    - No coupling between graph structure and streaming protocol

    Architecture:
    - Pluggable adapter works with any LangGraph graph
    - Configurable message extraction strategies
    - Easy to customize and maintain
    - Well-tested and documented

    Compatible with Vercel AI SDK's useChat and useAssistant hooks.
    Supports interrupts for human-in-the-loop workflows.
    """
    # Transform UI messages to message string
    message = extract_user_message(request.messages)

    # Use thread_id from body if provided, otherwise use conversation id
    thread_id = request.thread_id or request.id
    print(f"Thread ID: {thread_id}")

    context = Context(user_name=request.user_name, assistent_name=request.assistent_name)

    response = StreamingResponse(
        stream_interview_coach_chat(
            message=message, thread_id=thread_id, resume=request.resume or False, context=context
        ),
        media_type="text/event-stream",
    )

    return patch_vercel_headers(response)
