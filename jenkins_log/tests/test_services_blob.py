import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import json

from jenkins_log.services.blob import extract_builds_to_blob


@pytest.mark.asyncio
async def test_extract_builds_to_blob_old_build():
    # Arrange
    build_time = datetime.now() - timedelta(days=10)
    timestamp_ms = int(build_time.timestamp() * 1000)

    mock_blob = AsyncMock()
    mock_blob.upload_blob = AsyncMock()

    with patch("jenkins_log.services.blob.BlobServiceClient") as mock_bsc, \
         patch("aiohttp.ClientSession") as mock_sess:
        mock_bsc.return_value.get_blob_client.return_value = mock_blob

        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({
            "timestamp": timestamp_ms
        }).encode()

        mock_get_cm = AsyncMock()
        mock_get_cm.__aenter__.return_value = mock_resp

        mock_session_instance = MagicMock()
        mock_session_instance.get.return_value = mock_get_cm
        mock_sess.return_value.__aenter__.return_value = mock_session_instance

        # Act
        await extract_builds_to_blob("http://mockurl/api/json", "mockblob")

        # Assert
        assert mock_blob.upload_blob.called, "Build mais ANTIGA que 7 dias, será salva no blob."


@pytest.mark.asyncio
async def test_extract_builds_to_blob_new_build():
    # Arrange: Simula timestamp de 2 dias atrás (build RECENTE - NÃO deve salvar)
    build_time = datetime.now() - timedelta(days=2)
    timestamp_ms = int(build_time.timestamp() * 1000)

    mock_blob = AsyncMock()
    mock_blob.upload_blob = AsyncMock()

    mock_container = MagicMock()
    mock_container.get_blob_client.return_value = mock_blob

    with patch("jenkins_log.services.blob.BlobServiceClient") as mock_bsc, \
         patch("aiohttp.ClientSession") as mock_sess:
        mock_bsc.return_value.get_container_client.return_value = mock_container

        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({
            "timestamp": timestamp_ms
        }).encode()

        mock_get_cm = AsyncMock()
        mock_get_cm.__aenter__.return_value = mock_resp

        mock_session_instance = MagicMock()
        mock_session_instance.get.return_value = mock_get_cm
        mock_sess.return_value.__aenter__.return_value = mock_session_instance
        # Act
        await extract_builds_to_blob("http://mockurl/api/json", "mockblob")

        # Assert
        assert not mock_blob.upload_blob.called, "Build mais RECENTE que 7 dias, não será salva no blob."


@pytest.mark.asyncio
async def test_extract_builds_to_blob_upload_error():
    # Arrange:
    build_time = datetime.now() - timedelta(days=10)
    timestamp_ms = int(build_time.timestamp() * 1000)

    mock_blob = AsyncMock()
    mock_blob.upload_blob.side_effect = Exception("Falha upload")

    with patch("jenkins_log.services.blob.BlobServiceClient") as mock_bsc, \
         patch("aiohttp.ClientSession") as mock_sess:
        mock_bsc.return_value.get_blob_client.return_value = mock_blob

        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({
            "timestamp": timestamp_ms
        }).encode()

        mock_get_cm = AsyncMock()
        mock_get_cm.__aenter__.return_value = mock_resp

        mock_session_instance = MagicMock()
        mock_session_instance.get.return_value = mock_get_cm
        mock_sess.return_value.__aenter__.return_value = mock_session_instance

        # Act
        await extract_builds_to_blob("http://mockurl/api/json", "mockblob")

        # Assert
        assert mock_blob.upload_blob.called


@pytest.mark.asyncio
async def test_extract_builds_to_blob_malformed_json():
    # Arrange:
    mock_blob = AsyncMock()
    with patch("jenkins_log.services.blob.BlobServiceClient") as mock_bsc, \
         patch("aiohttp.ClientSession") as mock_sess:
        mock_bsc.return_value.get_blob_client.return_value = mock_blob

        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b"txt response!"

        mock_get_cm = AsyncMock()
        mock_get_cm.__aenter__.return_value = mock_resp

        mock_session_instance = MagicMock()
        mock_session_instance.get.return_value = mock_get_cm
        mock_sess.return_value.__aenter__.return_value = mock_session_instance

        # Act/Assert
        await extract_builds_to_blob("http://mockurl/api/json", "mockblob")
        assert not mock_blob.upload_blob.called
