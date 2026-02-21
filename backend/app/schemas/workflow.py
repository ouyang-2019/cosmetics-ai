from pydantic import BaseModel


class WorkflowRunRequest(BaseModel):
    workflow_key: str
    inputs: dict


class WorkflowRunResponse(BaseModel):
    workflow_run_id: str
    status: str
    outputs: dict | None = None
    error: str | None = None


class ChatRequest(BaseModel):
    query: str
    conversation_id: str = ""


class ChatResponse(BaseModel):
    answer: str
    conversation_id: str
    sources: list[dict] = []
