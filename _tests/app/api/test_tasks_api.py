from httpx import AsyncClient


async def test_user_task_lifecycle_and_stats(client: AsyncClient) -> None:
    user_response = await client.post("/users", json={"email": "user@example.com", "name": "Ivan"})
    assert user_response.status_code == 201
    user = user_response.json()

    fetched_user_response = await client.get(f"/users/{user['id']}")
    assert fetched_user_response.status_code == 200
    assert fetched_user_response.json()["email"] == "user@example.com"

    first_task_response = await client.post(
        f"/users/{user['id']}/tasks",
        json={"title": "Prepare report", "description": "Collect weekly data"},
    )
    assert first_task_response.status_code == 201
    first_task = first_task_response.json()
    assert first_task["status"] == "new"

    second_task_response = await client.post(f"/users/{user['id']}/tasks", json={"title": "Send report"})
    assert second_task_response.status_code == 201

    update_response = await client.patch(f"/tasks/{first_task['id']}/status", json={"status": "done"})
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "done"

    list_response = await client.get(f"/users/{user['id']}/tasks", params={"status": "done", "limit": 10, "offset": 0})
    assert list_response.status_code == 200
    listed_tasks = list_response.json()["tasks"]
    assert len(listed_tasks) == 1
    assert listed_tasks[0]["id"] == first_task["id"]

    stats_response = await client.get(f"/users/{user['id']}/tasks/stats")
    assert stats_response.status_code == 200
    assert stats_response.json() == {"total": 2, "new": 1, "in_progress": 0, "done": 1, "cancelled": 0}

    delete_response = await client.delete(f"/tasks/{first_task['id']}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"ok": True}

    missing_delete_response = await client.delete(f"/tasks/{first_task['id']}")
    assert missing_delete_response.status_code == 404


async def test_create_user(client: AsyncClient) -> None:
    response = await client.post("/users", json={"email": "created@example.com", "name": "Created User"})

    assert response.status_code == 201
    response_data = response.json()
    assert response_data["email"] == "created@example.com"
    assert response_data["name"] == "Created User"


async def test_create_user_duplicate_email_returns_conflict(client: AsyncClient) -> None:
    payload = {"email": "duplicate@example.com", "name": "First User"}

    first_response = await client.post("/users", json=payload)
    duplicate_response = await client.post("/users", json={**payload, "name": "Second User"})

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409


async def test_create_task(client: AsyncClient) -> None:
    user_response = await client.post("/users", json={"email": "task-owner@example.com", "name": "Task Owner"})
    user = user_response.json()

    response = await client.post(
        f"/users/{user['id']}/tasks",
        json={"title": "Create an explicit task", "description": "API contract coverage"},
    )

    assert response.status_code == 201
    response_data = response.json()
    assert response_data["title"] == "Create an explicit task"
    assert response_data["description"] == "API contract coverage"
    assert response_data["status"] == "new"


async def test_get_task_list(client: AsyncClient) -> None:
    user_response = await client.post("/users", json={"email": "list-owner@example.com", "name": "List Owner"})
    user = user_response.json()
    await client.post(f"/users/{user['id']}/tasks", json={"title": "First listed task"})
    await client.post(f"/users/{user['id']}/tasks", json={"title": "Second listed task"})

    response = await client.get(f"/users/{user['id']}/tasks")

    assert response.status_code == 200
    assert [task["title"] for task in response.json()["tasks"]] == ["First listed task", "Second listed task"]


async def test_filter_tasks_by_status(client: AsyncClient) -> None:
    user_response = await client.post("/users", json={"email": "filter-owner@example.com", "name": "Filter Owner"})
    user = user_response.json()
    first_task_response = await client.post(f"/users/{user['id']}/tasks", json={"title": "Done task"})
    await client.post(f"/users/{user['id']}/tasks", json={"title": "New task"})
    first_task = first_task_response.json()
    await client.patch(f"/tasks/{first_task['id']}/status", json={"status": "done"})

    response = await client.get(f"/users/{user['id']}/tasks", params={"status": "done"})

    assert response.status_code == 200
    tasks = response.json()["tasks"]
    assert len(tasks) == 1
    assert tasks[0]["id"] == first_task["id"]
    assert tasks[0]["status"] == "done"


async def test_update_task_status(client: AsyncClient) -> None:
    user_response = await client.post("/users", json={"email": "status-owner@example.com", "name": "Status Owner"})
    user = user_response.json()
    task_response = await client.post(f"/users/{user['id']}/tasks", json={"title": "Status task"})
    task = task_response.json()

    response = await client.patch(f"/tasks/{task['id']}/status", json={"status": "in_progress"})

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


async def test_delete_task(client: AsyncClient) -> None:
    user_response = await client.post("/users", json={"email": "delete-owner@example.com", "name": "Delete Owner"})
    user = user_response.json()
    task_response = await client.post(f"/users/{user['id']}/tasks", json={"title": "Delete task"})
    task = task_response.json()

    response = await client.delete(f"/tasks/{task['id']}")

    assert response.status_code == 200
    assert response.json() == {"ok": True}


async def test_get_statistics(client: AsyncClient) -> None:
    user_response = await client.post("/users", json={"email": "stats-owner@example.com", "name": "Stats Owner"})
    user = user_response.json()
    first_task_response = await client.post(f"/users/{user['id']}/tasks", json={"title": "Done stats task"})
    second_task_response = await client.post(f"/users/{user['id']}/tasks", json={"title": "Cancelled stats task"})
    await client.post(f"/users/{user['id']}/tasks", json={"title": "New stats task"})
    await client.patch(f"/tasks/{first_task_response.json()['id']}/status", json={"status": "done"})
    await client.patch(f"/tasks/{second_task_response.json()['id']}/status", json={"status": "cancelled"})

    response = await client.get(f"/users/{user['id']}/tasks/stats")

    assert response.status_code == 200
    assert response.json() == {"total": 3, "new": 1, "in_progress": 0, "done": 1, "cancelled": 1}


async def test_two_users_with_three_tasks_each_across_all_endpoints(client: AsyncClient) -> None:
    users = []
    for index in range(1, 3):
        user_response = await client.post(
            "/users",
            json={"email": f"scenario-user-{index}@example.com", "name": f"Scenario User {index}"},
        )
        assert user_response.status_code == 201
        users.append(user_response.json())

    for user in users:
        fetched_user_response = await client.get(f"/users/{user['id']}")
        assert fetched_user_response.status_code == 200
        assert fetched_user_response.json()["email"] == user["email"]

        task_responses = [
            await client.post(f"/users/{user['id']}/tasks", json={"title": f"{user['name']} new task"}),
            await client.post(f"/users/{user['id']}/tasks", json={"title": f"{user['name']} progress task"}),
            await client.post(f"/users/{user['id']}/tasks", json={"title": f"{user['name']} done task"}),
        ]
        assert [response.status_code for response in task_responses] == [201, 201, 201]
        tasks = [response.json() for response in task_responses]

        progress_response = await client.patch(f"/tasks/{tasks[1]['id']}/status", json={"status": "in_progress"})
        done_response = await client.patch(f"/tasks/{tasks[2]['id']}/status", json={"status": "done"})
        assert progress_response.status_code == 200
        assert done_response.status_code == 200

        list_response = await client.get(f"/users/{user['id']}/tasks")
        assert list_response.status_code == 200
        assert len(list_response.json()["tasks"]) == 3

        done_filter_response = await client.get(f"/users/{user['id']}/tasks", params={"status": "done"})
        assert done_filter_response.status_code == 200
        assert len(done_filter_response.json()["tasks"]) == 1

        stats_response = await client.get(f"/users/{user['id']}/tasks/stats")
        assert stats_response.status_code == 200
        assert stats_response.json() == {"total": 3, "new": 1, "in_progress": 1, "done": 1, "cancelled": 0}

    delete_response = await client.delete(f"/tasks/{tasks[0]['id']}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"ok": True}


async def test_create_task_requires_existing_user(client: AsyncClient) -> None:
    response = await client.post("/users/999/tasks", json={"title": "Missing user task_obj"})

    assert response.status_code == 404
    assert response.json()["detail"] == "UserModel not found error"


async def test_invalid_status_returns_validation_details(client: AsyncClient) -> None:
    response = await client.patch("/tasks/1/status", json={"status": "unknown"})

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail[0]["param"] == "status"
    assert detail[0]["value"] == "unknown"
