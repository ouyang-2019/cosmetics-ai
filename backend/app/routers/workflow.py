from fastapi import APIRouter, Depends, HTTPException, status

from app.models.user import User
from app.schemas.workflow import ChatRequest, ChatResponse, WorkflowRunRequest, WorkflowRunResponse
from app.services.auth import get_current_user
from app.services.dify import dify_client

router = APIRouter(prefix="/api/workflow", tags=["工作流"])

WORKFLOW_KEYS = {
    "regulation_search": "",   # WF1
    "doc_review": "",          # WF2
    "copy_review": "",         # WF3
    "copy_generate": "",       # WF4
}
CHAT_APP_KEY = ""  # APP1


@router.post("/run", response_model=WorkflowRunResponse)
async def run_workflow(
    request: WorkflowRunRequest,
    current_user: User = Depends(get_current_user),
):
    api_key = WORKFLOW_KEYS.get(request.workflow_key)
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"未知的工作流: {request.workflow_key}",
        )
    try:
        result = await dify_client.run_workflow(
            workflow_api_key=api_key,
            inputs=request.inputs,
            user=current_user.username,
        )
        return WorkflowRunResponse(
            workflow_run_id=result.get("workflow_run_id", ""),
            status=result.get("data", {}).get("status", result.get("status", "unknown")),
            outputs=result.get("data", {}).get("outputs"),
            error=result.get("data", {}).get("error"),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"工作流执行失败: {str(e)}",
        )


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        result = await dify_client.chat(
            app_api_key=CHAT_APP_KEY,
            query=request.query,
            user=current_user.username,
            conversation_id=request.conversation_id,
        )
        return ChatResponse(
            answer=result.get("answer", ""),
            conversation_id=result.get("conversation_id", ""),
            sources=result.get("retriever_resources", []),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"对话请求失败: {str(e)}",
        )
