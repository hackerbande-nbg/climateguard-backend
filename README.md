# Quantum Telemetry

# Overview
Quantum Telemetry is a FastAPI-based application designed to collect, store, and retrieve sensor metrics. It uses PostgreSQL as the database and provides RESTful endpoints for interacting with the data.

# Features
- **/ping**: Health check endpoint to verify the service is running.
- **/sensormetrics**: 
  - `GET`: Retrieve all sensor metrics.
  - `POST`: Add a new sensor metric.

# Project Structure
- **project/app**: Contains the FastAPI application code.
  - `main.py`: Defines the API endpoints.
  - `db.py`: Handles database initialization and session management.
  - `models.py`: Defines the database models using SQLModel.
- **test/int**: Contains integration tests for the application.
- **config**: Stores configuration files like `test_config.json`.

# Components
1. **FastAPI Application**:
   - Provides RESTful APIs for sensor metrics.
   - Runs on Uvicorn server.
2. **PostgreSQL Database**:
   - Stores sensor metrics.
   - Managed via Docker Compose.
3. **Docker Compose**:
   - Orchestrates the application and database containers.
   - Configured in `docker-compose.yml`.
4. **Environment Variables**:
   - Managed via `.env.stage` and `.env.prod` files.

# Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/hackerbande-nbg/climateguard-backend.git
   cd quantum-telemetry
   ```

2. Create and configure `.env` files:
   - `.env` for development.
   
3. Build and run the application using Docker Compose:
   ```bash
   docker-compose up --build
   ```

4. Access the application:
   - FastAPI: `http://localhost:<FASTAPI_PORT>`

# Endpoints
- **GET /ping**: Returns `{"ping": "pong!"}`.
- **GET /sensormetrics**: Retrieves all sensor metrics.
- **POST /sensormetrics**: Adds a new sensor metric. Example payload:
  ```json
  {
      "timestamp_device": 1617184800,
      "timestamp_server": 1617184800,
      "device_id": "lora_test_1",
      "temperature": 22.5,
      "humidity": 45.0,
      "rssi": -70
  }
  ```

# Notes
- Ensure the database is running before starting the application.
- Use the provided `test_config.json` for testing configurations.

## CICD

via github

# Envs 

All env vars are maintained in vaultwarden.
https://vault.hackerban.de/


Prod api link: https://api.quantum.hackerban.de/docs/docs

The following variables are required(example from dev):
```bash
FASTAPI_PORT=8001
QUANTUM_ENV=dev
POSTGRES_USER=postgres
POSTGRES_PW=postgres
POSTGRES_DB=quantum
POSTGRES_DNS=quantum_postgres
DB_PORT=5432
```

the credentials and DB names have to be adjusted for stage and prod

## How to run on dev

see also devops/dev_functions.sh

1. Clone the repository:
    ```sh
    git clone <repository_url>
    cd <repository_directory>
    ```

1. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

1. Set up the environment variables:
    Ensure you have a `.env` file in the `infra/quantum_dev` directory with the following content:
    ```dotenv
    POSTGRES_USER=quantum
    POSTGRES_PW=LOCAL_DEV_PW
    POSTGRES_DB=quantum
    POSTGRES_PORT=5432
    POSTGRES_DNS=quantum_postgres
    ```
   
1. Build the containers:
    ```sh
    docker compose up --build
    ```

1. Initialize alembic (only required once per repo, done already)
    ```sh
    docker exec quantum_web_dev alembic init -t async migrations
    ```

1. generate alembic migration
    ```sh
    docker exec quantum_web_dev alembic revision --autogenerate -m "YOUR_NAME"
    ```
1. check if the migration looks good (with your eyes on code)

1. apply a alembic migration
    ```sh
    docker exec quantum_web_dev alembic upgrade head
    ```
## Run on stage

Will be triggered by jenkins pipeline in devops/run_stage.groovy

Pipelines are maintained in jenkins folder "prod_quantum_telemetry"
Relevant secret: quantum_stage_dotenv

# demo curl for inserting values
```bash
curl -d '{ "timestamp_device": 1617184800,"timestamp_server": 1617184800,"device_id": 1,"temperature": 22.5,"humidity": 45.0}' -H "Content-Type: application/json" -X POST http://localhost:9301/sensormetrics
```

# Testing commands

kill everything:
docker compose down -v; docker compose up --build -d; docker ps

quandeploy:
docker compose down; docker compose up --build -d; docker exec quantum_web_dev alembic upgrade head; sleep 2;python3 -m pytest test/integration/; docker logs quantum_web_dev

alias quandeploy="docker compose down; docker compose up --build -d; docker exec quantum_web_dev alembic upgrade head; sleep 2;python3 -m pytest test/integration/; sleep 2; docker logs quantum_web_dev"

alias quantest="python3 -m pytest test/integration/"

# DB ops

## list all DBs
```bash
docker exec -it quantum_db_prod bash
psql -U postgres -c "\l"
```

## disconnect all users
```bash
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'foo' AND pid <> pg_backend_pid();
```