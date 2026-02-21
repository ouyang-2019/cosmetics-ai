from pydantic import BaseModel


class SearchRequest(BaseModel):
    question: str
    dataset_ids: list[str]
    top_k: int = 5


class SearchChunk(BaseModel):
    content: str
    score: float
    document_name: str
    dataset_id: str


class SearchResponse(BaseModel):
    question: str
    chunks: list[SearchChunk]
    total: int
