# 2.3.0

- add air_pressure field
- [docs/changes/air_pressure.md](docs/changes/air_pressure.md)

# 2.2.0

- add auth
- [docs/changes/auth.md](docs/changes/auth.md)

# 2.1.0

- add /metrics endpoint with date filtering and limits
- add pagination to /metrics endpoint when more than LIMIT entries exist
- add comprehensive pagination tests and integration tests
- add README-example-calls.md for some curl examples
- add .env file and example launch.json

# 2.0.0

- add changelog at CHANGELOG.md
- add API versioning via URLs (/v1 and /v2)
- add max return limit for https://api.quantum.hackerban.de/v2/sensormetrics
- add max return limit for https://api.quantum.hackerban.de/v1/sensormetrics
- add openAPI spec https://api.quantum.hackerban.de/v2/docs
- add redoc endpoint https://api.quantum.hackerban.de/v2/redoc
- beautify the deploy script devops/dev_functions.sh /to be replaced by uv native commands)
- add test env creation scripts that creates randomly entries at test/manual/create_test_metrics.py


# 1.0.0

- First productive version
- supports /sensormetrics endpoint