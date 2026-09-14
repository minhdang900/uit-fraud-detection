#!/usr/bin/env bash
# Run the fraud-detection lab in Docker.
#   ./run.sh          build, start, wait for healthy, open browser
#   ./run.sh demo     print the whole result story to the terminal
#   ./run.sh test     run the test suite inside the container
#   ./run.sh verify   recompute every headline number from raw arrays
#   ./run.sh logs     follow container logs
#   ./run.sh stop     stop and remove the container
set -euo pipefail

cd "$(dirname "$0")"

# Thư mục bộ nộp bài nằm ở hai chỗ khác nhau tuỳ bản sao đang chạy:
#   - trong repo:        anh em cùng cấp  ../08-Nop-bai
#   - trong chính bộ nộp: là thư mục cha  ..
# Giải quyết ở đây để MỘT file docker-compose.yml dùng được cho cả hai, thay vì
# để hai bản sao trôi khác nhau. Logic này phản chiếu paths.bundle_dir().
if [ -d ../01-Bao-cao ]; then
  NOP_BAI_PATH=..
else
  NOP_BAI_PATH=../08-Nop-bai
fi
export NOP_BAI_PATH

# A committed token is a credential in git, and any page you visit could try
# it against localhost. Generate a random one per machine into .env, which is
# gitignored and which docker compose reads automatically.
if [ -n "${JUPYTER_TOKEN:-}" ]; then
  TOKEN="$JUPYTER_TOKEN"
elif [ -f .env ] && grep -q '^JUPYTER_TOKEN=' .env; then
  TOKEN="$(grep '^JUPYTER_TOKEN=' .env | cut -d= -f2-)"
else
  TOKEN="$(openssl rand -hex 24 2>/dev/null || python3 -c 'import secrets;print(secrets.token_hex(24))')"
  umask 077
  printf 'JUPYTER_TOKEN=%s\n' "$TOKEN" > .env
  echo "Generated a new token into .env (gitignored)."
fi
export JUPYTER_TOKEN="$TOKEN"
URL="http://localhost:8888/lab?token=${TOKEN}"

ensure_up() {
  if [ "$(docker inspect --format '{{.State.Running}}' uit-fraud-lab 2>/dev/null)" != "true" ]; then
    echo "Container is not running -- starting it first."
    docker compose up -d --build >/dev/null
    wait_healthy
  fi
}

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
    docker compose up -d --build
    wait_healthy
    echo
    echo "  JupyterLab : $URL"
    echo "  Token      : stored in .env"
    echo "  Tests      : ./run.sh test"
    echo
    open_browser "$URL"
    ;;
  demo)
    # Extra args pass through, e.g. ./run.sh demo --score 0.02 1500
    shift || true
    ensure_up
    docker compose exec -T lab python demo.py "$@"
    ;;
  test)
    ensure_up
    docker compose exec -T lab python -m pytest tests/ -v
    ;;
  verify)
    ensure_up
    docker compose exec -T lab python -c "
from verify_results import reproduce_headline
for k, v in reproduce_headline().items(): print(f'{k:<26} {v}')"
    ;;
  logs)
    docker compose logs -f lab
    ;;
  stop)
    docker compose down
    ;;
  *)
    echo "usage: ./run.sh [up|demo|test|verify|logs|stop]" >&2
    exit 1
    ;;
esac
