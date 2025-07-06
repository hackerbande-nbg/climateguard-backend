alias quandevkill="docker compose down -v"

alias quantest="python3 -m pytest test/integration/"

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

    echo "⏱️ Waiting a moment for services to stabilize..."
    # Parameters
    NUM_OS=${1:-20}         # num of  "o"s
    DELAY=${2:-0.1}        # seconds between prints

    progress=""
    for ((i=1; i<=NUM_OS; i++)); do
        progress+="⌛"
        printf "\r%s" "$progress"
        sleep $DELAY
    done

    echo ""
    echo ""
    echo "🧪 Running tests..."
    python3 -m pytest --tb=short --quiet --junit-xml=dev_testauto_results.xml
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
    
    # Only show detailed results if tests were successful
    if [ $test_exit_code -eq 0 ] && [ -f "dev_testauto_results.xml" ]; then
        # Extract test summary from XML
        failures=$(grep -o 'failures="[0-9]*"' dev_testauto_results.xml | grep -o '[0-9]*' | head -1)
        errors=$(grep -o 'errors="[0-9]*"' dev_testauto_results.xml | grep -o '[0-9]*' | head -1)
        
        # Handle empty values
        failures=${failures:-0}
        errors=${errors:-0}
        
        # Only show details if there are failures or errors
        if [ $failures -gt 0 ] || [ $errors -gt 0 ]; then
            total_tests=$(grep -o 'tests="[0-9]*"' dev_testauto_results.xml | grep -o '[0-9]*' | head -1)
            total_tests=${total_tests:-0}
            passed=$((total_tests - failures - errors))
            
            echo ""
            echo "📊 Test Results Overview:"
            echo "========================"
            echo "📈 Total Tests: $total_tests"
            echo "✅ Passed: $passed"
            echo "❌ Failed: $failures"
            echo "⚠️  Errors: $errors"
            echo "========================"
            
            # Show pass rate
            if [ $total_tests -gt 0 ]; then
                pass_rate=$(( (passed * 100) / total_tests ))
                echo "🎯 Pass Rate: $pass_rate%"
            fi

        fi
    fi
}