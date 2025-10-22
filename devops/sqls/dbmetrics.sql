INSERT INTO public.dbmetrics (
  snapshot_timestamp, db_name, db_size_bytes, active_connections,
  xact_commit, xact_rollback, blks_read, blks_hit, temp_files, temp_bytes, deadlocks
)
SELECT
  now() AS snapshot_timestamp,
  current_database() AS db_name,
  pg_database_size(current_database())::int4 AS db_size_bytes,
  (SELECT count(*) FROM pg_stat_activity WHERE datname = current_database())::int4 AS active_connections,
  xact_commit::int4,
  xact_rollback::int4,
  blks_read::int4,
  blks_hit::int4,
  temp_files::int4,
  temp_bytes::int4,
  deadlocks::int4
FROM pg_stat_database
WHERE datname = current_database();