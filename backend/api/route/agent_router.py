from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from api.controller.agent_controller import WQIAgentController

router = APIRouter(prefix="/agent")
controller = WQIAgentController()

@router.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        message = data.get("message")
        result = await controller.chat(message)
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "error": f"Internal server error: {str(e)}",
            "status": "error"
        })

# @router.post("/chat/stream")
# async def chat_stream(request: Request):
#     return StreamingResponse(
#         controller.generate_stream_from_request(request),
#         media_type="text/event-stream",
#         headers={
#             "Cache-Control": "no-cache",
#             "Connection": "keep-alive",
#             "Access-Control-Allow-Origin": "*",
#             "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
#             "Access-Control-Allow-Headers": "*",
#         }
#     )

@router.get("/health")
async def health_check():
    return controller.health_check()

@router.get("/tools")
async def get_tools_info():
    """
    Get information about available tools
    """
    try:
        tools_info = []
        for tool in controller.tools:
            tools_info.append({
                "name": tool.name,
                "description": tool.description,
                "args_schema": str(tool.args_schema) if tool.args_schema else None
            })
        
        return {
            "tools": tools_info,
            "total_tools": len(tools_info),
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "error": f"Failed to get tools info: {str(e)}",
            "status": "error"
        })
