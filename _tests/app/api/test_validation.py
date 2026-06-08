from httpx import AsyncClient


async def test_create_user_validates_blank_name_with_parameter_value(client: AsyncClient) -> None:
    response = await client.post("/users", json={"email": "user@example.com", "name": ""})

    assert response.status_code == 422
    assert response.json()["detail"][0]["param"] == "request"
    assert "name" in response.json()["detail"][0]["message"]


async def test_duplicate_email_returns_conflict(client: AsyncClient) -> None:
    first_response = await client.post("/users", json={"email": "dupe@example.com", "name": "Ivan"})
    assert first_response.status_code == 201

    second_response = await client.post("/users", json={"email": "dupe@example.com", "name": "Petr"})
    assert second_response.status_code == 409


async def test_list_user_tasks_uses_pydantic_pagination_limits(client: AsyncClient) -> None:
    user_response = await client.post("/users", json={"email": "pager@example.com", "name": "Ivan"})
    assert user_response.status_code == 201
    user_id = user_response.json()["id"]

    max_limit_response = await client.get(f"/users/{user_id}/tasks", params={"limit": 1000})
    assert max_limit_response.status_code == 200

    too_large_response = await client.get(f"/users/{user_id}/tasks", params={"limit": 1001})
    assert too_large_response.status_code == 422
    assert too_large_response.json()["detail"][0]["param"] == "limit"


async def test_list_user_tasks_rejects_invalid_offset(client: AsyncClient) -> None:
    user_response = await client.post("/users", json={"email": "offset@example.com", "name": "Ivan"})
    assert user_response.status_code == 201
    user_id = user_response.json()["id"]

    response = await client.get(f"/users/{user_id}/tasks", params={"offset": -1})

    assert response.status_code == 422
    assert response.json()["detail"][0]["param"] == "offset"
