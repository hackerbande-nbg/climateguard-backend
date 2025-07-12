print_checkmarks() {
  local message="$1"
  echo ""
  echo "✅"
  echo "✅"
  echo "✅ $message"
  echo "✅"
  echo "✅"  
  echo ""
} 

quantest() {
    echo ""
    echo "🧪 Running tests..."
    python3 -m pytest -n 4 test/integration/
}

quandebug() {
    echo ""
    docker compose down || true
    docker compose up -d db
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

    # Lint
    echo "🧹 Linting Python Code..."
    flake8 --config=config/flake8.ini || {
        echo "❌ Linting failed. Please fix the issues before deploying."
        return 1
    }
    print_checkmarks "Python Code linted"

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

    echo "📦 Bootstrap test users in DB..."
    python project/app/bootstrap_test_users.py || {
        echo "❌ Bootstrap script failed."
        return 1
    }
    print_checkmarks "Bootstrap script executed"

    echo "⏱️ Waiting a moment for services to stabilize..."
    # Parameters
    NUM_OS=${1:-10 }         # num of  "o"s
    DELAY=${2:-0.05}        # seconds between prints

    progress=""
    for ((i=1; i<=NUM_OS; i++)); do
        progress+="⌛"
        printf "\r%s" "$progress"
        sleep $DELAY
    done

    echo ""
    echo ""
    echo "🧪 Running tests..."
    python3 -m pytest -n 4 --tb=short --quiet
    test_exit_code=$?
    
    if [ $test_exit_code -ne 0 ]; then
        echo "❌ Some tests failed."
        return 1
    fi
    
    print_checkmarks "python tests executed"
    sleep 1
    print_checkmarks "Deployment completed"

    sleep 1;

    docker logs quantum_web_dev

    source .env

    echo ""
    echo "🚀 Deployment complete! You can now access the application."
    echo "Visit http://localhost:$FASTAPI_PORT/v2/docs in your browser."
    echo ""
    
}