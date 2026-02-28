╔══════════════════════════════════════════════════╗
║          ASTRA-9 — NAVIGATION USB                ║
║       Property of Outer Ring Maintenance         ║
╚══════════════════════════════════════════════════╝

This device contains navigation telemetry, crew logs, and the
station authentication console (dockauth).

CONTENTS:
  /logs/crew_log.txt   — Maintenance shift log
  /bin/dockauth        — Dock authentication binary
  /nav.bc              — Navigation bytecode (telemetry)
  /payload.enc         — Encrypted signal payload

USAGE:
  To verify station credentials, run the auth console:

    cd /path/to/this/drive
    echo "<YOUR_TOKEN>" | ./bin/dockauth

  The binary reads nav.bc, payload.enc, and seed32.bin from
  the current working directory.

  If your token is valid, you will see: "signal verified"

NOTE:
  The diagnostic cache partition may contain leftover
  telemetry data from previous maintenance cycles.
  This data is scheduled for periodic purge and should
  not be relied upon.

--- ASTRA-9 OPS DIVISION ---
