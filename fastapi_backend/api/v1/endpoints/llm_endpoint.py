from fastapi import Request
from fastapi import status
from fastapi.responses import StreamingResponse, JSONResponse
from services import llm_service
from fastapi import APIRouter, Depends
from models.schemas import llm_schema
from core.configure import conf
from api import deps

llm_router = APIRouter(prefix='/llm', tags=['LLM'])


@llm_router.post('/stream-general-agent')
async def stream_agent(call_llm: llm_schema.CallLLM, user_id: str = Depends(deps.check_token)):
    if user_id != call_llm.user_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={'detail': 'User ID does not match token'},
        )
    return StreamingResponse(
        llm_service.service_general_agent(call_llm),
        media_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache, no-transform, no-store',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no',
        },
    )


@llm_router.get('/llm-names', dependencies=[Depends(deps.check_token)])
def llm_names():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=conf.llm_names,
    )
