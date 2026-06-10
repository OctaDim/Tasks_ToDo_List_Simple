from pathlib import Path
import shutil
import subprocess

import pytest


ROOT_DIR = Path(__file__).resolve().parents[2]


def _read_env_file(env_path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip()
    return values


def test_postgres_env_file_contains_runtime_keys() -> None:
    values = _read_env_file(ROOT_DIR / "docker_compose" / ".env.postgres")

    assert values["POSTGRES_DB_NAME"]
    assert values["POSTGRES_DB"] == values["POSTGRES_DB_NAME"]
    assert values["POSTGRES_USER"]
    assert values["POSTGRES_PASSWORD"]
    assert values["POSTGRES_HOST"] == "127.0.0.1"
    assert values["POSTGRES_HOST_PORT"] == values["POSTGRES_PORT"]


def test_api_uvicorn_env_file_contains_compact_key_value_pairs() -> None:
    env_path = ROOT_DIR / "docker_compose" / ".env.api_uvicorn"
    values = _read_env_file(env_path)

    assert values == {
        "API_PUBLISH_HOST": "127.0.0.1",
        "API_HOST": "0.0.0.0",
        "API_PORT": "8000",
    }
    assert " = " not in env_path.read_text(encoding="utf-8")


def test_root_compose_references_expected_env_files_and_dockerfile() -> None:
    compose_text = (ROOT_DIR / "docker-compose.yaml").read_text(
        encoding="utf-8"
    )

    assert "docker_compose/.env.postgres" in compose_text
    assert "docker_compose/.env.api_uvicorn" in compose_text
    assert "dockerfile: docker_compose/Dockerfile" in compose_text
    assert (
        '${POSTGRES_HOST:-127.0.0.1}:${POSTGRES_HOST_PORT:-15433}:'
        '${POSTGRES_PORT:-15433}'
    ) in compose_text
    assert (
        '${API_PUBLISH_HOST:-127.0.0.1}:${API_PORT:-8000}:${API_PORT:-8000}'
    ) in compose_text
    assert "POSTGRES_HOST: db" in compose_text


def test_dockerfile_uses_api_host_and_port_environment_defaults() -> None:
    dockerfile_text = (ROOT_DIR / "docker_compose" / "Dockerfile").read_text(
        encoding="utf-8"
    )

    assert "uvicorn main:app" in dockerfile_text
    assert "API_HOST:-0.0.0.0" in dockerfile_text
    assert "API_PORT:-8000" in dockerfile_text
    assert "alembic -c alembic/alembic.ini upgrade head" in dockerfile_text


def test_root_compose_is_renderable() -> None:
    if shutil.which("docker") is None:
        pytest.skip(
            "Docker CLI is unavailable in the current runtime; "
            "compose renderability is a host-side contract check."
        )

    result = subprocess.run(
        [
            "docker",
            "compose",
            "--env-file",
            "docker_compose/.env.postgres",
            "--env-file",
            "docker_compose/.env.api_uvicorn",
            "config",
            "--quiet",
        ],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        check=False,
    )

    combined_output = f"{result.stdout}\n{result.stderr}"
    if (
        "could not be found in this WSL 2 distro" in combined_output
        or "activate the WSL integration in Docker Desktop settings" in combined_output
    ):
        pytest.skip(
            "Docker CLI stub is present, but Docker Desktop WSL integration is "
            "not available in the current runtime."
        )

    assert result.returncode == 0, result.stderr
