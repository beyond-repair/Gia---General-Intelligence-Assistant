import asyncio

import pytest


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_create_list_get_task(client):
    create = await client.post("/tasks/", json={"description": "API demo task"})
    assert create.status_code == 200
    body = create.json()
    assert body["description"] == "API demo task"
    assert body["id"]
    assert len(body["steps"]) == 7
    task_id = body["id"]

    # Background processing — wait briefly for stub pipeline
    for _ in range(40):
        got = await client.get(f"/tasks/{task_id}")
        assert got.status_code == 200
        data = got.json()
        if data["status"] in ("completed", "failed"):
            break
        await asyncio.sleep(0.05)
    else:
        pytest.fail("task did not finish in time")

    assert data["status"] == "completed"
    assert data["result"]

    listing = await client.get("/tasks/")
    assert listing.status_code == 200
    ids = [t["id"] for t in listing.json()]
    assert task_id in ids


@pytest.mark.asyncio
async def test_get_missing_task(client):
    resp = await client.get("/tasks/does-not-exist")
    assert resp.status_code == 404
