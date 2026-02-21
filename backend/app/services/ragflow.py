import httpx

from app.config import settings


class RAGFlowClient:
    def __init__(self):
        self.base_url = settings.ragflow_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {settings.ragflow_api_key}",
            "Content-Type": "application/json",
        }

    async def search(self, question: str, dataset_ids: list[str], top_k: int = 5) -> dict:
        url = f"{self.base_url}/api/v1/retrieval"
        body = {
            "question": question,
            "datasets": dataset_ids,
            "top_k": top_k,
            "similarity_threshold": 0.3,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json=body, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def list_datasets(self) -> dict:
        url = f"{self.base_url}/api/v1/datasets"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def upload_document(self, dataset_id: str, file_path: str, file_name: str) -> dict:
        url = f"{self.base_url}/api/v1/datasets/{dataset_id}/documents"
        upload_headers = {k: v for k, v in self.headers.items() if k != "Content-Type"}
        async with httpx.AsyncClient(timeout=30) as client:
            with open(file_path, "rb") as f:
                files = {"file": (file_name, f)}
                response = await client.post(url, files=files, headers=upload_headers)
                response.raise_for_status()
                return response.json()


ragflow_client = RAGFlowClient()
