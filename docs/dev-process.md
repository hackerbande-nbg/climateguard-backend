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
    copy the migration from the container to the local filesystem, e.g.
    docker cp quantum_web_dev:/usr/src/app/migrations/versions/. ./project/migrations/versions/
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
   docker compose down
   docker compose up db -d
   ```

2. **Debug FastAPI application**:
   - In VS Code, go to Run and Debug (Ctrl+Shift+D)
   - Select "Python Debugger: FastAPI" 
   - Start debugging (F5)
   - This will start the FastAPI server on http://localhost:8001

3. **Debug integration tests**:
   - While FastAPI is running in debug mode
   - Select "Python Debugger: Test integration" configuration
   - Start the second debugger (F5)
   - This will run the integration tests against the local FastAPI instance

**Note**: Make sure the database is running on localhost:5432 before starting the debuggers. The launch configurations are set up with the necessary environment variables for local development.


# Adding a New Field to Database

This guide walks you through the complete process of adding a new database field and making it available through the API.

## Prerequisites
- Ensure you're on the main branch
- Have a clean development environment

## Step-by-Step Process

### 1. Prepare Clean Environment
```bash
# Switch to main branch and delete dev branch (connected to CI pipeline)
git checkout main
git branch -D dev  # if exists

# Reset database volume for a clean slate
docker volume rm $(docker volume ls -q)
```

### 2. Verify Current Environment
Test that the current environment works without any changes:
```bash
quandeploy
```
> ⚠️ **Important**: Make sure everything ramps up properly before proceeding.

### 3. Add Field to Data Model
Edit the database model in `project/app/models.py`:
- Add your new field
- **Decision Point**: Determine if the field should be optional or required
- Consider database constraints and default values

### 4. Generate Database Migration
Create an Alembic migration for your changes:
```bash
# Generate migration (replace YOUR_FIELD_NAME with descriptive name)
docker exec quantum_web_dev alembic revision --autogenerate -m "add optional YOUR_FIELD_NAME field"
```

### 5. Copy Migration Files
Transfer the generated migration to your local filesystem:
```bash
# Copy migration files from container to local
docker cp quantum_web_dev:/usr/src/app/migrations/versions/. ./project/migrations/versions/
```

### 6. Apply Database Migration
Update the database schema:
```bash
docker exec quantum_web_dev alembic upgrade head
```

### 7. Update API Layer
Make the following changes to expose your new field:

- **API Endpoints**: Update relevant endpoints in `project/app/v***`
- **Schemas**: Modify schema objects in `project/app/schemas.py`
- **Tests**: Update tests in `test/integration/` and/or `test/prod/`

### 8. Deploy and Test
Run a complete deployment to verify everything works:
```bash
quandeploy
```

## Verification Checklist
- [ ] Database migration applied successfully
- [ ] API endpoints return new field
- [ ] All tests pass
- [ ] No breaking changes for existing clients
- [ ] Documentation updated (if needed)

## Troubleshooting
If you encounter issues:
1. Check migration file for correctness
2. Verify field names match between model and schema
3. Ensure proper data types are used
4. Check for any missing imports or dependencies
