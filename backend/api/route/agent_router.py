from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from api.controller.agent_controller import AQIAgentController

router = APIRouter(prefix="/agent")
controller = AQIAgentController()

@router.post("/chat")
async def chat(request: Request):
    return await controller.chat(request)

@router.post("/chat/stream")
async def chat_stream(request: Request):
    return StreamingResponse(
        controller.generate_stream_from_request(request),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )

@router.get("/health")
async def health_check():
    return controller.health_check()
