from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, knowledge, workflow

app = FastAPI(
    title="化妆品AI智能平台",
    description="化妆品行业垂直AI平台 - 法规检索、文档审核、文案合规、知识库问答",
    version="0.1.0",
)

# CORS 配置：生产环境应通过 CORS_ORIGINS 环境变量限制来源
_origins = settings.cors_origins.split(",") if settings.cors_origins else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=bool(settings.cors_origins),
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(knowledge.router)
app.include_router(workflow.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "cosmetics-ai-backend"}
