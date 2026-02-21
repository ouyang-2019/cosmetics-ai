from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, knowledge, workflow

app = FastAPI(
    title="化妆品AI智能平台",
    description="化妆品行业垂直AI平台 - 法规检索、文档审核、文案合规、知识库问答",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(knowledge.router)
app.include_router(workflow.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "cosmetics-ai-backend"}
