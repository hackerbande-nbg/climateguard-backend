INSERT INTO public.indexactivitymetrics (
  snapshot_timestamp, schemaname, tablename, indexname,
  indexrelid, relid, idx_scan, idx_tup_read, idx_tup_fetch
)
SELECT
  now() AS snapshot_timestamp,
  schemaname,
  relname        AS tablename,
  indexrelname   AS indexname,
  indexrelid::int4 AS indexrelid,
  relid::int4      AS relid,
  idx_scan::int4,
  idx_tup_read::int4,
  idx_tup_fetch::int4
FROM pg_stat_user_indexes;