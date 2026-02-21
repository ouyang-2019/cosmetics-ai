from fastapi import APIRouter, Depends, HTTPException, status

from app.models.user import User
from app.schemas.knowledge import SearchChunk, SearchRequest, SearchResponse
from app.services.auth import get_current_user
from app.services.ragflow import ragflow_client

router = APIRouter(prefix="/api/knowledge", tags=["知识库"])


@router.post("/search", response_model=SearchResponse)
async def search_knowledge(
    request: SearchRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        result = await ragflow_client.search(
            question=request.question,
            dataset_ids=request.dataset_ids,
            top_k=request.top_k,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"RAGFlow 服务异常: {str(e)}",
        )

    raw_chunks = []
    data = result.get("data", {})
    if isinstance(data, dict):
        raw_chunks = data.get("chunks", [])
    elif isinstance(data, list):
        raw_chunks = data

    chunks = []
    for chunk in raw_chunks:
        chunks.append(
            SearchChunk(
                content=chunk.get("content", chunk.get("content_with_weight", "")),
                score=float(chunk.get("similarity", chunk.get("score", 0.0))),
                document_name=chunk.get("document_keyword", chunk.get("document_name", "")),
                dataset_id=chunk.get("kb_id", chunk.get("dataset_id", "")),
            )
        )

    return SearchResponse(
        question=request.question,
        chunks=chunks,
        total=len(chunks),
    )


@router.get("/datasets")
async def list_datasets(
    current_user: User = Depends(get_current_user),
):
    try:
        result = await ragflow_client.list_datasets()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"RAGFlow 服务异常: {str(e)}",
        )
