alias quandevkill="docker compose down -v"

alias quantest="python3 -m pytest test/integration/"

print_checkmarks() {
  local message="$1"
  echo ""
  echo "✅"
  echo "✅ $message"
  echo "✅"
  echo ""
}

quandeploy() {
    unset FASTAPI_PORT
    unset DB_PORT
    unset QUANTUM_ENV

    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed or not in PATH. Aborting."
        return 1
    fi

    print_checkmarks "Docker installed"

    # Check if docker daemon is running
    if ! docker info &> /dev/null; then
        echo "❌ Docker daemon is not running or accessible. Aborting."
        return 1
    fi
    sleep 1

    print_checkmarks "Docker Daemon running"

    echo "🔻 Stopping existing Docker containers..."
    docker compose down || true
    print_checkmarks "containers stopped"

    echo "🛠️ Building and starting containers..."
    docker compose up --build -d
    print_checkmarks "containers rebuilt and restarted"

    echo "📦 Applying database migrations via alembic..."
    docker exec quantum_web_dev alembic upgrade head || {
        echo "❌ Alembic migration failed."
        return 1
    }
    print_checkmarks "DB migrations done"

    echo "⏱️ Waiting a moment for services to stabilize..."
    sleep 2

    echo "🧪 Running tests..."
    python3 -m pytest || {
        echo "❌ Some tests failed."
    }
    print_checkmarks "python tests executed"
    sleep 1
    print_checkmarks "Deployment completed"

    sleep 1;

    docker logs quantum_web_dev
}