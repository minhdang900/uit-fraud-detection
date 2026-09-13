#!/usr/bin/env bash
# Run the fraud-detection lab in Docker.
#   ./run.sh          build, start, wait for healthy, open browser
#   ./run.sh test     run the test suite inside the container
#   ./run.sh logs     follow container logs
#   ./run.sh stop     stop and remove the container
set -euo pipefail

cd "$(dirname "$0")"
TOKEN="${JUPYTER_TOKEN:-uit-fraud}"
URL="http://localhost:8888/lab?token=${TOKEN}"

open_browser() {
  case "$(uname -s)" in
    Darwin) open "$1" ;;
    Linux)  xdg-open "$1" >/dev/null 2>&1 || true ;;
    *)      echo "Open manually: $1" ;;
  esac
}

wait_healthy() {
  printf 'Waiting for JupyterLab to become healthy'
  for _ in $(seq 1 60); do
    status=$(docker inspect --format '{{.State.Health.Status}}' uit-fraud-lab 2>/dev/null || echo starting)
    if [ "$status" = "healthy" ]; then
      printf ' ready\n'
      return 0
    fi
    printf '.'
    sleep 2
  done
  printf '\n'
  echo "Never became healthy. Recent logs:" >&2
  docker compose logs --tail=30 lab >&2
  return 1
}

case "${1:-up}" in
  up)
    JUPYTER_TOKEN="$TOKEN" docker compose up -d --build
    wait_healthy
    echo
    echo "  JupyterLab : $URL"
    echo "  Token      : $TOKEN"
    echo "  Tests      : ./run.sh test"
    echo
    open_browser "$URL"
    ;;
  test)
    docker compose exec -T lab python -m pytest tests/ -v
    ;;
  logs)
    docker compose logs -f lab
    ;;
  stop)
    docker compose down
    ;;
  *)
    echo "usage: ./run.sh [up|test|logs|stop]" >&2
    exit 1
    ;;
esac
