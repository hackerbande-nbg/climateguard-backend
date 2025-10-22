INSERT INTO public.tableactivitymetrics (
  snapshot_timestamp, schemaname, tablename, relid,
  seq_scan, idx_scan, n_tup_ins, n_tup_upd, n_tup_del, n_tup_hot_upd,
  n_dead_tup, last_vacuum, last_autovacuum, last_analyze, last_autoanalyze
)
SELECT
  now() AS snapshot_timestamp,
  schemaname,
  relname      AS tablename,
  relid::int4  AS relid,
  seq_scan::int4,
  idx_scan::int4,
  n_tup_ins::int4,
  n_tup_upd::int4,
  n_tup_del::int4,
  n_tup_hot_upd::int4,
  n_dead_tup::int4,
  last_vacuum::timestamp,
  last_autovacuum::timestamp,
  last_analyze::timestamp,
  last_autoanalyze::timestamp
FROM pg_stat_user_tables;