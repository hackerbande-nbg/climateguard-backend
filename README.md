# Quantum Telemetry

# Overview
Quantum Telemetry is a FastAPI-based application designed to collect, store, and retrieve sensor metrics. It uses PostgreSQL as the database and provides RESTful endpoints for interacting with the data.

# Changelog

Check out: [CHANGELOG.md](CHANGELOG.md)

# Features
- **/ping**: Health check endpoint to verify the service is running.
- **/sensormetrics**: 
  - `GET`: Retrieve all sensor metrics.
  - `POST`: Add a new sensor metric.
- **/metrics**: 
  - `GET`: Retrieve sensor metrics with optional date filtering and pagination.

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
- **GET /sensormetrics**: Retrieves latest 100 sensor metrics.
- **GET /metrics**: Retrieves sensor metrics with optional filtering:
  - `min_date`: Minimum date filter (Unix timestamp or ISO string)
  - `max_date`: Maximum date filter (Unix timestamp or ISO string)  
  - `limit`: Number of records to return (default: 100, max: 1000)
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



