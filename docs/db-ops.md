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
## Connect to prod DB

ssh -L 5433:localhost:5432 $USER@quan

## set new pw

psql -h localhost -p 5431 -d postgres -U postgres -c "ALTER USER postgres WITH PASSWORD '237894nd';"
