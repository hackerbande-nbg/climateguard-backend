# Dev Process 

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

# Testing commands

kill everything:
docker compose down -v; docker compose up --build -d; docker ps

quandeploy:
docker compose down; docker compose up --build -d; docker exec quantum_web_dev alembic upgrade head; sleep 2;python3 -m pytest test/integration/; docker logs quantum_web_dev

alias quandeploy="docker compose down; docker compose up --build -d; docker exec quantum_web_dev alembic upgrade head; sleep 2;python3 -m pytest test/integration/; sleep 2; docker logs quantum_web_dev"

alias quantest="python3 -m pytest test/integration/"


# Debugging

For local development and debugging in VS Code, check the launch.json and the .env file given as examples
Process for local debugging:

1. **Start PostgreSQL database first**:
   ```bash
   # Run only the database container
   docker-compose up db -d
   ```

2. **Debug FastAPI application**:
   - In VS Code, go to Run and Debug (Ctrl+Shift+D)
   - Select "Python Debugger: FastAPI" 
   - Start debugging (F5)
   - This will start the FastAPI server on http://localhost:8001

3. **Debug integration tests**:
   - While FastAPI is running in debug mode
   - Select "Python Debugger: Test Metrics" configuration
   - Start the second debugger (F5)
   - This will run the integration tests against the local FastAPI instance

**Note**: Make sure the database is running on localhost:5432 before starting the debuggers. The launch configurations are set up with the necessary environment variables for local development.