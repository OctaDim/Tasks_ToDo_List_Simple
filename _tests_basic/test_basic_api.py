import pytest
from httpx import AsyncClient


async def _create_user(
        client: AsyncClient,
        email: str = "basic-user@example.com",
        name: str = "Basic User",
) -> dict:
    response = await client.post("/users", json={"email": email, "name": name})
    assert response.status_code == 201
    return response.json()


async def _create_task(
        client: AsyncClient,
        user_id: int,
        title: str = "Basic task",
        description: str | None = "Basic description",
) -> dict:
    response = await client.post(
        f"/users/{user_id}/tasks",
        json={"title": title, "description": description},
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.parametrize(
    ("payload", "expected_status", "expected_param", "message_fragment"),
    [
        ({"email": "created-basic@example.com", "name": "Created Basic"}, 201, None, None),
        ({"email": "not-an-email", "name": "Created Basic"}, 422, "email", None),
        ({"email": "missing-name@example.com"}, 422, "request", "name"),
        ({"email": "", "name": ""}, 422, "request", "email"),
    ],
)
async def test_basic_create_user_cases(
        client: AsyncClient,
        payload: dict,
        expected_status: int,
        expected_param: str | None,
        message_fragment: str | None,
) -> None:
    response = await client.post("/users", json=payload)

    assert response.status_code == expected_status
    if expected_status == 201:
        response_data = response.json()
        assert response_data["email"] == payload["email"]
        assert response_data["name"] == payload["name"]
        return

    detail = response.json()["detail"][0]
    assert detail["param"] == expected_param
    if message_fragment is not None:
        assert message_fragment in detail["message"]


async def test_basic_create_user_duplicate_email_returns_conflict(client: AsyncClient) -> None:
    payload = {"email": "duplicate-basic@example.com", "name": "First Basic User"}

    first_response = await client.post("/users", json=payload)
    second_response = await client.post("/users", json={**payload, "name": "Second Basic User"})

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"][0]["param"] == "email"


@pytest.mark.parametrize(
    ("user_id", "payload", "expected_status", "expected_param", "message_fragment"),
    [
        ("created", {"title": "Created basic task", "description": "Task body"}, 201, None, None),
        ("created", {"title": 123, "description": "Task body"}, 422, "request", "title"),
        ("created", {"description": "Task without title"}, 422, "request", "title"),
        ("created", {"title": "", "description": "Task with blank title"}, 422, "request", "title"),
        (999, {"title": "Task for missing user"}, 404, None, None),
    ],
)
async def test_basic_create_task_cases(
        client: AsyncClient,
        user_id: str | int,
        payload: dict,
        expected_status: int,
        expected_param: str | None,
        message_fragment: str | None,
) -> None:
    created_user = await _create_user(client, email="task-owner-basic@example.com", name="Task Owner Basic")
    resolved_user_id = created_user["id"] if user_id == "created" else user_id

    response = await client.post(f"/users/{resolved_user_id}/tasks", json=payload)

    assert response.status_code == expected_status
    if expected_status == 201:
        response_data = response.json()
        assert response_data["title"] == payload["title"]
        assert response_data["status"] == "new"
        return

    if expected_status == 404:
        assert response.json()["detail"] == "UserModel not found error"
        return

    detail = response.json()["detail"][0]
    assert detail["param"] == expected_param
    if message_fragment is not None:
        assert message_fragment in detail["message"]


@pytest.mark.parametrize(
    ("user_id", "params", "expected_status", "expected_param"),
    [
        ("created", {"limit": 10, "offset": 0}, 200, None),
        ("created", {"limit": 1001}, 422, "limit"),
        ("created", {}, 200, None),
        ("created", {"limit": "", "offset": ""}, 422, "limit"),
        (999, {}, 404, None),
    ],
)
async def test_basic_list_user_tasks_cases(
        client: AsyncClient,
        user_id: str | int,
        params: dict,
        expected_status: int,
        expected_param: str | None,
) -> None:
    created_user = await _create_user(client, email="list-owner-basic@example.com", name="List Owner Basic")
    await _create_task(client, created_user["id"], title="First basic listed task")
    await _create_task(client, created_user["id"], title="Second basic listed task")
    resolved_user_id = created_user["id"] if user_id == "created" else user_id

    response = await client.get(f"/users/{resolved_user_id}/tasks", params=params)

    assert response.status_code == expected_status
    if expected_status == 200:
        response_data = response.json()
        assert "tasks" in response_data
        return

    if expected_status == 404:
        assert response.json()["detail"] == "UserModel not found error"
        return

    assert response.json()["detail"][0]["param"] == expected_param


@pytest.mark.parametrize(
    ("status_value", "expected_status", "expected_param", "expected_count"),
    [
        ("done", 200, None, 1),
        ("archived", 422, "status", None),
        (None, 200, None, 2),
        ("", 422, "status", None),
    ],
)
async def test_basic_filter_tasks_by_status_cases(
        client: AsyncClient,
        status_value: str | None,
        expected_status: int,
        expected_param: str | None,
        expected_count: int | None,
) -> None:
    user = await _create_user(client, email="filter-owner-basic@example.com", name="Filter Owner Basic")
    task_done = await _create_task(client, user["id"], title="Done basic task")
    await _create_task(client, user["id"], title="New basic task")
    update_response = await client.patch(f"/tasks/{task_done['id']}/status", json={"status": "done"})
    assert update_response.status_code == 200

    params = {} if status_value is None else {"status": status_value}
    response = await client.get(f"/users/{user['id']}/tasks", params=params)

    assert response.status_code == expected_status
    if expected_status == 200:
        assert len(response.json()["tasks"]) == expected_count
        return

    assert response.json()["detail"][0]["param"] == expected_param


@pytest.mark.parametrize(
    ("task_id_factory", "payload", "expected_status", "expected_param", "message_fragment"),
    [
        ("created", {"status": "in_progress"}, 200, None, None),
        ("created", {"status": "unknown"}, 422, "status", None),
        ("created", {}, 422, "status", "Field required"),
        ("created", {"status": ""}, 422, "status", None),
        ("missing", {"status": "done"}, 404, None, None),
    ],
)
async def test_basic_update_task_status_cases(
        client: AsyncClient,
        task_id_factory: str,
        payload: dict,
        expected_status: int,
        expected_param: str | None,
        message_fragment: str | None,
) -> None:
    user = await _create_user(client, email="status-owner-basic@example.com", name="Status Owner Basic")
    task = await _create_task(client, user["id"], title="Status basic task")
    task_id = task["id"] if task_id_factory == "created" else 999

    response = await client.patch(f"/tasks/{task_id}/status", json=payload)

    assert response.status_code == expected_status
    if expected_status == 200:
        assert response.json()["status"] == payload["status"]
        return

    if expected_status == 404:
        assert response.json()["detail"] == "TaskModel not found error"
        return

    detail = response.json()["detail"][0]
    assert detail["param"] == expected_param
    if message_fragment is not None:
        assert message_fragment in detail["message"]


@pytest.mark.parametrize(
    ("path", "prepare_task", "expected_status", "expected_param", "expected_detail"),
    [
        ("/tasks/{task_id}", True, 200, None, None),
        ("/tasks/not-int", False, 422, "task_id", None),
        ("/tasks/", False, 404, None, None),
        ("/tasks/%20", False, 422, "task_id", None),
        ("/tasks/999", False, 404, None, "TaskModel not found error: task id: 999"),
    ],
)
async def test_basic_delete_task_cases(
        client: AsyncClient,
        path: str,
        prepare_task: bool,
        expected_status: int,
        expected_param: str | None,
        expected_detail: str | None,
) -> None:
    task_id = 0
    if prepare_task:
        user = await _create_user(client, email="delete-owner-basic@example.com", name="Delete Owner Basic")
        task = await _create_task(client, user["id"], title="Delete basic task")
        task_id = task["id"]

    response = await client.delete(path.format(task_id=task_id))

    assert response.status_code == expected_status
    if expected_status == 200:
        assert response.json() == {"ok": True}
        return

    if expected_status == 404 and expected_detail is not None:
        assert response.json()["detail"] == expected_detail
        return

    if expected_status == 422:
        assert response.json()["detail"][0]["param"] == expected_param


@pytest.mark.parametrize(
    ("path", "prepare_data", "expected_status", "expected_param", "expected_total", "expected_detail"),
    [
        ("/users/{user_id}/tasks/stats", True, 200, None, 2, None),
        ("/users/not-int/tasks/stats", False, 422, "user_id", None, None),
        ("/users/tasks/stats", False, 404, None, None, None),
        ("/users/%20/tasks/stats", False, 422, "user_id", None, None),
        ("/users/999/tasks/stats", False, 404, None, None, "UserModel not found error"),
    ],
)
async def test_basic_user_task_stats_cases(
        client: AsyncClient,
        path: str,
        prepare_data: bool,
        expected_status: int,
        expected_param: str | None,
        expected_total: int | None,
        expected_detail: str | None,
) -> None:
    user_id = 0
    if prepare_data:
        user = await _create_user(client, email="stats-owner-basic@example.com", name="Stats Owner Basic")
        user_id = user["id"]
        task_done = await _create_task(client, user_id, title="Done stats basic task")
        await _create_task(client, user_id, title="New stats basic task")
        update_response = await client.patch(f"/tasks/{task_done['id']}/status", json={"status": "done"})
        assert update_response.status_code == 200

    response = await client.get(path.format(user_id=user_id))

    assert response.status_code == expected_status
    if expected_status == 200:
        response_data = response.json()
        assert response_data["total"] == expected_total
        assert response_data["done"] == 1
        assert response_data["new"] == 1
        return

    if expected_status == 404 and expected_detail is not None:
        assert response.json()["detail"] == expected_detail
        return

    if expected_status == 422:
        assert response.json()["detail"][0]["param"] == expected_param
