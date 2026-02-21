import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.ragflow import RAGFlowClient


@pytest.mark.asyncio
async def test_ragflow_search():
    client = RAGFlowClient()

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": {
            "chunks": [
                {
                    "content": "烟酰胺在化妆品中的限量为2%",
                    "similarity": 0.95,
                    "document_keyword": "化妆品法规手册",
                    "kb_id": "kb1",
                }
            ],
            "total": 1,
        }
    }
    mock_response.raise_for_status = MagicMock()

    mock_client_instance = AsyncMock()
    mock_client_instance.post = AsyncMock(return_value=mock_response)
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=False)

    with patch("httpx.AsyncClient", return_value=mock_client_instance):
        result = await client.search("烟酰胺限量", ["kb1"], top_k=5)

    assert "data" in result
    assert "chunks" in result["data"]
    assert len(result["data"]["chunks"]) == 1
    assert result["data"]["chunks"][0]["content"] == "烟酰胺在化妆品中的限量为2%"

    mock_client_instance.post.assert_called_once()
    call_kwargs = mock_client_instance.post.call_args
    assert "烟酰胺限量" in str(call_kwargs)


@pytest.mark.asyncio
async def test_ragflow_list_datasets():
    client = RAGFlowClient()

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [
            {"id": "kb1", "name": "化妆品法规库"},
            {"id": "kb2", "name": "成分安全库"},
        ]
    }
    mock_response.raise_for_status = MagicMock()

    mock_client_instance = AsyncMock()
    mock_client_instance.get = AsyncMock(return_value=mock_response)
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=False)

    with patch("httpx.AsyncClient", return_value=mock_client_instance):
        result = await client.list_datasets()

    assert "data" in result
    assert len(result["data"]) == 2
    assert result["data"][0]["id"] == "kb1"

    mock_client_instance.get.assert_called_once()
