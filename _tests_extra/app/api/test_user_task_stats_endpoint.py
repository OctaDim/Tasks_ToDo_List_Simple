from httpx import AsyncClient


async def test_user_task_stats_returns_counts_for_each_status(client: AsyncClient) -> None:
    user_response = await client.post("/users", json={"email": "stats-check@example.com", "name": "Stats Check"})
    assert user_response.status_code == 201
    user = user_response.json()

    new_task_response = await client.post(f"/users/{user['id']}/tasks", json={"title": "New task"})
    in_progress_task_response = await client.post(
        f"/users/{user['id']}/tasks",
        json={"title": "In progress task"},
    )
    done_task_response = await client.post(f"/users/{user['id']}/tasks", json={"title": "Done task"})
    cancelled_task_response = await client.post(f"/users/{user['id']}/tasks", json={"title": "Cancelled task"})

    assert [response.status_code for response in [
        new_task_response,
        in_progress_task_response,
        done_task_response,
        cancelled_task_response,
    ]] == [201, 201, 201, 201]

    in_progress_task = in_progress_task_response.json()
    done_task = done_task_response.json()
    cancelled_task = cancelled_task_response.json()

    assert (await client.patch(
        f"/tasks/{in_progress_task['id']}/status",
        json={"status": "in_progress"},
    )).status_code == 200
    assert (await client.patch(
        f"/tasks/{done_task['id']}/status",
        json={"status": "done"},
    )).status_code == 200
    assert (await client.patch(
        f"/tasks/{cancelled_task['id']}/status",
        json={"status": "cancelled"},
    )).status_code == 200

    response = await client.get(f"/users/{user['id']}/tasks/stats")

    assert response.status_code == 200
    assert response.json() == {
        "total": 4,
        "new": 1,
        "in_progress": 1,
        "done": 1,
        "cancelled": 1,
    }


async def test_user_task_stats_returns_zero_counts_for_user_without_tasks(client: AsyncClient) -> None:
    user_response = await client.post("/users", json={"email": "empty-stats@example.com", "name": "Empty Stats"})
    assert user_response.status_code == 201
    user = user_response.json()

    response = await client.get(f"/users/{user['id']}/tasks/stats")

    assert response.status_code == 200
    assert response.json() == {
        "total": 0,
        "new": 0,
        "in_progress": 0,
        "done": 0,
        "cancelled": 0,
    }


async def test_user_task_stats_returns_not_found_for_missing_user(client: AsyncClient) -> None:
    response = await client.get("/users/999/tasks/stats")

    assert response.status_code == 404
    assert response.json()["detail"] == "UserModel not found error"
