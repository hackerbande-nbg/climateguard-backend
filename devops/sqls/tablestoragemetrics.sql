-- TABLE STORAGE METRICS
INSERT INTO public.tablestoragemetrics (
  snapshot_timestamp, schemaname, tablename, relid,
  total_bytes, table_bytes, index_bytes, toast_bytes
)
SELECT
  now() AS snapshot_timestamp,
  n.nspname AS schemaname,
  c.relname AS tablename,
  c.oid::int4 AS relid,
  pg_total_relation_size(c.oid)::int4 AS total_bytes,
  pg_relation_size(c.oid)::int4 AS table_bytes,
  pg_indexes_size(c.oid)::int4 AS index_bytes,
  COALESCE(pg_total_relation_size(c.reltoastrelid), 0)::int4 AS toast_bytes
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind IN ('r','m')            -- ordinary, materialized views-as-tables
  AND n.nspname NOT IN ('pg_catalog','information_schema');