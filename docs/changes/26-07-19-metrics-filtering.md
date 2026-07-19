# Metrics filtering by devices or tags

## Why

`GET /v2/devices` could select devices by tag, but `GET /v2/metrics` could not
use that selection. It queried every metric in the requested time range, so
clients had to download mixed-device pages and filter them afterward. This did
not scale with many sensors reporting every few seconds.

## What changed

`GET /v2/metrics` now supports two mutually exclusive filter modes:

- Supply `device_ids` as a comma-separated list to select one or more devices.
- Supply both `tag_category` and `tag_name` to select devices by an exact tag.

The selected filter is applied to both the returned rows and the pagination
count. Existing calls without a device or tag filter remain valid. Mixing the
two modes, supplying only half of a tag pair, or supplying malformed device IDs
returns HTTP 422. Device IDs must contain ASCII decimal digits and be between 1
and 1,000,000, matching the device API. Whitespace is trimmed and duplicate IDs
are harmlessly deduplicated.

Examples:

```text
GET /v2/metrics?device_ids=12,34
GET /v2/metrics?tag_category=device&tag_name=Annapark
```

The local container bootstrap was also repaired so the test user is created
inside the web container with its Compose database configuration.

## Proof

Container-backed HTTP integration tests cover ID and tag filtering, scoped
pagination, date composition, empty matches, invalid combinations, and
backward-compatible unfiltered requests. The complete suite passed with 61
tests.

## Remaining operational note

Integration runs leave UUID-isolated metrics in the local database because the
API has no metric deletion endpoint. Recreate the disposable test volume when
periodic cleanup is needed.
