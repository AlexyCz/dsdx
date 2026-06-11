import pytest
from unittest.mock import MagicMock, AsyncMock
from oauth.authorization_server import AuthorizationServer
from oauth.oauth_types import TokenRequest, AuthorizationCode
from asimpy import Environment, Queue

@pytest.fixture(scope="module")
def test_auth_server():
    env = Environment()
    auth_server = AuthorizationServer(env)
    auth_server.register_client(client_id="test_id", client_secret="test_secret", redirect_uris=["test.uri"])
    auth_server.auth_codes["test_code"] = AuthorizationCode(
        code="test_code",
        client_id="test_id",
        redirect_uri="test.uri",
        scope=["test"],
        expires_at=123.45,
        used=True
    )
    return auth_server

@pytest.mark.asyncio
async def test_validate_token_request(test_auth_server):
    mock_queue = AsyncMock()
    invalid_token_request = TokenRequest(
        code="test_code",
        client_id="test_id",
        client_secret="test_secret",
        redirect_uri="test.uri",
        response_queue=mock_queue
    )

    response_code = await test_auth_server._validate_token_request(invalid_token_request)
    assert response_code is None
