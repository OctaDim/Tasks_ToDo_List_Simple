from pathlib import Path
import re
import subprocess


ROOT_DIR = Path(__file__).resolve().parents[2]
MAKEFILE_PATH = ROOT_DIR / "Makefile"


def test_makefile_exists_with_curated_targets() -> None:
    makefile_text = MAKEFILE_PATH.read_text(encoding="utf-8")

    assert "docker_compose/.env.postgres" in makefile_text
    assert "docker_compose/.env.api_uvicorn" in makefile_text

    expected_targets = {
        "help",
        "up",
        "up-d",
        "local-python",
        "urls",
        "swagger",
        "redoc",
        "json",
        "openapi-status",
        "down",
        "restart",
        "ps",
        "docker-logs",
        "api-logs",
        "db-logs",
        "docker-config",
        "migrate",
        "test",
        "test-basic",
        "test-extra",
        "test-compose",
        "test-local",
        "test-local-basic",
        "test-local-extra",
        "ruff",
        "ruff-fix",
        "ruff-format-check",
        "ruff-format-fix",
        "mypy",
        "global-check",
    }

    discovered_targets = set(
        re.findall(r"^([a-zA-Z0-9_.-]+):(?:.*## .*)?$", makefile_text, re.MULTILINE)
    )

    assert expected_targets.issubset(discovered_targets)
    assert "awk 'BEGIN {FS = \":.*## \"}" in makefile_text
    assert "load_env_file()" in makefile_text
    assert 'printf -v "$$key" "%s" "$$value"' in makefile_text
    assert "$(COMPOSE) up -d db" in makefile_text
    assert 'pg_isready -h 127.0.0.1 -p "$${POSTGRES_PORT:-15433}"' in makefile_text
    assert "$(PYTHON) -m alembic -c alembic/alembic.ini upgrade head" in makefile_text
    assert "exec $(PYTHON) -m uvicorn main:app" in makefile_text


def test_makefile_local_env_loader_preserves_shell_special_characters(
    tmp_path: Path,
) -> None:
    env_file = tmp_path / ".env.test"
    env_file.write_text(
        "POSTGRES_PASSWORD=be2_happy3_%~^&!%\nAPI_HOST=0.0.0.0\n",
        encoding="utf-8",
    )

    shell_program = """
load_env_file() {
  while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in
      ""|\\#*) continue ;;
      *=*)
        key=${line%%=*}
        value=${line#*=}
        printf -v "$key" "%s" "$value"
        export "$key"
        ;;
    esac
  done < "$1"
}
load_env_file "$1"
printf '%s\\n%s\\n' "$POSTGRES_PASSWORD" "$API_HOST"
"""
    completed = subprocess.run(
        ["bash", "-lc", shell_program, "bash", str(env_file)],
        check=True,
        capture_output=True,
        text=True,
    )

    assert completed.stdout.splitlines() == [
        "be2_happy3_%~^&!%",
        "0.0.0.0",
    ]
