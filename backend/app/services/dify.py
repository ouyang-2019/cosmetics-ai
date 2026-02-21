from typing import AsyncGenerator

import httpx

from app.config import settings


class DifyClient:
    def __init__(self):
        self.base_url = settings.dify_url.rstrip("/")

    def _headers(self, workflow_api_key: str | None = None) -> dict:
        api_key = workflow_api_key or settings.dify_api_key
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def run_workflow(self, workflow_api_key: str, inputs: dict, user: str) -> dict:
        url = f"{self.base_url}/v1/workflows/run"
        body = {
            "inputs": inputs,
            "response_mode": "blocking",
            "user": user,
        }
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(url, json=body, headers=self._headers(workflow_api_key))
            response.raise_for_status()
            return response.json()

    async def run_workflow_stream(
        self, workflow_api_key: str, inputs: dict, user: str
    ) -> AsyncGenerator[str, None]:
        url = f"{self.base_url}/v1/workflows/run"
        body = {
            "inputs": inputs,
            "response_mode": "streaming",
            "user": user,
        }
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream("POST", url, json=body, headers=self._headers(workflow_api_key)) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        yield line[5:].strip()

    async def chat(
        self,
        app_api_key: str,
        query: str,
        user: str,
        conversation_id: str = "",
    ) -> dict:
        url = f"{self.base_url}/v1/chat-messages"
        body = {
            "inputs": {},
            "query": query,
            "response_mode": "blocking",
            "user": user,
            "conversation_id": conversation_id,
        }
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, json=body, headers=self._headers(app_api_key))
            response.raise_for_status()
            return response.json()


dify_client = DifyClient()
