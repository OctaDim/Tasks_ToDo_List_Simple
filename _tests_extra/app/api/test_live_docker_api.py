from __future__ import annotations

import errno
import os
import socket
import time

import httpx
import pytest

BASE_URL = os.getenv("LIVE_API_BASE_URL", "http://127.0.0.1:8000")


def _skip_when_loopback_tcp_is_blocked() -> None:
    host = "127.0.0.1"
    port = 8000

    try:
        with socket.create_connection((host, port), timeout=1.0):
            return
    except OSError as exc:
        if exc.errno in {errno.EPERM, errno.EACCES}:
            pytest.skip(
                "Live API smoke test requires loopback TCP access, but the "
                "current runtime blocks connections to 127.0.0.1:8000."
            )


def _request(
        client: httpx.Client,
        method: str,
        path: str,
        expected_status: int,
        **kwargs,
) -> dict:
    response = client.request(method=method, url=path, **kwargs)
    assert response.status_code == expected_status, response.text
    if response.content:
        return response.json()
    return {}


def test_live_docker_api_end_to_end() -> None:
    _skip_when_loopback_tcp_is_blocked()

    unique_suffix = str(time.time_ns())
    statuses_plan = ("new", "in_progress", "done")
    expected_paths = {
        "/users",
        "/users/{user_id}",
        "/users/{user_id}/tasks",
        "/users/{user_id}/tasks/stats",
        "/tasks/{task_id}",
        "/tasks/{task_id}/status",
    }

    with httpx.Client(base_url=BASE_URL, timeout=15.0) as client:
        openapi = _request(client, "GET", "/openapi.json", 200)
        assert expected_paths.issubset(set(openapi["paths"]))

        users_payloads = [
            {
                "email": f"live-user-1-{unique_suffix}@example.com",
                "name": "Live User 1",
            },
            {
                "email": f"live-user-2-{unique_suffix}@example.com",
                "name": "Live User 2",
            },
            {
                "email": f"live-user-3-{unique_suffix}@example.com",
                "name": "Live User 3",
            },
        ]

        created_users: list[dict] = []
        created_tasks_by_user: dict[int, list[dict]] = {}

        for user_payload in users_payloads:
            created_user = _request(client, "POST", "/users", 201, json=user_payload)
            created_users.append(created_user)

            loaded_user = _request(
                client,
                "GET",
                f"/users/{created_user['id']}",
                200,
            )
            assert loaded_user["email"] == user_payload["email"]
            assert loaded_user["name"] == user_payload["name"]

            created_tasks_by_user[created_user["id"]] = []

            for index, planned_status in enumerate(statuses_plan, start=1):
                created_task = _request(
                    client,
                    "POST",
                    f"/users/{created_user['id']}/tasks",
                    201,
                    json={
                        "title": f"Task {index} for user {created_user['id']}",
                        "description": (
                            f"Live docker smoke task {index} "
                            f"for user {created_user['id']}"
                        ),
                    },
                )

                if planned_status != "new":
                    created_task = _request(
                        client,
                        "PATCH",
                        f"/tasks/{created_task['id']}/status",
                        200,
                        json={"status": planned_status},
                    )

                assert created_task["status"] == planned_status
                created_tasks_by_user[created_user["id"]].append(created_task)

            user_tasks = _request(
                client,
                "GET",
                f"/users/{created_user['id']}/tasks",
                200,
            )
            assert len(user_tasks["tasks"]) == 3

            for planned_status in statuses_plan:
                filtered_tasks = _request(
                    client,
                    "GET",
                    f"/users/{created_user['id']}/tasks",
                    200,
                    params={"status": planned_status, "limit": 10, "offset": 0},
                )
                assert len(filtered_tasks["tasks"]) == 1
                assert filtered_tasks["tasks"][0]["status"] == planned_status

            user_stats = _request(
                client,
                "GET",
                f"/users/{created_user['id']}/tasks/stats",
                200,
            )
            assert user_stats == {
                "total": 3,
                "new": 1,
                "in_progress": 1,
                "done": 1,
                "cancelled": 0,
            }

        delete_probe_user = created_users[0]
        delete_probe_task = _request(
            client,
            "POST",
            f"/users/{delete_probe_user['id']}/tasks",
            201,
            json={
                "title": "Delete probe task",
                "description": "Disposable task for delete endpoint verification.",
            },
        )
        delete_result = _request(
            client,
            "DELETE",
            f"/tasks/{delete_probe_task['id']}",
            200,
        )
        assert delete_result == {"ok": True}
