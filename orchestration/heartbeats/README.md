# Lane heartbeats

Lane scripts write one JSON heartbeat per lane atomically. Heartbeats contain only
schema version, lane ID, status, phase, current non-sensitive action, restart count,
process ID, and UTC update timestamp. They do not store branch names, checkpoint
SHAs, credentials, raw external text, or personal paths.
Five minutes is the update target; twenty minutes without an update is `STALLED`.
