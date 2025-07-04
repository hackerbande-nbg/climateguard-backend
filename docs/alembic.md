# General

this file contains some info and learnings on alembic and DB migrations.
They're paid in quite a lot of time, so read them carefully.

# Upgrades

## Autodetection of column type changes sometimes fails

Sometimes, the column type change detection is failing, so always check that it's properly working
via checking the upgrade/downgrade functions

# Syntax

## Alter Column statements

alembic does not autowarn in case an alter table fails.
Therefore, missing executions due to errors might go unexplored.

## Example: to varchar

see: /home/andi/git/quantum-telemetry/project/migrations/versions/1790945e6da6_device_to_str.py