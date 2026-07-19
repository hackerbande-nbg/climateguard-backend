.PHONY: test debug deploy help print-checkmarks db-migrate-generate db-migrate-copy db-migrate-apply db-mig-down

# Default target
help:
	@echo "Available targets:"
	@echo "  test               - Run integration tests"
	@echo "  debug              - Stop containers and start only database"
	@echo "  deploy             - Full deployment pipeline with linting, building, and testing"
	@echo "  db-migrate-generate - Generate new Alembic migration (use MSG='description')"
	@echo "  db-migrate-copy    - Copy migration files from container to local filesystem"
	@echo "  db-migrate-apply   - Apply database migrations using Alembic"
	@echo "  db-mig-down        - Downgrade to specified revision: make db-mig-down <revision_id>"
	@echo "  help               - Show this help message"

print-checkmarks:
	@echo ""
	@echo "✅"
	@echo "✅"
	@echo "✅ $(MSG)"
	@echo "✅"
	@echo "✅"
	@echo ""

test:
	@echo ""
	@echo "🧪 Running tests..."
	@python3 -m pytest -n 4 test/integration/

debug:
	@echo ""
	@docker compose down || true
	@docker compose up -d db

deploy:
	@$(MAKE) --no-print-directory _check-docker
	@$(MAKE) --no-print-directory print-checkmarks MSG="Docker installed"
	@$(MAKE) --no-print-directory _check-docker-daemon
	@sleep 1
	@$(MAKE) --no-print-directory print-checkmarks MSG="Docker Daemon running"
	@$(MAKE) --no-print-directory _lint
	@$(MAKE) --no-print-directory print-checkmarks MSG="Python Code linted"
	@$(MAKE) --no-print-directory _stop-containers
	@$(MAKE) --no-print-directory print-checkmarks MSG="containers stopped"
	@$(MAKE) --no-print-directory _build-containers
	@$(MAKE) --no-print-directory print-checkmarks MSG="containers rebuilt and restarted"
	@$(MAKE) --no-print-directory _run-migrations
	@$(MAKE) --no-print-directory print-checkmarks MSG="DB migrations done"
	@$(MAKE) --no-print-directory _bootstrap-users
	@$(MAKE) --no-print-directory print-checkmarks MSG="Bootstrap script executed"
	@$(MAKE) --no-print-directory _wait-services
	@$(MAKE) --no-print-directory _run-tests
	@$(MAKE) --no-print-directory print-checkmarks MSG="python tests executed"
	@sleep 1
	@$(MAKE) --no-print-directory print-checkmarks MSG="Deployment completed"
	@sleep 1
	@docker logs quantum_web_dev
	@$(MAKE) --no-print-directory _show-completion

_check-docker:
	@if ! command -v docker > /dev/null 2>&1; then \
		echo "❌ Docker is not installed or not in PATH. Aborting."; \
		exit 1; \
	fi

_check-docker-daemon:
	@if ! docker info > /dev/null 2>&1; then \
		echo "❌ Docker daemon is not running or accessible. Aborting."; \
		exit 1; \
	fi

_lint:
	@echo "🧹 Linting Python Code..."
	@flake8 --config=config/flake8.ini || { \
		echo "❌ Linting failed. Please fix the issues before deploying."; \
		exit 1; \
	}

_stop-containers:
	@echo "🔻 Stopping existing Docker containers..."
	@docker compose down || true

_build-containers:
	@echo "🛠️ Building and starting containers..."
	@docker compose up --build -d

_run-migrations:
	@echo "📦 Applying database migrations via alembic..."
	@docker exec quantum_web_dev alembic upgrade head || { \
		echo "❌ Alembic migration failed."; \
		exit 1; \
	}

_bootstrap-users:
	@echo "📦 Bootstrap test users in DB..."
	@docker compose exec -T web python app/bootstrap_test_users.py || { \
		echo "❌ Bootstrap script failed."; \
		exit 1; \
	}

_wait-services:
	@echo "⏱️ Waiting a moment for services to stabilize..."
	@progress=""; \
	for i in $$(seq 1 10); do \
		progress="$$progress⌛"; \
		printf "\r%s" "$$progress"; \
		sleep 0.05; \
	done; \
	echo ""; \
	echo ""

_run-tests:
	@echo "🧪 Running tests..."
	@python3 -m pytest -n 4 --tb=short --color=no || { \
		echo "❌ Some tests failed."; \
		exit 1; \
	}

_show-completion:
	@if [ -f .env ]; then \
		. ./.env; \
		echo ""; \
		echo "🚀 Deployment complete! You can now access the application."; \
		echo "Visit http://localhost:$$FASTAPI_PORT/v2/docs in your browser."; \
		echo ""; \
	else \
		echo ""; \
		echo "🚀 Deployment complete! You can now access the application."; \
		echo ""; \
	fi

db-mig-gen:
	@if [ -z "$(MSG)" ]; then \
		echo "❌ Please provide a migration message: make db-migrate-generate MSG='your description'"; \
		exit 1; \
	fi
	@echo "📝 Generating migration: $(MSG)"
	@docker exec quantum_web_dev alembic revision --autogenerate -m "$(MSG)"
	@echo "📋 Copying migration files from container to local filesystem..."
	@docker cp quantum_web_dev:/usr/src/app/migrations/versions/. ./project/migrations/versions/
	@echo "✅ Migration files copied successfully"

db-mig-apply:
	@echo "📦 Applying database migrations via alembic..."
	@docker exec quantum_web_dev alembic upgrade head
	@echo "✅ Database migrations applied successfully"

db-mig-down:
	@if [ -z "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
		echo "❌ Please provide a revision ID: make db-mig-down <revision_id>"; \
		echo "💡 Use 'base' to downgrade to initial state"; \
		echo "💡 Use '-1' to downgrade by one revision"; \
		echo "💡 Use specific revision ID to downgrade to that revision"; \
		exit 1; \
	fi
	@echo "📉 Downgrading database to revision: $(filter-out $@,$(MAKECMDGOALS))"
	@docker exec quantum_web_dev alembic downgrade $(filter-out $@,$(MAKECMDGOALS))
	@echo "✅ Database downgraded successfully to revision: $(filter-out $@,$(MAKECMDGOALS))"

# Catch-all target to handle revision arguments
%:
	@:
