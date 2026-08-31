# TERA guard review

TERA independently specified the fail-closed Git fixture matrix. The implemented
tests cover allowed new/fast-forward `task/**`, `integration/**`, and
`release/**` pushes plus denial of main, tags, deletion, non-fast-forward,
unapproved namespaces, malformed protocol, unavailable/non-commit objects, and
mixed multi-ref pushes. Installer tests cover fresh install, idempotency,
LF/no-BOM bytes, effective `core.hooksPath`, dirty source, existing-hook
preservation, tamper detection, and Unix user-execute semantics.
preservation, tamper detection, Windows hook invocation, and a conditional
non-Windows user-execute assertion.

Result: 21 targeted tests passed. No real main or tag push was performed.
The Unix user-execute assertion is present but did not execute on this Windows
host; it remains for Hosted Linux verification.
