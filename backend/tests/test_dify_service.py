import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.dify import DifyClient


@pytest.mark.asyncio
async def test_dify_run_workflow():
    client = DifyClient()

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "workflow_run_id": "run-abc123",
        "task_id": "task-xyz",
        "data": {
            "id": "run-abc123",
            "workflow_id": "wf-001",
            "status": "succeeded",
            "outputs": {"result": "法规检索完成，未发现违规成分"},
            "error": None,
            "elapsed_time": 3.14,
            "total_tokens": 512,
        },
    }
    mock_response.raise_for_status = MagicMock()

    mock_client_instance = AsyncMock()
    mock_client_instance.post = AsyncMock(return_value=mock_response)
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=False)

    with patch("httpx.AsyncClient", return_value=mock_client_instance):
        result = await client.run_workflow(
            workflow_api_key="test-wf-key",
            inputs={"ingredient": "烟酰胺", "concentration": "2%"},
            user="testuser",
        )

    assert "workflow_run_id" in result
    assert result["workflow_run_id"] == "run-abc123"
    assert "data" in result
    assert result["data"]["status"] == "succeeded"
    assert result["data"]["outputs"]["result"] == "法规检索完成，未发现违规成分"

    mock_client_instance.post.assert_called_once()
    call_kwargs = mock_client_instance.post.call_args
    assert "/v1/workflows/run" in str(call_kwargs)
    assert "blocking" in str(call_kwargs)


@pytest.mark.asyncio
async def test_dify_chat():
    client = DifyClient()

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "message_id": "msg-abc123",
        "conversation_id": "conv-xyz456",
        "mode": "chat",
        "answer": "根据化妆品法规，烟酰胺的使用限量为2%，超过该限量需要特殊审批。",
        "metadata": {
            "usage": {"total_tokens": 256},
            "retriever_resources": [
                {"document_name": "化妆品安全技术规范2023", "score": 0.92}
            ],
        },
        "created_at": 1700000000,
    }
    mock_response.raise_for_status = MagicMock()

    mock_client_instance = AsyncMock()
    mock_client_instance.post = AsyncMock(return_value=mock_response)
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=False)

    with patch("httpx.AsyncClient", return_value=mock_client_instance):
        result = await client.chat(
            app_api_key="test-app-key",
            query="烟酰胺的使用限量是多少？",
            user="testuser",
            conversation_id="",
        )

    assert "answer" in result
    assert "conversation_id" in result
    assert result["answer"] == "根据化妆品法规，烟酰胺的使用限量为2%，超过该限量需要特殊审批。"
    assert result["conversation_id"] == "conv-xyz456"

    mock_client_instance.post.assert_called_once()
    call_kwargs = mock_client_instance.post.call_args
    assert "/v1/chat-messages" in str(call_kwargs)
    assert "烟酰胺的使用限量是多少？" in str(call_kwargs)
