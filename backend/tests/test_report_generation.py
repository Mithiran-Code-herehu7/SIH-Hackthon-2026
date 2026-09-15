import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_report_generation_flow():
    """Verify that mode=generate_report returns task_type=generate_report and creates a valid .docx file."""
    response = client.post(
        "/query",
        json={
            "query": "Compile a technical compliance audit report for MRPL Refinery operations.",
            "mode": "generate_report",
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    assert data["task_type"] == "generate_report"
    assert data["requires_file"] is True
    assert data["file_type"] == "docx"
    assert len(data["files"]) > 0

    file_meta = data["files"][0]
    assert file_meta["name"].endswith(".docx")
    assert "/files/" in file_meta["download_url"]

    # Download file and verify existence & content
    dl_resp = client.get(file_meta["download_url"])
    assert dl_resp.status_code == 200
    assert len(dl_resp.content) > 1024  # DOCX file must be non-empty (>1KB)
    assert dl_resp.content[:2] == b"PK"  # Office Open XML ZIP magic header


def test_report_generation_keyword_query():
    """Verify that a prompt requesting a report returns valid docx deliverable payload."""
    response = client.post(
        "/query",
        json={
            "query": "Generate a technical compliance report on safety and equipment incidents",
            "mode": "chat",
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert data["task_type"] == "generate_report"
    assert data["requires_file"] is True
    assert data["file_type"] == "docx"
